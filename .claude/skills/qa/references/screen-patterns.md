# Screen Patterns Reference

Conventions for building screen wrappers in the Breeze Airways app. Each screen imports an existing component from `libs/`, provides mock data, and wires navigation.

## Screen File Structure

```
app/src/screens/{PageName}Screen.tsx
```

Each screen is a thin wrapper — it should NOT re-implement the component. It only provides:
1. Mock data (reused from story factories)
2. Navigation callbacks (react-router-dom)
3. State management for interactive flows
4. URL parameter parsing

## Screen Template

```tsx
import { useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { PageName } from '@libs/feature/feature-components';
// Or direct path: import { PageName } from '../../../../libs/feature/feature-components/src/lib/PageName/PageName';

// ─── Mock Data ──────────────────────────────────────────────
// Reuse factories from the story file. Copy them here or import from shared mock module.

function createMockData(overrides = {}) {
  return {
    // ... realistic Breeze Airways data
    ...overrides,
  };
}

// ─── Screen Wrapper ─────────────────────────────────────────

export function PageNameScreen() {
  const navigate = useNavigate();
  const { paramName } = useParams();

  // Local state for interactive elements
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<{ message: string } | null>(null);

  // Mock data — in a real app, this would come from API calls
  const data = createMockData();

  // Navigation callbacks — map component callbacks to route navigation
  const handleComplete = useCallback(() => {
    navigate('/next-page');
  }, [navigate]);

  const handleRetry = useCallback(() => {
    setError(null);
    setIsLoading(true);
    // Simulate API retry
    setTimeout(() => setIsLoading(false), 1000);
  }, []);

  return (
    <PageName
      data={data}
      isLoading={isLoading}
      error={error}
      onComplete={handleComplete}
      onRetry={handleRetry}
    />
  );
}

export default PageNameScreen;
```

## Navigation Wiring

### Route Definition (in routes.tsx)

```tsx
import { lazy } from 'react';
import { RouteObject } from 'react-router-dom';

const PageNameScreen = lazy(() => import('./screens/PageNameScreen'));

export const routes: RouteObject[] = [
  {
    path: '/page-name',
    element: <PageNameScreen />,
  },
  {
    path: '/page-name/:id',  // For pages that need URL params
    element: <PageNameScreen />,
  },
];
```

### Navigation Callback Mapping

Map component callbacks to navigation actions. Common patterns:

```tsx
// Simple navigation to next page
const handleComplete = () => navigate('/next-page');

// Navigation with params
const handleSelectPassenger = (pnr: string) => navigate(`/passengers/${pnr}`);

// Navigation with state
const handleStartCheckIn = (passenger: PassengerData) =>
  navigate('/check-in', { state: { passenger } });

// Back navigation
const handleBack = () => navigate(-1);

// Conditional navigation based on flow
const handleStepComplete = (step: string) => {
  if (step === 'boarding-pass') {
    navigate('/boarding-gate');
  }
  // Otherwise stay on current page, component handles internal step changes
};
```

## Mock Data Rules

1. **Reuse story factories** — every component's story file has `createMock*()` functions with realistic Breeze Airways data. Copy these into the screen or import from a shared mock module.

2. **Use realistic aviation data** — real Breeze route cities (MCO, BDL, TPA, RDU, CHS, SAV, etc.), real flight number format (MX ###), real PNR format (6 uppercase alphanumeric).

3. **Mock data module** — if multiple screens need the same data (e.g., passenger data shared between search and detail), create a shared mock in `app/src/mock-api/data/`:

```tsx
// app/src/mock-api/data/passengers.ts
export const mockPassengers = [
  {
    firstName: 'Sarah',
    lastName: 'Mitchell',
    pnr: 'BRZ4K7',
    flightNumber: 'MX 401',
    origin: 'MCO',
    destination: 'BDL',
    scheduledDeparture: '2026-02-17T14:30:00Z',
  },
  // ... more passengers
];
```

4. **Simulate async behavior** — use `setTimeout` to simulate API latency so loading states are exercised:

```tsx
const [isLoading, setIsLoading] = useState(true);

useEffect(() => {
  const timer = setTimeout(() => setIsLoading(false), 800);
  return () => clearTimeout(timer);
}, []);
```

## Interactive State Management

For pages with multi-step flows (like CheckInWorkflow), manage step state locally:

```tsx
const [currentStep, setCurrentStep] = useState<CheckInStep>('document-verification');
const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());

const handleStepChange = (step: CheckInStep) => {
  setCurrentStep(step);
};

const handleStepComplete = (step: string) => {
  setCompletedSteps(prev => new Set([...prev, step]));
};
```

For pages with selection state (like SeatMap), maintain selection in the wrapper:

```tsx
const [selectedSeat, setSelectedSeat] = useState<SeatOption | null>(null);

const handleSeatSelect = (seat: SeatOption) => {
  setSelectedSeat(seat);
  // Optionally navigate or update passenger data
};
```

## App Shell Integration

Every screen renders inside the `AppShell` layout which provides:
- **Sidebar navigation** — links to all major pages
- **Header** — shows current page title and breadcrumbs
- **Connectivity indicator** — online/offline toggle for testing

Screens do NOT need to render navigation chrome — the layout handles it. The screen component occupies the main content area.

## Path Aliases

The app's `vite.config.ts` configures path aliases matching the monorepo:

```tsx
// These import paths should work in screen files:
import { CheckInWorkflow } from '@libs/check-in/check-in-components';
import { FlightBoard } from '@libs/flights/flights-components';
```

If alias resolution fails, fall back to relative paths:
```tsx
import { CheckInWorkflow } from '../../../../libs/check-in/check-in-components/src/lib/CheckInWorkflow/CheckInWorkflow';
```

## Data-Testid Convention

Add `data-testid` attributes to the screen wrapper's key navigation elements. These are the hooks that Playwright page objects will use:

```tsx
<div data-testid="screen-page-name">
  <PageName
    // ... props
  />
  {/* Navigation actions that the screen adds */}
  <button data-testid="nav-back" onClick={() => navigate(-1)}>
    Back
  </button>
</div>
```

Existing components already have semantic HTML (roles, aria-labels) that Playwright can target. Only add `data-testid` for screen-level navigation elements that the wrapper introduces.
