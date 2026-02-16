---
name: microfrontend-nx
description: NX monorepo microfrontend patterns for the Breeze Airways ops-fe workspace. Enforces Module Federation architecture, feature-scoped library structure, shared platform conventions, and routing rules. Use when writing or modifying React/TypeScript code in the operations frontend.
---

# Microfrontend NX Skill — Operations Frontend

Patterns and conventions for the Breeze Airways `ops-fe` NX monorepo. This workspace implements a Module Federation microfrontend architecture with a single host app (`ns2`) orchestrating feature domains via React 19, Rspack, and TypeScript.

## Architecture Overview

A host application loads feature domains as local routes and remote MFE applications at runtime via Module Federation.

```
Browser (SPA)
├── ns2 (HOST) :4200 — BrowserRouter
│   ├── /access-mgmt, /disruption, /crew-notifications, ... (local features)
│   └── /flight-story/* → React.lazy(() => import('flight_story/Module'))
│                           ↓ Module Federation runtime loading
├── flight_story (REMOTE) :4201 — HashRouter, exposes ./Module
└── turn (STANDALONE) :4200 — No Module Federation
```

**Key rules:**
- Host uses `BrowserRouter`, remotes use `HashRouter` (prevents route collisions)
- Host owns the URL pathname (`/flight-story`), remote owns the hash fragment (`/#/details/123`)
- Shared singletons (React, Apollo, MSAL) resolve from the host — not duplicated
- All apps are client-rendered SPAs (no SSR), all React 19

## Directory Structure

```
ops-fe/
├── apps/
│   ├── ns2/                          # HOST application
│   │   ├── module-federation.config.ts
│   │   ├── rspack.config.ts
│   │   ├── rspack.config.prod.ts
│   │   ├── project.json
│   │   └── src/
│   │       ├── bootstrap.tsx         # MSAL init + app mount
│   │       ├── main.ts              # Entry point (import bootstrap)
│   │       └── app/
│   │           └── app.tsx           # Routes + lazy remote import
│   │
│   ├── flight_story/                 # REMOTE application
│   │   ├── module-federation.config.ts
│   │   ├── rspack.config.ts
│   │   ├── rspack.config.prod.ts
│   │   ├── project.json
│   │   └── src/
│   │       ├── bootstrap.tsx
│   │       ├── main.ts
│   │       ├── remote-entry.ts       # MFE entry (re-exports app)
│   │       └── app/
│   │           └── app.tsx           # HashRouter + routes
│   │
│   └── turn/                         # STANDALONE application
│
├── libs/
│   ├── shared/                       # Platform-level shared code
│   │   ├── shared-ui/                # Reusable UI components
│   │   ├── shared-hooks/             # React hooks
│   │   ├── shared-models/            # Types and interfaces
│   │   ├── shared-services/          # Business logic helpers
│   │   ├── shared-utils/             # Utility functions, clientFactory
│   │   ├── shared-configs/           # MSAL, Sentry, NewRelic, MFE config
│   │   ├── shared-contexts/          # React Contexts
│   │   ├── shared-graphql/           # GraphQL queries/mutations
│   │   └── shared-assets/            # Icons, SVGs (via SVGR)
│   │
│   ├── {feature}/                    # Feature-scoped libraries
│   │   ├── {feature}-components/     # UI components for this domain
│   │   └── {feature}-hooks/          # Data hooks for this domain
│   │
│   └── ns2/                          # Host app-specific libs
│       ├── ns2-components/
│       └── ns2-hooks/
│
├── environments/
│   ├── environment.ts                # Dev/staging config
│   └── environment.cicd.ts           # CI/CD config
│
├── nx.json
├── tsconfig.base.json
├── package.json
└── tailwind.config.js
```

## Feature Domains

18 feature domains, each with its own `libs/{feature}/` directory:

