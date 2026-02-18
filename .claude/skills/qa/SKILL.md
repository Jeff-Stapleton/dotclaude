# QA Skill — TDD via Prototype + Playwright

Scaffold the actual application as a working prototype using existing Storybook components and referenceing Storybook on how the pages should look, then generate a comprehensive Playwright E2E test suite against it. The prototype becomes the real app as features are implemented; the tests become the regression safety net.

## Argument Handling

```
/qa path/to/specs/product-requirement-brief.md
```

If the argument is missing, use `AskUserQuestion` to request the PRB path. The PRB is required input.

Before starting, verify these files exist (use `Glob`):
1. The PRB at the given path
2. A technical architecture document — search for `technical-architecture.md` in the same directory as the PRB, or in `specs/`
3. Storybook stories — search for `**/*.stories.tsx` under `libs/`

If the technical architecture document cannot be found, use `AskUserQuestion` to request its path.

## Execution Phases

Run these five phases sequentially. **Do not skip phases.**

---

### Phase 1 — Parse Inputs into Manifest

**Goal:** Read all large input documents once, distill them into a compact `qa-manifest.json`, then let the documents leave context. This manifest drives every subsequent phase.

1. Read the **technical architecture document** with the `Read` tool. Extract:
   - Framework and language (React Native, TypeScript, etc.)
   - Build tool (Vite, Metro, Expo, etc.)
   - Navigation library (React Navigation, React Router, etc.)
   - Existing test infrastructure (Jest, Detox, Playwright, etc.)
   - Key NFRs relevant to testing (performance targets, accessibility requirements)
   - The `libs/` directory structure (feature domains and component locations)

2. Read the **PRB** with the `Read` tool. For each page/feature, extract:
   - Page name (PascalCase)
   - Feature domain (maps to `libs/{feature}/`)
   - User flows (step-by-step navigation paths)
   - Acceptance criteria IDs
   - PRB line range (start-end) for subagent slicing
   - Priority (P0/P1/P2)

3. Scan **all `*.stories.tsx` files** using `Glob` and read each story file's meta/exports section (first ~30 lines + export names). For each, extract:
   - Component import path
   - Story title (e.g., `CheckIn/Pages/CheckInWorkflow`)
   - Named story exports (states: Default, Loading, Error, Offline, etc.)
   - Whether mock data factories exist

4. Build the **navigation graph** — which pages link to which, based on PRB flows:
   ```
   Login -> FlightBoard -> PassengerSearch -> PassengerDetail -> CheckInWorkflow
                                                                   |-> SeatMap
                                                                   |-> BaggageProcessing
                                                                   |-> AncillarySales
   FlightBoard -> BoardingGate
   ```

5. Write `qa-manifest.json` to the project root with this structure:

```json
{
  "techStack": {
    "framework": "react-native",
    "language": "typescript",
    "buildTool": "vite",
    "navigation": "react-router-dom",
    "prototypeTarget": "web"
  },
  "navigationGraph": {
    "Login": ["FlightBoard"],
    "FlightBoard": ["PassengerSearch", "BoardingGate"],
    "PassengerSearch": ["PassengerDetail"],
    "PassengerDetail": ["CheckInWorkflow"],
    "CheckInWorkflow": ["SeatMap", "BaggageProcessing", "AncillarySales"]
  },
  "pages": [
    {
      "name": "CheckInWorkflow",
      "feature": "check-in",
      "componentPath": "libs/check-in/check-in-components/src/lib/CheckInWorkflow/CheckInWorkflow.tsx",
      "storyPath": "libs/check-in/check-in-components/src/lib/CheckInWorkflow/CheckInWorkflow.stories.tsx",
      "storyTitle": "CheckIn/Pages/CheckInWorkflow",
      "states": ["Default", "DocumentVerification", "SeatSelection", "BaggageEntry", "BoardingPass", "Complete", "Loading", "Error", "Offline"],
      "hasMockFactories": true,
      "prbLineRange": [142, 189],
      "flows": [
        "Search passenger -> Start check-in -> Verify docs -> Select seat -> Add bags -> Issue boarding pass",
        "Offline check-in -> Sync when back online"
      ],
      "acceptanceCriteria": ["AC-TS-001-1", "AC-TS-001-2"],
      "priority": "P0",
      "navigatesTo": ["SeatMap", "BaggageProcessing"],
      "navigatesFrom": ["PassengerDetail", "PassengerSearch"]
    }
  ]
}
```

