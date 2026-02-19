# Playwright Test Patterns Reference

Conventions for Playwright E2E tests against the Breeze Airways app. Tests use the Page Object Model, run against the Vite dev server, and cover rendering, navigation, interaction, offline, error, and accessibility categories.

## File Structure

```
e2e/
├── playwright.config.ts
├── fixtures/
│   ├── base.ts              # Extended test fixtures
│   └── mock-data.ts         # Shared assertion data
├── page-objects/
│   ├── BasePage.ts           # Base page object
│   └── {PageName}Page.ts    # Per-page page objects
├── utils/
│   ├── navigation.ts
│   └── assertions.ts
└── specs/
    └── {feature}/
        └── {pageName}.spec.ts
```

## Page Object Pattern

### Base Page Object

```typescript
import { Page, Locator, expect } from '@playwright/test';

export class BasePage {
  readonly page: Page;
  readonly loadingIndicator: Locator;
  readonly errorMessage: Locator;
  readonly retryButton: Locator;
  readonly offlineBanner: Locator;
  readonly mainHeading: Locator;

  constructor(page: Page) {
    this.page = page;
    this.loadingIndicator = page.locator('[aria-busy="true"]');
    this.errorMessage = page.locator('[role="alert"]');
    this.retryButton = page.getByRole('button', { name: /try again|retry/i });
    this.offlineBanner = page.locator('[role="alert"]').filter({ hasText: /offline/i });
    this.mainHeading = page.locator('h1, h2').first();
  }

  async navigateTo(path: string) {
    await this.page.goto(path);
    await this.waitForPageLoad();
  }

  async waitForPageLoad() {
    // Wait for loading skeleton to disappear
    await this.loadingIndicator.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {
      // Page may not have a loading state — that's fine
    });
  }

  async expectLoading() {
    await expect(this.loadingIndicator).toBeVisible();
  }

  async expectError(message?: string) {
    await expect(this.errorMessage).toBeVisible();
    if (message) {
      await expect(this.errorMessage).toContainText(message);
    }
  }

  async expectOffline() {
    await expect(this.offlineBanner).toBeVisible();
  }

  async expectNotOffline() {
    await expect(this.offlineBanner).not.toBeVisible();
  }

  async clickRetry() {
    await this.retryButton.click();
  }

  async getPageTitle(): Promise<string> {
    return this.mainHeading.textContent() ?? '';
  }
}
```

### Per-Page Page Object

```typescript
import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class CheckInWorkflowPage extends BasePage {
  // Locators — use semantic selectors, not CSS
  readonly passengerName: Locator;
  readonly pnrBadge: Locator;
  readonly stepIndicator: Locator;
  readonly currentStep: Locator;
  readonly continueButton: Locator;
  readonly backButton: Locator;
  readonly documentTypeSelect: Locator;
  readonly scanButton: Locator;
  readonly seatGrid: Locator;
  readonly baggageIncrement: Locator;
  readonly baggageDecrement: Locator;
  readonly boardingPassCard: Locator;

  constructor(page: Page) {
    super(page);
    this.passengerName = page.locator('h1');
    this.pnrBadge = page.locator('[class*="pnrBadge"], [data-testid="pnr-badge"]');
    this.stepIndicator = page.getByRole('navigation', { name: /progress/i });
    this.currentStep = page.locator('[aria-current="step"]');
    this.continueButton = page.getByRole('button', { name: /continue|issue/i });
    this.backButton = page.getByRole('button', { name: /back/i });
    this.documentTypeSelect = page.locator('#doc-type');
    this.scanButton = page.getByRole('button', { name: /scan/i });
    this.seatGrid = page.getByRole('grid', { name: /seat/i });
    this.baggageIncrement = page.getByRole('button', { name: /increase/i }).first();
    this.baggageDecrement = page.getByRole('button', { name: /decrease/i }).first();
    this.boardingPassCard = page.locator('[class*="boardingPassCard"]');
  }

  // Actions
  async advanceToStep(stepName: string) {
    const stepButton = this.page.getByRole('button', { name: new RegExp(stepName, 'i') });
    await stepButton.click();
  }

  async selectSeat(seatLabel: string) {
    const seat = this.page.getByRole('button', { name: new RegExp(`seat ${seatLabel}`, 'i') });
    await seat.click();
  }

  async incrementBags(count: number = 1) {
    for (let i = 0; i < count; i++) {
      await this.baggageIncrement.click();
    }
  }

  async clickContinue() {
    await this.continueButton.click();
  }

  async clickBack() {
    await this.backButton.click();
  }

  // Assertions
  async expectPassengerName(name: string) {
    await expect(this.passengerName).toContainText(name);
  }

  async expectOnStep(stepName: string) {
    await expect(this.currentStep).toContainText(stepName);
  }

  async expectBoardingPass() {
    await expect(this.boardingPassCard).toBeVisible();
  }
}
```