| Domain | Library Path |
|--------|-------------|
| access-management | `libs/access-management/` |
| bag-bungler | `libs/bag-bungler/` |
| bag-tag-scanner | `libs/bag-tag-scanner/` |
| crew-notifications | `libs/crew-notifications/` |
| disruption-log | `libs/disruption-log/` |
| employee-travel | `libs/employee-travel/` |
| far-monitor | `libs/far-monitor/` |
| flight-line | `libs/flight-line/` |
| flight-story | `libs/flight-story/` |
| fuel-slip | `libs/fuel-slip/` |
| guest-notifications | `libs/guest-notifications/` |
| load-sheet | `libs/load-sheet/` |
| notifications | `libs/notifications/` |
| ns2 | `libs/ns2/` |
| ssim | `libs/ssim/` |
| ssr-portal | `libs/ssr-portal/` |
| turn | `libs/turn/` |

## Core Patterns

### 1. TypeScript Path Aliases

All imports use `@ops-fe/` scoped aliases defined in `tsconfig.base.json`:

```typescript
// Shared platform libraries
import { SomeComponent } from '@ops-fe/shared-ui';
import { useAuth } from '@ops-fe/shared-hooks';
import { FlightModel } from '@ops-fe/shared-models';
import { clientFactory } from '@ops-fe/shared-utils';
import { msalConfig } from '@ops-fe/shared-configs';
import { AppContext } from '@ops-fe/shared-contexts';
import { GET_FLIGHTS } from '@ops-fe/shared-graphql';

// Feature-scoped libraries
import { FlightCard } from '@ops-fe/{feature}-components';
import { useFlightData } from '@ops-fe/{feature}-hooks';

// Assets (wildcard path)
import SomeIcon from '@ops-fe/shared-assets/icons/SomeIcon.svg';
```

**Rules:**
- Never use relative paths across library boundaries — always use `@ops-fe/` aliases
- Each library exports through a single `src/index.ts` barrel file
- Feature libs only import from `shared/` libs, never from other feature libs

### 2. Module Federation Configuration

**Host** (`apps/ns2/module-federation.config.ts`):

```typescript
import { ModuleFederationConfig } from '@nx/module-federation';
import { MFE_PACKAGE_CONFIG } from '@ops-fe/shared-configs';

const config: ModuleFederationConfig = {
  name: 'ns2',
  remotes: ['flight_story'],
  shared: (name, config) => {
    if (MFE_PACKAGE_CONFIG.includes(name)) return false;
    return config;
  },
};
export default config;
```

**Remote** (`apps/flight_story/module-federation.config.ts`):

```typescript
const config: ModuleFederationConfig = {
  name: 'flight_story',
  exposes: {
    './Module': './src/remote-entry.ts',
  },
  shared: (name, config) => {
    if (MFE_PACKAGE_CONFIG.includes(name)) return false;
    return config;
  },
};
export default config;
```

**Singleton exclusions** (`libs/shared/shared-configs/src/lib/mfe-package-config.ts`):

```typescript
export const MFE_PACKAGE_CONFIG: string[] = [
  '@apollo/client/link/retry',
  '@apollo/client/link/context',
  '@radix-ui/react-slot',
  'react-phone-number-input/input',
  'react-phone-number-input/locale/en',
];
```

These packages are excluded from Module Federation's singleton sharing to avoid version conflicts.

### 3. Application Bootstrap Pattern

Every app follows: `main.ts` → async `bootstrap.tsx` → `<App />`

```typescript
// main.ts — entry point (async boundary for Module Federation)
import('./bootstrap');

// bootstrap.tsx — initialize auth, mount app
import { PublicClientApplication } from '@azure/msal-browser';
import { MsalProvider } from '@azure/msal-react';

const msalInstance = new PublicClientApplication(msalConfig);
// ... MSAL init
root.render(
  <MsalProvider instance={msalInstance}>
    <App />
  </MsalProvider>
);
```

The async boundary in `main.ts` is **required** — it allows Module Federation to negotiate shared dependencies before app code executes.

### 4. Remote Loading Pattern

Remotes are loaded in the host via `React.lazy` + `Suspense`:

```typescript
// apps/ns2/src/app/app.tsx
const FlightStory = React.lazy(() => import('flight_story/Module'));

// In routes:
<React.Suspense fallback={<LoadingSpinner />}>
  <FlightStory />
</React.Suspense>
```

