# Storybook Configuration Templates

Boilerplate for the `.storybook/` directory in a Breeze Airways ops-fe project, themed with the Moxy Design System 2.0.

## Directory Structure

```
.storybook/
├── main.ts              # Storybook config (builder, addons, story globs)
├── preview.ts           # Global decorators, parameters, viewports
├── manager.ts           # Storybook UI theme (sidebar, toolbar branding)
└── moxy-decorator.tsx   # Shared decorator providing Moxy CSS vars and fonts
```

---

## .storybook/main.ts

```ts
import type { StorybookConfig } from '@storybook/react-vite';

const config: StorybookConfig = {
  stories: [
    '../libs/**/*.stories.@(ts|tsx)',
  ],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
    '@storybook/addon-interactions',
  ],
  framework: {
    name: '@storybook/react-vite',
    options: {},
  },
  viteFinal: async (config) => {
    // Resolve @ops-fe/ path aliases to match tsconfig.base.json
    const path = await import('path');
    config.resolve = config.resolve || {};
    config.resolve.alias = {
      ...config.resolve.alias,
      // Add aliases dynamically or hardcode known ones:
      // '@ops-fe/shared-ui': path.resolve(__dirname, '../libs/shared/shared-ui/src/index.ts'),
      // '@ops-fe/shared-assets': path.resolve(__dirname, '../libs/shared/shared-assets/src'),
    };
    return config;
  },
  docs: {
    autodocs: 'tag',
  },
  typescript: {
    reactDocgen: 'react-docgen-typescript',
  },
};

export default config;
```

### Adapting for NX

If using NX's built-in Storybook support, the `main.ts` may use NX presets instead:

```ts
import type { StorybookConfig } from '@storybook/react-vite';
import { nxViteTsPaths } from '@nx/vite/plugins/nx-tsconfig-paths.plugin';

const config: StorybookConfig = {
  stories: ['../libs/**/*.stories.@(ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
    '@storybook/addon-interactions',
  ],
  framework: {
    name: '@storybook/react-vite',
    options: {},
  },
  viteFinal: async (config) => {
    // NX plugin auto-resolves tsconfig path aliases
    config.plugins = [...(config.plugins || []), nxViteTsPaths()];
    return config;
  },
  docs: { autodocs: 'tag' },
};

export default config;
```

---

## .storybook/preview.ts

```ts
import type { Preview } from '@storybook/react';
import { MoxyDecorator } from './moxy-decorator';

const preview: Preview = {
  decorators: [MoxyDecorator],
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    viewport: {
      viewports: {
        desktop: {
          name: 'Desktop',
          styles: { width: '1440px', height: '900px' },
        },
        desktopSm: {
          name: 'Desktop SM',
          styles: { width: '1280px', height: '800px' },
        },
        tabletLandscape: {
          name: 'Tablet Landscape',
          styles: { width: '1024px', height: '768px' },
        },
        tabletPortrait: {
          name: 'Tablet Portrait',
          styles: { width: '768px', height: '1024px' },
        },
        mobile: {
          name: 'Mobile',
          styles: { width: '375px', height: '812px' },
        },
      },
    },
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#FFFFFF' },
        { name: 'gray', value: '#F9FAFB' },    // gray-50
        { name: 'dark', value: '#001633' },      // skyBlue-950
        { name: 'primary', value: '#1F74DF' },   // skyBlue-600
      ],
    },
    a11y: {
      config: {
        rules: [
          { id: 'color-contrast', enabled: true },
          { id: 'link-name', enabled: true },
        ],
      },
    },
  },
};

export default preview;
```

---

## .storybook/manager.ts

Brands the Storybook UI itself with Breeze colors.

```ts
import { addons } from '@storybook/manager-api';
import { create } from '@storybook/theming/create';

const breezeTheme = create({
  base: 'light',

  // Brand
  brandTitle: 'Breeze Airways — Ops UI',
  brandUrl: 'https://www.flybreeze.com',
  // brandImage: '/breeze-logo.svg', // Uncomment if logo is in public/

  // Colors
  colorPrimary: '#1F74DF',       // skyBlue-600
  colorSecondary: '#FF527B',     // sunsetPink-400

  // UI
  appBg: '#F8F9FF',             // skyBlue-50
  appContentBg: '#FFFFFF',
  appBorderColor: '#C1DDFF',    // skyBlue-200
  appBorderRadius: 8,

  // Text
  textColor: '#030712',          // text-dark
  textInverseColor: '#FFFFFF',
  textMutedColor: '#6B7280',     // gray-500

  // Toolbar
  barTextColor: '#6B7280',
  barSelectedColor: '#1F74DF',
  barHoverColor: '#FF527B',
  barBg: '#FFFFFF',

  // Form
  inputBg: '#FFFFFF',
  inputBorder: '#C1DDFF',
  inputTextColor: '#030712',
  inputBorderRadius: 4,

  // Typography
  fontBase: '"Open Sans", sans-serif',
  fontCode: 'monospace',
});

addons.setConfig({
  theme: breezeTheme,
});
```

