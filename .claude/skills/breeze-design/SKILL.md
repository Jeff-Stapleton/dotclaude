---
name: breeze-design
description: "Create production-grade frontend interfaces for Breeze Airways using the Moxy Design System 2.0. Enforces brand colors, typography (Poppins/Open Sans), token system, and operational aviation UI patterns. Use when building web components, pages, or applications for Breeze Airways operations."
---

# Breeze Airways Frontend Design Skill

This skill guides creation of production-grade frontend interfaces for Breeze Airways operations applications, grounded in the **Moxy Design System 2.0**. Every interface must feel unmistakably Breeze — warm, confident, and effortlessly clear — while meeting the demands of high-stakes aviation operations.

**Moxy Design System Reference:** [Figma — Moxy Design System 2.0](https://www.figma.com/design/djnYbcDghiSsZoXR51Ck2b/Moxy-Design-System-2.0)

## Design Philosophy

Breeze Airways operations tools serve airport agents, crew, and dispatchers who work under time pressure in noisy, bright, and unpredictable environments. Every design decision must serve **clarity under stress**.

Before coding, commit to a direction by answering:

- **Who uses this?** Airport gate agents on tablets? Dispatchers on desktops? Crew on phones? Each demands different density and touch targets.
- **What's the operational tempo?** Real-time flight ops need glanceable dashboards. Back-office tools can afford more density.
- **What's the failure mode?** Missed information in aviation operations has real consequences. Critical states (delays, cancellations, weight limits) must be impossible to overlook.
- **What's the Breeze tone?** Even operational tools should feel warm and approachable — never cold or clinical. Breeze's brand personality is friendly, modern, and optimistic.

Then implement working code (React/TypeScript preferred per ops-fe conventions, or HTML/CSS/JS) that is:
- Anchored to the Moxy Design System tokens
- Operationally clear — status, priority, and action are immediately apparent
- Warm without sacrificing information density
- Accessible (WCAG 2.1 AA minimum, high contrast for outdoor/bright environments)

## Moxy Color System

### Primary Brand Colors — Sky Blue

The dominant palette. Sky Blue is the backbone of every Breeze interface.

| Token | Hex | Usage |
|-------|-----|-------|
| `skyBlue-50` | `#F8F9FF` | Lightest tint, subtle backgrounds |
| `skyBlue-100` | `#E0C4FF` | Light backgrounds, hover states |
| `skyBlue-200` | `#C1DDFF` | Secondary backgrounds, disabled fills |
| `skyBlue-300` | `#95C5FF` | Borders, dividers on dark |
| `skyBlue-400` | `#6AA2FF` | Interactive secondary elements |
| `skyBlue-500` | `#3F96FF` | Mid-range accent |
| `skyBlue-600` | `#1F74DF` | **Primary brand action color** |
| `skyBlue-700` | `#0C4D9D` | Hyperlinks on light backgrounds |
| `skyBlue-800` | `#02397B` | Contrast-dark, primary on dark |
| `skyBlue-900` | `#022659` | Deep blue accents |
| `skyBlue-950` | `#001633` | **Darkest blue — primary dark, nav backgrounds** |

### Secondary — Sunset Pink

Accent color for highlights, alerts, and differentiation.

| Token | Hex | Usage |
|-------|-----|-------|
| `sunsetPink-50` | `#FFF1F3` | Light pink tint |
| `sunsetPink-100` | `#FFE3E8` | Pink hover backgrounds |
| `sunsetPink-200` | `#FFCCD7` | Pink borders |
| `sunsetPink-300` | `#FFA1B6` | Soft pink accents |
| `sunsetPink-400` | `#FF527B` | **highlight-secondary — key accent** |
| `sunsetPink-500` | `#FF3A6D` | Active/pressed pink |
| `sunsetPink-600` | `#E7175B` | Bold pink actions |
| `sunsetPink-700` | `#C30D4A` | Dark pink |
| `sunsetPink-800` | `#A30E45` | Deeper pink |
| `sunsetPink-900` | `#8B1041` | Very dark pink |
| `sunsetPink-950` | `#4E031F` | Darkest pink |

### Secondary — Sunrise Tan

Warm accent for tertiary highlights and category differentiation.

| Token | Hex | Usage |
|-------|-----|-------|
| `sunriseTan-50` | `#FFFAF0` | Lightest warm background |
| `sunriseTan-100` | `#FFEFD0` | Warm highlight background |
| `sunriseTan-200` | `#FFD8A5` | Warm borders |
| `sunriseTan-300` | `#FFC07B` | Warm accents |
| `sunriseTan-400` | `#FFD4AA` | **highlight-tertiary** |
| `sunriseTan-500` | `#FF9F43` | Active warm |
| `sunriseTan-600` | `#E77E22` | Bold warm |
| `sunriseTan-700` | `#C05E10` | Dark warm |
| `sunriseTan-800` | `#A04910` | Deeper warm |
| `sunriseTan-900` | `#843B10` | Very dark warm |
| `sunriseTan-950` | `#4A1C04` | Darkest warm |

### Loyalty Program — Breezy Club

Used exclusively for loyalty level indicators and rewards UI.

| Token | Hex | Usage |
|-------|-----|-------|
| `breezyClub-50` | `#FEF8EE` | Lightest club tint |
| `breezyClub-100` | `#FDEFD7` | Light gold background |
| `breezyClub-200` | `#F9DAAF` | Gold borders |
| `breezyClub-300` | `#F6C07B` | Gold accent |
| `breezyClub-400` | `#F19D4A` | **breezyClub-primary** |
| `breezyClub-500` | `#ED7E22` | Active gold |
| `breezyClub-600` | `#DE6518` | Bold gold |
| `breezyClub-700` | `#B84D16` | Dark gold |
| `breezyClub-800` | `#933E19` | Deeper gold |
| `breezyClub-900` | `#763418` | Very dark gold |
| `breezyClub-950` | `#40190A` | Darkest gold |

### Loyalty Level Teal

| Token | Hex |
|-------|-----|
| `teal-50` | `#F0FDFA` |
| `teal-100` | `#CCFBF1` |
| `teal-200` | `#99F6E4` |
| `teal-300` | `#5EEAD4` |
| `teal-400` | `#2DD4BF` |
| `teal-500` | `#14B8A6` |
| `teal-600` | `#0D9488` |
| `teal-700` | `#0F766E` |
| `teal-800` | `#115E59` |
| `teal-900` | `#134E4A` |
| `teal-950` | `#042F2E` |

### Semantic Tokens

Use these semantic tokens — never raw hex values — in application code:

**Primary:**
| Token | Maps To | Hex |
|-------|---------|-----|
| `primary-light` | skyBlue-200 | `#C1DDFF` |
| `primary` | skyBlue-600 | `#1F74DF` |
| `primary-contrast-dark` | skyBlue-800 | `#02397B` |
| `primary-dark` | skyBlue-950 | `#001633` |

**Additional:**
| Token | Maps To | Hex |
|-------|---------|-----|
| `highlight-secondary` | sunsetPink-400 | `#FF527B` |
| `highlight-tertiary` | sunriseTan-400 | `#FFD4AA` |
| `white` | — | `#FFFFFF` |

**Status:**
| Token | Maps To | Hex | Usage |
|-------|---------|-----|-------|
| `success-light` | green-50 | — | Success background |
| `success` | green-600 | — | Success indicator |
| `success-dark` | green-800 | — | Success text on light |
| `danger-light` | red-50 | — | Danger background |
| `danger` | red-600 | — | Danger indicator |
| `danger-dark` | red-800 | — | Danger text on light |
| `notification-light` | amber-50 | — | Warning background |
| `notification` | amber-400 | — | Warning indicator |
| `notification-dark` | amber-700 | — | Warning text on light |

**Text:**
| Token | Maps To | Hex |
|-------|---------|-----|
| `text-light` | gray-500 | — |
| `text-medium` | gray-700 | — |
| `text-dark` | gray-950 | `#030712` |
| `hyperlink-on-light` | skyBlue-700 | `#0C4D9D` |
| `hyperlink-on-dark` | skyBlue-200 | `#C1DDFF` |

**Backgrounds:**
| Token | Maps To | Hex |
|-------|---------|-----|
| `background-light` | skyBlue-100 | — |
| `background-primary` | primarySkyBlue | — |
| `background-dark` | skyBlue-950 | `#001633` |
| `background-gray` | gray-50 | — |
| `background-disabled` | gray-100 | — |
| `background-overlay` | skyBlue-950 (70%) | — |

**Loyalty Levels:**
| Token | Color | Hex |
|-------|-------|-----|
| Breezy Rewards Member | primary-contrast-dark | `#02397B` |
| Breezy 1 | primary | `#1F74DF` |
| Breezy 2 | breezy2-teal | `#10B0A2` |
| Breezy 3 | highlight-secondary | `#FF527B` |
| Breezy Club Member | breezyClub-primary | `#F19D4A` |

## Moxy Typography System

### Poppins — Headings & Display

All Poppins sizes use `font-weight: 700` (Bold) by default. Poppins is the brand typeface — use it for all headings, display text, buttons, and eyebrow labels.

**Import:** `@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap');`

| Token | Size | Line Height | Letter Spacing | Usage |
|-------|------|-------------|----------------|-------|
| `text-xs` | 12px | 100% | 0% | Smallest Poppins text |
| `text-sm` | 14px | 120% | 0% | Small labels |
| `H6` / `text-base` | 16px | 140% | 0% | Subsection headings |
| `text-lg` | 18px | 100% | 0% | Emphasized text |
| `H5` | 20px | 100% | 0% | Section headings |
| `H4` | 24px | 100% | 0% | Card headings |
| `H3` | 30px | — | 0% | Page sub-headings |
| `H2` | 36px | — | 0% | Page headings |
| `H1` | 40px | — | 0% | Primary page title |
| `text-4xl` | 42px | 100% | 0% | Large display |
| `text-5xl` | 48px | 100% | 0% | Hero text |
| `text-6xl` | 60px | 100% | 0% | Feature headlines |
| `text-7xl` | 72px | 100% | 0% | Splash screens |
| `text-8xl` | 96px | 100% | 0% | Large numerics |
| `text-9xl` | 128px | 100% | 0% | Maximum display |

**Eyebrow styles** (uppercase micro-labels):
| Token | Size | Line Height | Letter Spacing | Weight |
|-------|------|-------------|----------------|--------|
| `EB2` | 7px | 16px | 10% | Semi-bold |
| `EB1` | 14px | — | 10% | Semi-bold |

**Button styles:**
| Token | Size | Line Height | Letter Spacing | Weight |
|-------|------|-------------|----------------|--------|
| `BT3` | 12px | 16px | 2% | Semi-bold (600) |
| `BT2` | 14px | 20px | 2% | Semi-bold (600) |
| `BT1` | 16px | 24px | 2% | Semi-bold (600) |

### Open Sans — Body & Data

All Open Sans sizes support four weights: Bold (700), Semibold (600), Normal (400), Light (300). Use Open Sans for all body text, data tables, form inputs, and long-form content.

**Import:** `@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap');`

| Token | Size | Line Height | Letter Spacing | Usage |
|-------|------|-------------|----------------|-------|
| `P4` / `text-xs` | 12px | 16px | 0% | Fine print, timestamps |
| `P3` / `text-sm` | 14px | 20px | 0% | Secondary body, table cells |
| `P2` / `text-base` | 16px | 24px | 0% | **Default body text** |
| `text-lg` | 18px | 28px | 0% | Emphasized body |
| `P1` / `text-xl` | 20px | 28px | 0% | Lead paragraphs |
| `text-2xl` | 24px | 32px | 0% | Large body |
| `text-3xl` | 30px | 36px | 0% | Display body |

### Font Pairing Rules

- **Headings, buttons, labels, nav items:** Poppins Bold (700) or Semi-bold (600)
- **Body text, descriptions, table data, form inputs:** Open Sans Regular (400) or Semi-bold (600)
- **Never mix** — do not use Poppins for body paragraphs or Open Sans for headings
- **Eyebrow text** uses Poppins Semi-bold with `letter-spacing: 10%; text-transform: uppercase`
- **Button text** uses Poppins Semi-bold with `letter-spacing: 2%`

## Spacing System

The Moxy Design System uses an **8px base grid**. All spacing values are multiples of 8:

| Token | Value | Usage |
|-------|-------|-------|
| `spacing-0.5` | 4px | Tight micro-spacing |
| `spacing-1` | 8px | Inline element gaps |
| `spacing-2` | 16px | Component internal padding |
| `spacing-3` | 24px | Section gaps |
| `spacing-4` | 32px | Card padding, form group gaps |
| `spacing-5` | 40px | Large section padding |
| `spacing-6` | 48px | Page section margins |
| `spacing-8` | 64px | Major layout divisions |

## Design Patterns for Aviation Operations

### Status Indication

Flight and operational status must be instantly recognizable. Use color + icon + label (never color alone):

```
On Time     → success (green-600) + checkmark icon
Delayed     → notification (amber-400) + clock icon
Cancelled   → danger (red-600) + x-circle icon
Boarding    → primary (skyBlue-600) + arrow-right icon
Departed    → text-medium (gray-700) + plane-takeoff icon
Arrived     → text-light (gray-500) + plane-landing icon
```

### Data Density Levels

Match information density to the user's operational role:

- **Gate Agent (tablet):** Large touch targets (min 44px), high contrast, P2 body minimum, generous spacing
- **Dispatcher (desktop):** Medium density, data tables with P3/P4 body, compact but scannable
- **Crew (mobile):** Essential info only, clear hierarchy, large status indicators, swipe actions

### Card Pattern

Operational cards (flights, passengers, loads) should follow:

```
┌─────────────────────────────────────────┐
│ [Eyebrow EB2: category]                 │
│ H5 Title                    [Status]    │
│ P3 subtitle / secondary info             │
│─────────────────────────────────────────│
│ Data grid or key-value pairs (P4/P3)     │
│                                          │
│ [Secondary Action]      [Primary Action] │
└─────────────────────────────────────────┘

Border radius: 8px (rounded-lg)
Shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)
Background: white
Border: 1px solid gray-200 (or skyBlue-100 for active/selected)
```

### Navigation

- **Sidebar nav** on desktop: `background-dark` (skyBlue-950), white text, skyBlue-400 active indicator
- **Bottom tab bar** on mobile: white background, skyBlue-600 active icon, gray-400 inactive
- **Top bar:** white or skyBlue-50 background, Breeze logo left, user actions right

### The Warm Breeze Background

For landing pages, dashboards, and feature headers, use the signature Breeze gradient:

```css
.warm-breeze {
  background: linear-gradient(
    135deg,
    rgba(255, 212, 170, 0.3) 0%,      /* sunriseTan-400 @ 30% */
    rgba(255, 82, 123, 0.15) 25%,      /* sunsetPink-400 @ 15% */
    rgba(193, 221, 255, 0.4) 50%,      /* skyBlue-200 @ 40% */
    rgba(255, 255, 255, 0.8) 75%,      /* white @ 80% */
    rgba(193, 221, 255, 0.25) 100%     /* skyBlue-200 @ 25% */
  );
}
```

This creates the organic, flowing pastel warmth seen in the Moxy cover. Use it sparingly — for hero sections and login screens, not for data-heavy operational views.

## Implementation Rules

### CSS Variables Setup

Always define Moxy tokens as CSS custom properties:

```css
:root {
  /* Primary */
  --color-primary-light: #C1DDFF;
  --color-primary: #1F74DF;
  --color-primary-contrast-dark: #02397B;
  --color-primary-dark: #001633;

  /* Secondary */
  --color-highlight-secondary: #FF527B;
  --color-highlight-tertiary: #FFD4AA;
  --color-white: #FFFFFF;

  /* Status */
  --color-success: var(--color-green-600);
  --color-danger: var(--color-red-600);
  --color-notification: var(--color-amber-400);

  /* Text */
  --color-text-dark: #030712;
  --color-text-medium: var(--color-gray-700);
  --color-text-light: var(--color-gray-500);
  --color-hyperlink: #0C4D9D;

  /* Backgrounds */
  --color-bg-light: var(--color-skyBlue-100);
  --color-bg-dark: #001633;
  --color-bg-gray: var(--color-gray-50);
  --color-bg-overlay: rgba(0, 22, 51, 0.7);

  /* Typography */
  --font-heading: 'Poppins', sans-serif;
  --font-body: 'Open Sans', sans-serif;

  /* Spacing (8px grid) */
  --space-1: 8px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
  --space-5: 40px;
  --space-6: 48px;
  --space-8: 64px;

  /* Border radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
}
```

### What NOT to Do

- **Never use colors outside the Moxy token system** — no random hex values, no CSS named colors
- **Never use fonts other than Poppins and Open Sans** — these are the only approved typefaces
- **Never use Poppins for body paragraphs** or Open Sans for headings — respect the pairing
- **Never rely on color alone for status** — always pair with icons and/or text labels
- **Never use purple gradients, Inter, Roboto, or generic AI aesthetics** — these violate brand identity
- **Never sacrifice clarity for aesthetics** — in aviation ops tools, information legibility wins
- **Never ignore the 8px grid** — all spacing must be multiples of 8

### What TO Do

- **Use semantic tokens** (`primary`, `danger`, `text-dark`) not raw scale values (`skyBlue-600`) in application code
- **Start with the darkest navy** (`skyBlue-950`) for headers/nav and the warmest gradient for landing pages
- **Pair bold status colors with soft backgrounds** — e.g., red-600 text on red-50 background for danger states
- **Use Poppins Bold at large sizes** for high-impact moments (hero text, dashboard KPIs, flight numbers)
- **Use Open Sans at P2/P3 sizes** for the bulk of operational content
- **Add subtle depth** with shadows and layered transparency rather than heavy borders
- **Design for bright environments** — airport terminals have overhead lighting and glare. Ensure minimum 4.5:1 contrast ratios
- **Apply motion intentionally** — staggered fade-ins on page load, smooth transitions on status changes. Keep animations under 300ms for operational tools

### Tailwind CSS Integration

When using Tailwind (per ops-fe conventions), extend the theme to include Moxy tokens:

```js
// tailwind.config.js extend
{
  colors: {
    'breeze-blue': {
      50: '#F8F9FF', 100: '#E0C4FF', 200: '#C1DDFF',
      300: '#95C5FF', 400: '#6AA2FF', 500: '#3F96FF',
      600: '#1F74DF', 700: '#0C4D9D', 800: '#02397B',
      900: '#022659', 950: '#001633'
    },
    'sunset-pink': {
      50: '#FFF1F3', 400: '#FF527B', 600: '#E7175B', 950: '#4E031F'
    },
    'sunrise-tan': {
      50: '#FFFAF0', 400: '#FFD4AA', 600: '#E77E22', 950: '#4A1C04'
    },
    'breezy-club': {
      50: '#FEF8EE', 400: '#F19D4A', 600: '#DE6518', 950: '#40190A'
    }
  },
  fontFamily: {
    heading: ['Poppins', 'sans-serif'],
    body: ['Open Sans', 'sans-serif'],
  }
}
```

## Quality Checklist

Before delivering any Breeze interface, verify:

- [ ] All colors reference Moxy tokens (no raw hex in components)
- [ ] Typography uses only Poppins (headings/labels/buttons) and Open Sans (body/data)
- [ ] Spacing follows 8px grid
- [ ] Status states use color + icon + label (not color alone)
- [ ] Touch targets are at minimum 44px for tablet/mobile contexts
- [ ] Contrast ratios meet WCAG 2.1 AA (4.5:1 for text, 3:1 for UI elements)
- [ ] Responsive at minimum desktop (1280px+) and tablet (768px+) breakpoints
- [ ] The Breeze logo appears correctly where brand identity is required
- [ ] Loyalty level colors use the correct tier-specific tokens
- [ ] The overall feel is warm, confident, and distinctly Breeze