Always wrap remote components with an error boundary to prevent host crash on remote load failure.

### 5. Router Isolation

```
HOST (ns2) — BrowserRouter          REMOTE (flight_story) — HashRouter
  /flight-story/*  ────────────▶      /#/
  /access-management/*                /#/:id
  /disruption-log/*                   /#/simulator/flights
  /crew-notifications/*               /#/simulator/load-sheet
  ...
```

**Rules:**
- Host always uses `BrowserRouter`
- Remote MFEs always use `HashRouter`
- Never mix router types within a single app

### 6. Feature-Scoped Library Pattern

Each feature domain isolates its code in `libs/{feature}/`:

```
libs/disruption-log/
├── disruption-log-components/
│   └── src/
│       ├── index.ts              # Barrel export
│       └── lib/
│           ├── DisruptionForm.tsx
│           └── DisruptionTable.tsx
└── disruption-log-hooks/
    └── src/
        ├── index.ts              # Barrel export
        └── lib/
            ├── useDisruptionLog.ts
            └── useDisruptionFilters.ts
```

**Rules:**
- `-components` libs contain React UI components
- `-hooks` libs contain data-fetching hooks (Apollo queries, state logic)
- Feature libs may import from `shared/` but never from other feature libs
- Cross-feature logic belongs in a `shared/` library

## Shared Dependency Resolution

These packages are shared as singletons across host and remotes via Module Federation:

| Package | Role |
|---------|------|
| `react` / `react-dom` | UI framework (single instance required) |
| `react-router` | Routing |
| `@apollo/client` | GraphQL client |
| `@azure/msal-react` | Authentication |

The `MFE_PACKAGE_CONFIG` list excludes specific sub-packages from sharing (loaded independently per MFE).

## Authentication Flow

1. `bootstrap.tsx` initializes MSAL `PublicClientApplication`
2. Azure AD login returns JWT with `name` and `employee_number`
3. Token feeds into `MsalProvider` (auth state), Apollo (Bearer header), and GrowthBook (user attributes)
4. Host and remotes share the MSAL instance through Module Federation singletons
5. Unauthenticated users see `UnauthenticatedTemplate` (login page)

## Rspack Configuration

Each app has two Rspack configs:

**Development** (`rspack.config.ts`):

```typescript
const { NxAppRspackPlugin } = require('@nx/rspack/app-plugin');
const { NxReactRspackPlugin } = require('@nx/rspack/react-plugin');
const { NxModuleFederationPlugin } = require('@nx/module-federation/rspack');
const { NxModuleFederationDevServerPlugin } = require('@nx/module-federation/rspack');

module.exports = {
  output: { uniqueName: 'ns2', publicPath: 'auto' },
  devServer: { port: 4200, historyApiFallback: true },
  plugins: [
    new NxAppRspackPlugin({ /* assets, styles, scripts */ }),
    new NxReactRspackPlugin({ svgr: true }),
    new NxModuleFederationPlugin({ config: mfConfig }),
    new NxModuleFederationDevServerPlugin({ config: mfConfig }),
  ],
};
```

**Production** (`rspack.config.prod.ts`) extends dev config with `xxhash64` hashing.

**Rules:**
- Always use Rspack (not Webpack) — `@nx/rspack` plugins
- SVGR is enabled (`svgr: true`) for importing SVGs as React components
- `publicPath: 'auto'` is required for Module Federation
- `historyApiFallback: true` is required for SPA routing

## Environment Configuration

```typescript
// environments/environment.ts
export const environment = {
  production: false,
  azureAd: { clientId: '...', apiScope: '...' },
  urls: { ns2: '...', disruptionLog: '...', operationsBackend: '...' },
  growthBook: { clientKey: '...' },
  firebase: { projectId: '...', vapidKey: '...' },
  scandit: { licenseKey: '...' },
  newRelic: { licenseKey: '...', accountId: '...' },
};
```

**Rules:**
- No secrets in client bundles
- Use `environment.ts` for dev/staging, `environment.cicd.ts` for CI/CD
- All API URLs come from environment config, never hardcoded