---

## .storybook/moxy-decorator.tsx

Global decorator that wraps every story with Moxy Design System foundations.

```tsx
import React from 'react';
import type { Decorator } from '@storybook/react';

// Moxy CSS custom properties — injected into :root by this decorator
const moxyStyles = `
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap');

  :root {
    /* Primary — Sky Blue */
    --color-skyBlue-50: #F8F9FF;
    --color-skyBlue-100: #E0C4FF;
    --color-skyBlue-200: #C1DDFF;
    --color-skyBlue-300: #95C5FF;
    --color-skyBlue-400: #6AA2FF;
    --color-skyBlue-500: #3F96FF;
    --color-skyBlue-600: #1F74DF;
    --color-skyBlue-700: #0C4D9D;
    --color-skyBlue-800: #02397B;
    --color-skyBlue-900: #022659;
    --color-skyBlue-950: #001633;

    /* Secondary — Sunset Pink */
    --color-sunsetPink-50: #FFF1F3;
    --color-sunsetPink-400: #FF527B;
    --color-sunsetPink-600: #E7175B;
    --color-sunsetPink-950: #4E031F;

    /* Secondary — Sunrise Tan */
    --color-sunriseTan-50: #FFFAF0;
    --color-sunriseTan-400: #FFD4AA;
    --color-sunriseTan-600: #E77E22;
    --color-sunriseTan-950: #4A1C04;

    /* Semantic */
    --color-primary-light: #C1DDFF;
    --color-primary: #1F74DF;
    --color-primary-contrast-dark: #02397B;
    --color-primary-dark: #001633;
    --color-highlight-secondary: #FF527B;
    --color-highlight-tertiary: #FFD4AA;
    --color-white: #FFFFFF;

    /* Status */
    --color-success-light: #F0FDF4;
    --color-success: #16A34A;
    --color-success-dark: #166534;
    --color-danger-light: #FEF2F2;
    --color-danger: #DC2626;
    --color-danger-dark: #991B1B;
    --color-notification-light: #FFFBEB;
    --color-notification: #FBBF24;
    --color-notification-dark: #B45309;

    /* Text */
    --color-text-dark: #030712;
    --color-text-medium: #374151;
    --color-text-light: #6B7280;
    --color-hyperlink: #0C4D9D;

    /* Backgrounds */
    --color-bg-light: #E0C4FF;
    --color-bg-dark: #001633;
    --color-bg-gray: #F9FAFB;
    --color-bg-overlay: rgba(0, 22, 51, 0.7);

    /* Typography */
    --font-heading: 'Poppins', sans-serif;
    --font-body: 'Open Sans', sans-serif;

    /* Spacing (8px grid) */
    --space-0-5: 4px;
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

  *, *::before, *::after {
    box-sizing: border-box;
  }

  body {
    font-family: var(--font-body);
    color: var(--color-text-dark);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-heading);
    font-weight: 700;
  }
`;

export const MoxyDecorator: Decorator = (Story) => (
  <>
    <style>{moxyStyles}</style>
    <Story />
  </>
);
```

### If the Project Uses Tailwind

When the project already has Tailwind configured with Moxy tokens (per the breeze-design skill's Tailwind config), the decorator can be simplified to just load fonts and import the Tailwind stylesheet:

```tsx
import React from 'react';
import type { Decorator } from '@storybook/react';
import '../src/styles/globals.css'; // Tailwind entry point

const fontImport = `
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap');
`;

export const MoxyDecorator: Decorator = (Story) => (
  <>
    <style>{fontImport}</style>
    <Story />
  </>
);
```

---

## Required Dependencies

Add these to `package.json` devDependencies:

```json
{
  "@storybook/react": "^8.x",
  "@storybook/react-vite": "^8.x",
  "@storybook/addon-essentials": "^8.x",
  "@storybook/addon-a11y": "^8.x",
  "@storybook/addon-interactions": "^8.x",
  "@storybook/test": "^8.x",
  "@storybook/manager-api": "^8.x",
  "@storybook/theming": "^8.x",
  "storybook": "^8.x"
}
```

## NX Integration

If using NX's Storybook generators, the project may already have per-library Storybook configs. In that case:

- The root `.storybook/` serves as the **composition root** that aggregates all library stories
- Individual library `project.json` files may define `storybook` and `build-storybook` targets
- Use `npx nx run {lib}:storybook` to run stories for a single library
- Use the root config to run all stories together

Check for existing NX Storybook config before scaffolding:
```bash
# Check if any library already has Storybook configured
grep -r "storybook" libs/*/project.json 2>/dev/null
```
