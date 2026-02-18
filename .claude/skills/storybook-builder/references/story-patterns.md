# Story Patterns Reference

Standard patterns for Storybook stories in the Breeze Airways ops-fe workspace. All stories use **CSF3 format** (Component Story Format 3) with TypeScript.

## File Naming and Location

```
libs/{feature}/{feature}-components/src/lib/{PageName}/
├── {PageName}.tsx              # Component
├── {PageName}.stories.tsx      # Stories
├── {PageName}.test.tsx         # Unit tests (optional, separate concern)
└── {PageName}.types.ts         # Props interface (if complex)
```

Story files are co-located with their component. Never place stories in a separate `stories/` directory.

## CSF3 Story File Template

```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { {PageName} } from './{PageName}';

const meta = {
  title: '{Feature}/{PageName}',
  component: {PageName},
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen', // Use 'fullscreen' for pages, 'centered' for small components
    docs: {
      description: {
        component: '{One-sentence description from manifest}',
      },
    },
  },
  argTypes: {
    // Define controls for interactive props
    // status: { control: 'select', options: ['on-time', 'delayed', 'cancelled'] },
  },
} satisfies Meta<typeof {PageName}>;

export default meta;
type Story = StoryObj<typeof meta>;

// ─── Standard States ────────────────────────────────────────

export const Default: Story = {
  args: {
    // Happy path with realistic mock data
  },
};

export const Loading: Story = {
  args: {
    isLoading: true,
  },
};

export const Empty: Story = {
  args: {
    data: [],
    // or items: [], flights: [], etc.
  },
};

export const Error: Story = {
  args: {
    error: { message: 'Failed to load flight data. Please try again.' },
  },
};

// ─── Domain-Specific States ─────────────────────────────────

// Add states unique to this page based on the PRB requirements.
// Examples for aviation ops:

// export const DelayedFlights: Story = { args: { ... } };
// export const CancelledFlight: Story = { args: { ... } };
// export const HighLoadFactor: Story = { args: { ... } };
// export const CrewShortage: Story = { args: { ... } };
```

## Standard State Definitions

Every page **must** have these four baseline states. Add domain-specific states on top.

| State | Purpose | What to Show |
|-------|---------|-------------|
| `Default` | Happy path, data loaded | Realistic mock data, typical operational scenario |
| `Loading` | Data is being fetched | Skeleton loaders or spinner, matching page layout |
| `Empty` | No data matches filters/query | Empty state illustration, helpful message, action CTA |
| `Error` | API failure or network error | Error message, retry button, fallback UI |

### Domain-Specific State Examples by Persona

**Gate Agent pages:**
- `BoardingInProgress` — active boarding with passenger queue
- `DelayedFlight` — delay banner, updated times, rebooking options
- `Overbooked` — standby list visible, volunteer solicitation UI
- `GateChange` — alert banner, updated gate info

**Dispatcher pages:**
- `IrregularOps` — multiple disruptions, priority indicators
- `WeatherHold` — weather overlay, affected flights highlighted
- `CrewSwap` — crew reassignment in progress
- `HighVolume` — many simultaneous flights, dense data view

**Crew pages:**
- `PreFlight` — checklist view, all items pending
- `InFlight` — active flight status, service flow
- `Deadhead` — minimal view, positioning flight info

## Mock Data Conventions

### Realistic Aviation Data

Use plausible Breeze Airways data in all mock stories. Never use lorem ipsum or obviously fake data.

```tsx
// Good mock data
const mockFlights = [
  {
    flightNumber: 'MX 401',
    origin: 'MCO',
    destination: 'BDL',
    scheduledDeparture: '2024-03-15T14:30:00Z',
    status: 'on-time',
    aircraft: 'E190',
    gate: 'B12',
    passengers: 108,
    capacity: 118,
  },
  {
    flightNumber: 'MX 822',
    origin: 'TPA',
    destination: 'RDU',
    scheduledDeparture: '2024-03-15T15:45:00Z',
    status: 'delayed',
    delayMinutes: 45,
    delayReason: 'Late arriving aircraft',
    aircraft: 'A220-300',
    gate: 'C4',
    passengers: 122,
    capacity: 137,
  },
];

// Bad mock data — never do this
const mockFlights = [
  { flightNumber: 'XX 123', origin: 'AAA', destination: 'BBB' },
];
```

### Breeze Route Cities

Use actual Breeze Airways destinations in mock data:

```
MCO (Orlando), TPA (Tampa), BDL (Hartford), RDU (Raleigh),
CHS (Charleston), SAV (Savannah), JAX (Jacksonville),
PBI (West Palm Beach), RSW (Fort Myers), SFB (Sanford),
MSY (New Orleans), BNA (Nashville), PIT (Pittsburgh),
LAX (Los Angeles), LAS (Las Vegas), SFO (San Francisco)
```

### Mock Data Factories

For pages with complex data, create a factory function at the top of the story file:

```tsx
function createMockFlight(overrides: Partial<Flight> = {}): Flight {
  return {
    flightNumber: 'MX 401',
    origin: 'MCO',
    destination: 'BDL',
    scheduledDeparture: '2024-03-15T14:30:00Z',
    status: 'on-time',
    aircraft: 'E190',
    gate: 'B12',
    passengers: 108,
    capacity: 118,
    ...overrides,
  };
}

// Usage in stories:
export const DelayedFlight: Story = {
  args: {
    flights: [
      createMockFlight({ status: 'delayed', delayMinutes: 45 }),
      createMockFlight({ flightNumber: 'MX 822', status: 'on-time' }),
    ],
  },
};
```

## Viewport Presets

Stories should be tested across these viewports (configured in `.storybook/preview.ts`):

| Name | Width | Use Case |
|------|-------|----------|
| `Desktop` | 1440px | Dispatcher workstations |
| `Desktop SM` | 1280px | Minimum desktop |
| `Tablet Landscape` | 1024px | Gate agent iPad landscape |
| `Tablet Portrait` | 768px | Gate agent iPad portrait |
| `Mobile` | 375px | Crew phones |

## Story Organization (title hierarchy)

```
{Feature Domain}/
├── Pages/
│   ├── {PageName}        # Full page stories
│   └── {PageName}
├── Components/
│   ├── {ComponentName}   # Shared feature components
│   └── {ComponentName}
└── Patterns/
    └── {PatternName}     # Composition patterns
```

Example title values:
- `'FlightLine/Pages/FlightBoard'`
- `'DisruptionLog/Pages/DisruptionForm'`
- `'Shared/Components/StatusBadge'`

## Decorator Pattern for Page Stories

Page-level stories should use the fullscreen layout with a simulated app shell:

```tsx
export const Default: Story = {
  decorators: [
    (Story) => (
      <div style={{ minHeight: '100vh', background: 'var(--color-bg-gray)' }}>
        <Story />
      </div>
    ),
  ],
  args: { /* ... */ },
};
```

The global Moxy decorator (fonts, CSS variables) is applied automatically via `.storybook/preview.ts` — individual stories should not re-apply it.

## Interaction Tests (Optional Enhancement)

For pages with interactive flows, add play functions:

```tsx
import { within, userEvent, expect } from '@storybook/test';

export const FilterByStatus: Story = {
  args: { flights: mockFlights },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole('button', { name: /filter/i }));
    await userEvent.click(canvas.getByText('Delayed'));
    await expect(canvas.getAllByRole('row')).toHaveLength(2); // header + 1 delayed
  },
};
```

Only add interaction tests for P0 user stories from the PRB. Do not add them for every state.