## NX Commands Reference

```bash
# Serve host with all remotes
npx nx serve ns2

# Serve individual remote
npx nx serve flight_story

# Serve host with specific remote in dev mode
NX_MF_DEV_REMOTES=flight_story npx nx serve ns2

# Build for production
npx nx run-many -t build --configuration=cicd --verbose

# Run all tests
npx nx run-many -t test

# Run tests for a specific library
npx nx test shared-ui

# Run affected tests only
npx nx affected -t test

# Generate a new library
npx nx g @nx/react:lib my-feature-components --directory=libs/my-feature

# Generate a new remote MFE app
npx nx g @nx/react:remote my-remote --host=ns2

# Visualize dependency graph
npx nx graph
```

## Testing

- **Unit Tests:** Jest + `@testing-library/react`. Each library has its own test config via NX project inference.
- **Component Dev:** Storybook (uses Vite builder, separate from Rspack).
- **Linting:** ESLint (flat config) + Prettier.
- **CI:** `npx nx run-many -t test` runs all affected tests. NX caching skips unchanged projects.

## Observability

| Tool | Purpose |
|------|---------|
| Sentry (`@sentry/react`) | Error tracking and source maps |
| New Relic (`@newrelic/browser-agent`) | Performance monitoring and RUM |
| Firebase | Push notification delivery tracking |

## Error Handling

| Scenario | Recovery |
|----------|----------|
| Remote fails to load | Suspense fallback UI; user can retry navigation |
| Auth token expired | MSAL auto-refreshes; redirect to login on failure |
| GraphQL error | Apollo error policies per query; toast notifications |
| Feature flag unavailable | GrowthBook defaults to `false` (feature hidden) |

## Technology Stack

| Category | Technology |
|----------|-----------|
| Framework | React 19 |
| Language | TypeScript |
| Bundler | Rspack (via `@nx/rspack`) |
| MFE Runtime | Module Federation (Enhanced) |
| Monorepo | NX |
| Routing | React Router 7 |
| GraphQL | Apollo Client |
| Auth | Azure MSAL |
| Feature Flags | GrowthBook |
| CSS | Tailwind CSS |
| UI Components | MUI |
| Testing | Jest + Testing Library |
| Component Dev | Storybook |
| CI/CD | GitLab CI |

## Adding a New Feature Checklist

When adding a new feature domain:

1. **Generate libraries** — `npx nx g @nx/react:lib {feature}-components --directory=libs/{feature}` and `{feature}-hooks`
2. **Add path aliases** — Update `tsconfig.base.json` with `@ops-fe/{feature}-components` and `@ops-fe/{feature}-hooks`
3. **Create components** — Add UI components in `{feature}-components/src/lib/`
4. **Create hooks** — Add data-fetching hooks in `{feature}-hooks/src/lib/`
5. **Export via barrel** — Update each library's `src/index.ts`
6. **Add route** — Add route in `apps/ns2/src/app/app.tsx` (or remote app if applicable)
7. **Add shared types** — If types are cross-feature, add to `shared-models`
8. **Add GraphQL operations** — If new queries/mutations, add to `shared-graphql` or feature hooks
9. **Test** — Unit tests per library, `npx nx test {feature}-components`

## Promoting a Feature to Remote MFE

When a feature domain needs independent deployment:

1. **Generate remote app** — `npx nx g @nx/react:remote {feature} --host=ns2`
2. **Add Module Federation config** — Create `module-federation.config.ts` with `exposes: { './Module': './src/remote-entry.ts' }`
3. **Use HashRouter** — Remote app must use `HashRouter`, not `BrowserRouter`
4. **Create remote-entry.ts** — Re-export the app component
5. **Update host config** — Add remote name to `remotes` array in host's `module-federation.config.ts`
6. **Add lazy import in host** — `React.lazy(() => import('{feature}/Module'))` wrapped in `Suspense` + error boundary
7. **Add type declaration** — Add `"{feature}/Module"` path alias in `tsconfig.base.json`