6. Print a summary table for the user:

```
QA Manifest Summary
====================================
Page                    States  Flows  Priority
------------------------------------
LoginPage               7       1      P0
FlightBoard             8       2      P0
PassengerSearch         6       1      P0
...
------------------------------------
Total: 15 pages | 118 states | 24 flows
```

**Before proceeding to Phase 2**, present the manifest summary and ask the user to confirm using `AskUserQuestion`. Include options to:
- Proceed with all pages
- Select only P0 pages
- Custom selection

---

### Phase 2 — Scaffold Prototype & Playwright Infrastructure

**Goal:** Create the application shell, mock API layer, navigation routing, and Playwright configuration. This phase stays in the main agent context — it's small config work.

#### 2a. Prototype App Shell

The prototype is a **web application** that imports existing components from `libs/` and wires them together with real navigation and mock data. It runs in a browser so Playwright can test it.

1. Read the existing project configuration (`package.json`, `tsconfig.json`, `vite.config.ts` or equivalent) to understand the build setup
2. Create the prototype app directory:
   ```
   apps/prototype/
   ├── index.html
   ├── vite.config.ts          # Vite config with path aliases matching libs/
   ├── tsconfig.json            # Extends root tsconfig
   ├── src/
   │   ├── main.tsx             # App entry point
   │   ├── App.tsx              # Router + layout shell
   │   ├── routes.tsx           # Route definitions from navigation graph
   │   ├── mock-api/
   │   │   ├── index.ts         # MSW or simple mock provider
   │   │   ├── handlers.ts      # Mock API response handlers
   │   │   └── data/            # Mock data files (reuse story factories)
   │   ├── layouts/
   │   │   └── AppShell.tsx     # Navigation chrome (sidebar, header, breadcrumbs)
   │   └── screens/             # Thin screen wrappers (populated in Phase 3)
   │       └── .gitkeep
   └── package.json             # Prototype-specific deps (react-router-dom, msw)
   ```