## Test File Template

```typescript
import { test, expect } from '@playwright/test';
import { CheckInWorkflowPage } from '../../page-objects/CheckInWorkflowPage';

test.describe('CheckIn Workflow', () => {
  let checkInPage: CheckInWorkflowPage;

  test.beforeEach(async ({ page }) => {
    checkInPage = new CheckInWorkflowPage(page);
    await checkInPage.navigateTo('/check-in/BRZ4K7');
  });

  // ─── Render Tests ─────────────────────────────────────────

  test.describe('Rendering', () => {
    test('renders default state with passenger info', async () => {
      await checkInPage.expectPassengerName('Sarah Mitchell');
      await expect(checkInPage.stepIndicator).toBeVisible();
    });

    test('renders loading state with skeleton', async ({ page }) => {
      // Navigate to a route that triggers loading
      await page.goto('/check-in/LOADING');
      const loadingPage = new CheckInWorkflowPage(page);
      await loadingPage.expectLoading();
    });

    test('renders error state with retry', async ({ page }) => {
      await page.goto('/check-in/ERROR');
      const errorPage = new CheckInWorkflowPage(page);
      await errorPage.expectError('Unable to load passenger data');
    });
  });

  // ─── Navigation Tests ─────────────────────────────────────

  test.describe('Navigation', () => {
    test('navigates through all check-in steps', async () => {
      // Step 1: Document Verification
      await checkInPage.expectOnStep('ID');
      await checkInPage.clickContinue();

      // Step 2: Seat Selection
      await checkInPage.expectOnStep('Seat');
      await checkInPage.clickContinue();

      // Step 3: Baggage
      await checkInPage.expectOnStep('Bags');
      await checkInPage.clickContinue();

      // Step 4: Boarding Pass
      await checkInPage.expectOnStep('Pass');
    });

    test('back button returns to previous step', async () => {
      await checkInPage.clickContinue(); // Go to step 2
      await checkInPage.clickBack();     // Back to step 1
      await checkInPage.expectOnStep('ID');
    });
  });

  // ─── Interaction Tests ────────────────────────────────────

  test.describe('Interactions', () => {
    test('seat selection updates the UI', async () => {
      await checkInPage.clickContinue(); // Go to seat selection
      await checkInPage.selectSeat('15C');
      // Verify seat appears selected (visual feedback)
    });

    test('baggage counter increments and decrements', async () => {
      await checkInPage.clickContinue(); // Step 2
      await checkInPage.clickContinue(); // Step 3 - Baggage
      await checkInPage.incrementBags(2);
      // Verify counter shows 2
    });
  });

  // ─── Offline Tests ────────────────────────────────────────

  test.describe('Offline', () => {
    test('offline banner is visible in offline mode', async ({ page }) => {
      await page.goto('/check-in/BRZ4K7?offline=true');
      const offlinePage = new CheckInWorkflowPage(page);
      await offlinePage.expectOffline();
    });
  });

  // ─── Error Tests ──────────────────────────────────────────

  test.describe('Error Handling', () => {
    test('retry button clears error and reloads', async ({ page }) => {
      await page.goto('/check-in/ERROR');
      const errorPage = new CheckInWorkflowPage(page);
      await errorPage.clickRetry();
      // After retry, should show loading or default state
      await expect(errorPage.errorMessage).not.toBeVisible({ timeout: 5000 });
    });
  });

  // ─── Accessibility Tests ──────────────────────────────────

  test.describe('Accessibility', () => {
    test('page has a main heading', async () => {
      const heading = await checkInPage.getPageTitle();
      expect(heading).toBeTruthy();
    });

    test('step indicator has navigation role', async () => {
      await expect(checkInPage.stepIndicator).toHaveRole('navigation');
    });

    test('interactive elements are keyboard focusable', async ({ page }) => {
      // Tab through the page and verify focus reaches key elements
      await page.keyboard.press('Tab');
      const focused = page.locator(':focus');
      await expect(focused).toBeVisible();
    });

    test('no critical accessibility violations', async ({ page }) => {
      // Using @axe-core/playwright for automated a11y checks
      // const results = await new AxeBuilder({ page }).analyze();
      // expect(results.violations.filter(v => v.impact === 'critical')).toHaveLength(0);
    });
  });
});
```

## Locator Priority

Use locators in this priority order (most reliable to least):

1. **Role + name** — `page.getByRole('button', { name: 'Continue' })`
2. **Label** — `page.getByLabel('Document Type')`
3. **Text** — `page.getByText('Offline Mode')`
4. **ARIA attributes** — `page.locator('[aria-current="step"]')`
5. **data-testid** — `page.locator('[data-testid="nav-back"]')`
6. **CSS selector** — `page.locator('.boarding-pass-card')` (last resort)

Never use fragile selectors like `div > div:nth-child(3) > span`.

## Test Naming Convention

```
{verb} {what} {when/condition}
```

Examples:
- `renders default state with passenger info`
- `navigates through all check-in steps`
- `displays offline banner when offline`
- `increments baggage counter on plus click`
- `shows error message on API failure`

## State Testing via URL Parameters

The app supports URL-driven state for testing:

```
/check-in/BRZ4K7              # Default state
/check-in/BRZ4K7?offline=true # Offline mode
/check-in/BRZ4K7?step=baggage # Start at specific step
/check-in/LOADING              # Loading state (special PNR)
/check-in/ERROR                # Error state (special PNR)
/check-in/EMPTY                # Empty state (special PNR)
```

Use these URL patterns to test different states without mocking internal state.

## Assertion Helpers

Common assertion patterns to use across all test files:

```typescript
// Wait for navigation to complete
async function expectNavigatedTo(page: Page, path: string) {
  await expect(page).toHaveURL(new RegExp(path));
}

// Verify a toast/notification appeared
async function expectToast(page: Page, message: string) {
  const toast = page.locator('[role="status"], [role="alert"]').filter({ hasText: message });
  await expect(toast).toBeVisible({ timeout: 5000 });
}

// Verify a count of items in a list
async function expectListCount(locator: Locator, count: number) {
  await expect(locator).toHaveCount(count);
}

// Verify element is not in loading state
async function expectNotLoading(page: Page) {
  const loading = page.locator('[aria-busy="true"]');
  await expect(loading).not.toBeVisible();
}
```

## Viewport Testing

The playwright config defines two projects (desktop and tablet). Tests run in both viewports automatically. For viewport-specific assertions:

```typescript
test('sidebar collapses on tablet', async ({ page, viewport }) => {
  if (viewport && viewport.width < 1024) {
    await expect(page.locator('[data-testid="sidebar"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="hamburger-menu"]')).toBeVisible();
  }
});
```

## Test Organization

Group tests by category within each spec file:

1. **Rendering** — each state renders without console errors
2. **Navigation** — flow-based tests that traverse multiple screens
3. **Interactions** — click, type, select, toggle actions
4. **Offline** — offline banner, cached data display
5. **Error handling** — error states, retry behavior
6. **Accessibility** — headings, keyboard nav, ARIA, color contrast

Keep each test focused on one assertion category. Cross-cutting flows (e.g., "complete check-in end to end") go in a separate `flows/` directory.