3. Key decisions for the prototype:
   - Use **Vite** as the dev server (it's already used by Storybook in this project)
   - Use **react-router-dom** for navigation (web-compatible, Playwright-friendly)
   - Use **MSW (Mock Service Worker)** or simple React context for mock data — whichever is simpler given the existing components
   - Configure **path aliases** so `libs/` imports work (match existing tsconfig paths)
   - The app shell should include: a navigation sidebar listing all pages, a header with the current page title, and a connectivity status indicator

4. Add scripts to root `package.json`:
   - `"prototype": "vite dev --config apps/prototype/vite.config.ts"`
   - `"prototype:build": "vite build --config apps/prototype/vite.config.ts"`

#### 2b. Playwright Configuration

1. Create the Playwright infrastructure:
   ```
   e2e/
   ├── playwright.config.ts     # Points at prototype dev server
   ├── tsconfig.json
   ├── fixtures/
   │   ├── base.ts              # Extended test fixture with page helpers
   │   └── mock-data.ts         # Shared mock data for assertions
   ├── page-objects/             # Page Object Model classes (populated in Phase 4)
   │   └── .gitkeep
   ├── utils/
   │   ├── navigation.ts        # Helper to navigate between pages
   │   └── assertions.ts        # Custom assertion helpers (e.g., checkOfflineBanner)
   └── specs/                   # Test files (populated in Phase 4)
       └── .gitkeep
   ```

2. `playwright.config.ts` must:
   - Start the prototype dev server via `webServer` config
   - Configure projects for: chromium (desktop 1440px), webkit (tablet 768px)
   - Set base URL to the prototype dev server
   - Enable screenshots on failure
   - Set reasonable timeouts (30s for navigation, 10s for assertions)

3. Create shared **page object** base class with common helpers:
   - `navigateTo(pageName)` — uses the navigation graph
   - `waitForPageLoad()` — waits for loading skeletons to disappear
   - `checkOfflineBanner(visible: boolean)` — asserts offline banner state
   - `getErrorMessage()` — extracts error message text
   - `clickRetry()` — clicks the retry button on error states

---

### Phase 3 — Build App Screens (Subagent Delegation)

**Goal:** For each page in the manifest, create a thin screen wrapper that imports the existing component, provides mock data, and wires navigation. Each screen is built by a subagent to protect the main context.

Read `qa-manifest.json`. For each page entry, launch a **Task subagent** (`subagent_type: "general-purpose"`) with this prompt template:

```
You are building a prototype screen for a Breeze Airways operations app.

READ THESE FILES FIRST:
1. {path to prototype-patterns.md reference file} — Screen wrapper conventions
2. {componentPath from manifest} — The existing component to wrap
3. {storyPath from manifest} — Mock data factories to reuse
4. {path to PRB} lines {prbLineRange[0]}-{prbLineRange[1]} — Requirements context

BUILD a screen wrapper at: apps/prototype/src/screens/{PageName}Screen.tsx

The screen wrapper MUST:
1. Import the {PageName} component from its library path
2. Reuse mock data factories from the story file (copy them into the screen or import from a shared mock data module)
3. Wire up navigation using react-router-dom:
   - This page navigates TO: {navigatesTo from manifest}
   - This page is reached FROM: {navigatesFrom from manifest}
   - Use useNavigate() for programmatic navigation
   - Map component callbacks (onComplete, onSeatSelect, etc.) to navigate to the appropriate next screen
4. Manage local state for interactive elements (step progression, form state, selections)
5. Support URL params where appropriate (e.g., /passengers/:pnr, /flights/:flightNumber)

Also UPDATE the routes file at apps/prototype/src/routes.tsx to add the route for this screen.

Page details:
- Name: {name}
- Feature: {feature}
- States: {states}
- Flows: {flows}
- Navigation: FROM {navigatesFrom} -> {name} -> TO {navigatesTo}

Return ONLY this line: DONE: {name}Screen — navigates to {navigatesTo count} pages, {states count} states wired
```

**Parallelism rules:**
- Launch up to 3 subagents concurrently using `run_in_background: true`
- Wait for all background agents to complete before launching the next batch
- After each batch, verify output files exist with `ls` — do NOT read the generated files

**If a subagent fails:** Read its output, diagnose the issue, and retry once with a corrected prompt. If it fails again, log the page name and move on — report failures in Phase 5.

**Batch order:** Process pages in navigation-graph order (upstream pages first), so later subagents can see the route structure:

- **Batch S1:** LoginPage, FlightBoard, ConnectivityStatus
- **Batch S2:** PassengerSearch, BoardingGate, FlightStatus
- **Batch S3:** PassengerDetail, BaggageProcessing, AncillarySales
- **Batch S4:** CheckInWorkflow, SeatMap, DocumentScanner
- **Batch S5:** OnboardingWalkthrough, ContextualHelp, ConflictResolution

Adjust batches based on the actual manifest — the above is an example. Group by navigation tier (pages reachable in 1 hop, 2 hops, etc.).

---

### Phase 4 — Generate Playwright Tests (Subagent Delegation)

**Goal:** For each page, generate a Playwright test file with a companion page object. Each test file is built by a subagent.

Read `qa-manifest.json`. For each page entry, launch a **Task subagent** (`subagent_type: "general-purpose"`) with this prompt template:

```
You are writing Playwright E2E tests for a Breeze Airways operations app.

READ THESE FILES FIRST:
1. {path to test-patterns.md reference file} — Test conventions and patterns
2. apps/prototype/src/screens/{PageName}Screen.tsx — The screen to test
3. e2e/fixtures/base.ts — Base test fixtures and helpers

BUILD two files:

1. Page Object: e2e/page-objects/{PageName}Page.ts
   - Extends the base page object
   - Locators for all interactive elements on this page
   - Action methods for common interactions (fill forms, click buttons, select items)
   - Assertion methods for verifying state (isLoading, hasError, isOffline, etc.)

2. Test Spec: e2e/specs/{feature}/{pageName}.spec.ts
   - Use the page object for all interactions
   - Test categories:
     a. RENDER TESTS — Each state from the manifest renders without errors:
        {states from manifest}
     b. NAVIGATION TESTS — Verify flows work end-to-end:
        {flows from manifest}
     c. INTERACTION TESTS — Interactive elements respond correctly:
        - Buttons trigger expected actions
        - Forms accept input and validate
        - Selections update the UI
        - Step progressions work (e.g., check-in workflow steps)
     d. OFFLINE TESTS — Offline banner appears, offline states display correctly
     e. ERROR TESTS — Error states show messages, retry buttons work
     f. ACCESSIBILITY TESTS — Basic a11y checks:
        - Page has a main heading
        - Interactive elements are keyboard-focusable
        - ARIA labels are present on non-text elements
        - Color contrast meets WCAG 2.1 AA (use @axe-core/playwright)

Page details:
- Name: {name}
- Feature: {feature}
- States: {states}
- Flows: {flows}
- Acceptance Criteria: {acceptanceCriteria}

Return ONLY this line: DONE: {name} — {N} tests across {M} categories
```

**Parallelism rules:** Same as Phase 3 — up to 3 subagents concurrently, sequential batches.

**Batch order:** Same navigation-graph order as Phase 3.

---

### Phase 5 — Validate and Report

**Goal:** Verify the prototype builds, Playwright tests are syntactically valid, and produce a coverage report.

1. **Build check:** Run `npx vite build --config apps/prototype/vite.config.ts` (or equivalent) to check for compilation errors in the prototype
2. **Type check:** Run `npx tsc --noEmit -p e2e/tsconfig.json` to validate test files compile
3. **List tests:** Run `npx playwright test --list` to enumerate all discovered tests
4. **Attempt a test run:** Run `npx playwright test --reporter=list` — if the prototype server starts successfully, report pass/fail counts. If it fails to start, report the build error.
5. **Coverage report:**

```
QA Build Report
====================================
Prototype
------------------------------------
Page                    Screen    Route    Mock Data
------------------------------------
LoginPage               OK        /login   OK
CheckInWorkflow         OK        /check-in/:pnr  OK
FlightBoard             MISSING   --       --
------------------------------------
Screens: 14/15 | Routes: 14/15

Playwright Tests
------------------------------------
Page                    Tests  Render  Nav   Interact  Offline  Error  A11y
------------------------------------
LoginPage               12     3       2     4         1        1      1
CheckInWorkflow         24     9       3     6         2        2      2
------------------------------------
Total: 15 pages | 186 tests | 0 compile errors

Test Run: 186 passed | 0 failed | 0 skipped
```

6. If any pages are missing, list them and explain what went wrong
7. Inform the user:
   - `npm run prototype` to launch the interactive prototype
   - `npx playwright test` to run the full test suite
   - `npx playwright test --ui` to use Playwright's interactive test runner
   - `npx playwright show-report` to view the HTML test report

---

## Context Window Strategy

This skill protects the context window through these mechanisms:

1. **Phase 1** reads all large documents (architecture, PRB, story files) once, distills them into `qa-manifest.json` (~200 lines), then the documents leave context. No subsequent phase reads these full documents.

2. **Phase 2** generates small configuration files — stays in the main context. Total output is ~500 lines of config.

3. **Phase 3** delegates each screen to a subagent with a fresh context. Each subagent reads:
   - One reference file (~150 lines)
   - One component file (~2000 lines)
   - One story file (~300 lines)
   - A PRB slice (~50 lines)
   Total per subagent: ~2500 lines. Well within limits.

4. **Phase 4** delegates each test file to a subagent. Each subagent reads:
   - One reference file (~200 lines)
   - One screen wrapper (~100 lines)
   - One base fixture file (~100 lines)
   Total per subagent: ~400 lines. Very lean.

5. **Phase 5** runs CLI commands and prints a summary. Minimal context usage.

The main context never holds more than: the manifest JSON + one batch of subagent one-line status returns.

**Subagent budget rules:**
- Spec generators (Phase 3): `max_turns: 8`
- Test generators (Phase 4): `max_turns: 6`
- Maximum concurrent subagents: 3 (use `run_in_background: true`)
- Agents return only one-line status. All detailed output goes to files.
- Verify output by checking file existence (`ls`), never by reading content.

---

## Dependencies

This skill depends on:
- **breeze-design skill** — Moxy Design System tokens, read by subagents for consistent styling in the app shell
- **A product requirement brief** — the input document defining pages, flows, and acceptance criteria
- **A technical architecture document** — tech stack and infrastructure decisions
- **Existing Storybook stories** — components and mock data that the prototype reuses

## Reference Files

- `references/test-patterns.md` — Playwright test conventions, page object patterns, assertion helpers
- `references/prototype-patterns.md` — Screen wrapper conventions, mock data wiring, navigation patterns
