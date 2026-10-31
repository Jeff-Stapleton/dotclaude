---
name: diagram
description: Generate a single SVG system architecture diagram from a description or existing spec/progress files. Produces a detailed, annotated diagram suitable for design docs and team reviews.
user-invocable: true
argument-hint: <description of the system or component to diagram>
---

# SVG Architecture Diagram

Generate a single SVG architecture diagram — service boundaries, data flows, team ownership, new vs. existing components — from a description, spec file, or task context.

## Arguments

`$ARGUMENTS` — Description of the system to diagram, or a reference to spec/progress files to read first. If empty, infer from the currently open files and task context.

## Process

1. **Understand the system.** Read any spec, progress, or code files relevant to the task. Identify: services, data stores, external systems, data flows, team ownership boundaries, and which components are new vs. existing vs. modified.

2. **Plan the layout.** Sketch the rough spatial arrangement before writing SVG. Common layouts:
   - **Left-to-right pipeline:** Trigger → Process → Store → Publish → Consume
   - **Layered:** Client on top, API layer, services, datastores at bottom
   - **Grouped by team:** One colored region per team, inter-team arrows crossing boundaries

3. **Write the SVG.** Follow all rules below. Save the file to the current task directory (e.g., `~/.claude/tasks/<project>/<task>/architecture.svg`) or to the repo root if no task is active.

4. **Report.** Tell the user where the file was saved and what it shows.

---

## The Arrow Rule (Critical — Prevents Black Triangles)

The most common SVG arrowhead bug produces a solid black filled triangle regardless of line color. The fix: **always use `<polygon>` with an explicit `fill`, and always set `viewBox` on the marker.**

**Correct pattern — use this verbatim:**

```xml
<defs>
  <marker id="arrow" viewBox="0 0 10 7" refX="9" refY="3.5" markerWidth="10" markerHeight="7" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#475569"/>
  </marker>
  <marker id="arrow-blue" viewBox="0 0 10 7" refX="9" refY="3.5" markerWidth="10" markerHeight="7" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#3b82f6"/>
  </marker>
  <marker id="arrow-green" viewBox="0 0 10 7" refX="9" refY="3.5" markerWidth="10" markerHeight="7" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#16a34a"/>
  </marker>
  <marker id="arrow-amber" viewBox="0 0 10 7" refX="9" refY="3.5" markerWidth="10" markerHeight="7" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#d97706"/>
  </marker>
  <marker id="arrow-purple" viewBox="0 0 10 7" refX="9" refY="3.5" markerWidth="10" markerHeight="7" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#7c3aed"/>
  </marker>
  <marker id="arrow-red" viewBox="0 0 10 7" refX="9" refY="3.5" markerWidth="10" markerHeight="7" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#dc2626"/>
  </marker>
</defs>
```

**What causes black triangles (never do these):**
- Using `fill="context-stroke"` — not well-supported
- Using `<path d="M0,0 L8,3 L0,6 Z"/>` without an explicit `fill` attribute (inherits black)
- Omitting `viewBox` on the `<marker>` element — misscales the arrowhead
- Omitting `refX`/`refY` — tip of the arrow lands in the wrong place
- Only declaring one generic `arrow` marker and trying to change its color per-line — doesn't work

**Usage on lines:**
```xml
<line x1="200" y1="100" x2="350" y2="100" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arrow-blue)"/>
```
The stroke color and the marker fill must match — they are independent attributes.

---

## Design System

### Canvas

```
viewBox:     0 0 1200 820  (adjust height to content — 820/860/900 are all fine)
Background:  <rect width="1200" height="820" fill="#f8fafc" rx="8"/>
Font:        font-family="Inter, -apple-system, sans-serif"
```

### Text Sizes

| Role | Size | Weight | Color |
|------|------|--------|-------|
| Diagram title | 18px | 700 | `#0f172a` |
| Diagram subtitle | 12px | 400 | `#64748b` |
| Group heading | 14px | 700 | group color (e.g. `#1e40af`) |
| Component name | 12–13px | 600 | group color or `#334155` |
| Detail / caption | 10px | 400 | `#64748b` |
| Monospace field | 10–11px | 400 | `#475569`, `font-family="monospace"` |
| Badge text | 8px | 700 | `#fff` |
| Arrow label | 9px | 400 | matches arrow color |
| Section header | 11px | 600 | `#94a3b8` (ALL CAPS) |

### Drop Shadow (all component boxes)

```xml
<filter id="shadow" x="-4%" y="-4%" width="108%" height="112%">
  <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
</filter>
```

Apply with `filter="url(#shadow)"` on any `<rect>` that represents a service or store.

### Color Palette

```
Slate / default:   stroke #e2e8f0,  text #334155,  arrow #475569
Blue (ops-be):     group bg #eff6ff, group stroke #bfdbfe, box stroke #93c5fd, text #1e40af
Green (loyalty/new): group bg #f0fdf4, group stroke #bbf7d0, box stroke #86efac, text #15803d
Amber (new client):  box stroke #d97706, text #92400e
Purple (modified):   box stroke #7c3aed, text #5b21b6
Red (warning):       text #dc2626

Callout amber:  fill #fefce8, stroke #fde68a,  text #92400e / #78350f
Callout red:    fill #fef2f2, stroke #fecaca,  text #991b1b / #7f1d1d
Callout orange: fill #fff7ed, stroke #fed7aa,  text #9a3412 / #7c2d12
Callout blue:   fill #eff6ff, stroke #bfdbfe,  text #1e40af
```

---

## Component Patterns

### Cluster / deployment boundary (outermost)
```xml
<rect x="30" y="72" width="1140" height="660" rx="12"
      fill="none" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="8 4"/>
<text x="50" y="92" font-size="11" fill="#94a3b8" font-weight="600">
  KUBERNETES CLUSTER (same VPC — internal DNS, service mesh mTLS)
</text>
```

### Team / service group (colored region)
```xml
<!-- Blue group (our team) -->
<rect x="50" y="186" width="560" height="530" rx="10"
      fill="#eff6ff" stroke="#bfdbfe" stroke-width="1"/>
<text x="70" y="210" font-size="14" font-weight="700" fill="#1e40af">operations-back-end</text>
<text x="260" y="210" font-size="10" fill="#64748b" font-style="italic">our team</text>

<!-- Green group (another team) -->
<rect x="660" y="186" width="500" height="380" rx="10"
      fill="#f0fdf4" stroke="#bbf7d0" stroke-width="1"/>
<text x="680" y="210" font-size="14" font-weight="700" fill="#15803d">loyalty-tier</text>
<text x="800" y="210" font-size="10" fill="#64748b" font-style="italic">Go, Gin REST</text>
```

### Service / component box
```xml
<rect x="75" y="230" width="210" height="64" rx="8"
      fill="#fff" stroke="#93c5fd" stroke-width="1.5" filter="url(#shadow)"/>
<text x="180" y="254" text-anchor="middle" font-size="12" font-weight="600" fill="#1e40af">GraphQL API</text>
<text x="180" y="270" text-anchor="middle" font-size="10" fill="#64748b">Seat Map Resolver</text>
```

### External system box (white, light gray stroke, no group)
```xml
<rect x="60" y="108" width="190" height="56" rx="8"
      fill="#fff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#shadow)"/>
<text x="155" y="132" text-anchor="middle" font-size="12" font-weight="600" fill="#334155">Crew Mobile App</text>
<text x="155" y="148" text-anchor="middle" font-size="10" fill="#64748b">integrations-front-end</text>
```

### Database box
```xml
<rect x="60" y="470" width="330" height="230" rx="8"
      fill="#fff" stroke="#93c5fd" stroke-width="1.5" filter="url(#shadow)"/>
<!-- Small DB badge -->
<rect x="75" y="483" width="24" height="18" rx="3" fill="#dbeafe"/>
<text x="87" y="496" text-anchor="middle" font-size="9" fill="#1e40af">DB</text>
<text x="115" y="496" font-size="13" font-weight="600" fill="#1e40af">Ops Postgres</text>

<!-- Table within the DB box -->
<rect x="80" y="514" width="290" height="170" rx="6" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"/>
<text x="225" y="534" text-anchor="middle" font-size="11" font-weight="700" fill="#334155">table_name</text>
<text x="96" y="554" font-size="10" fill="#475569" font-family="monospace">column_one</text>
<!-- Highlight a new/changed column with a colored band -->
<rect x="96" y="630" width="254" height="16" rx="2" fill="#dbeafe"/>
<text x="100" y="642" font-size="10" fill="#1e40af" font-weight="600" font-family="monospace">+ new_column (NEW — purpose)</text>
```

### NEW / MODIFY badges
```xml
<!-- NEW badge — green -->
<rect x="325" y="328" width="32" height="14" rx="3" fill="#16a34a"/>
<text x="341" y="338" text-anchor="middle" font-size="8" fill="#fff" font-weight="700">NEW</text>

<!-- MODIFY badge — purple -->
<rect x="425" y="474" width="52" height="14" rx="3" fill="#7c3aed"/>
<text x="451" y="484" text-anchor="middle" font-size="8" fill="#fff" font-weight="700">MODIFY</text>
```
Place badge in the top-left corner of the containing component box.

### Phase / section dividers (horizontal swimlane style)
```xml
<text x="40" y="92" font-size="11" font-weight="700" fill="#6b7280"
      letter-spacing="1.5">1  TRIGGER</text>
<line x1="130" y1="88" x2="1060" y2="88" stroke="#e5e7eb" stroke-width="1"/>
```

---

## Arrow Patterns

### Solid arrow (synchronous primary flow)
```xml
<line x1="285" y1="364" x2="311" y2="364"
      stroke="#d97706" stroke-width="1.5" marker-end="url(#arrow-amber)"/>
<text x="298" y="358" text-anchor="middle" font-size="9" fill="#d97706">label</text>
```

### Dashed arrow (async / background / existing / alternative)
```xml
<line x1="790" y1="432" x2="790" y2="476"
      stroke="#16a34a" stroke-width="1.2" stroke-dasharray="4 3" marker-end="url(#arrow-green)"/>
```

### Curved path arrow (routing around other elements)
```xml
<path d="M 595 504 L 644 504 Q 650 504 650 510 L 650 514 Q 650 520 656 520 L 936 520"
      stroke="#94a3b8" stroke-width="1.2" fill="none" stroke-dasharray="4 3"
      marker-end="url(#arrow)"/>
```
Use `fill="none"` on `<path>` — without it the path interior fills black.

---

## Callout Cards (bottom of diagram)

Use 2–3 callout cards at the bottom to summarize key flows, open questions, or tradeoffs.

```xml
<!-- Flow summary — amber -->
<rect x="50" y="748" width="560" height="56" rx="8"
      fill="#fefce8" stroke="#fde68a" stroke-width="1"/>
<text x="70" y="770" font-size="11" font-weight="700" fill="#92400e">Request flow:</text>
<text x="70" y="788" font-size="10" fill="#78350f">Client → Resolver → Service → DB + External → merge → response</text>

<!-- Open question — red -->
<rect x="630" y="748" width="530" height="56" rx="8"
      fill="#fef2f2" stroke="#fecaca" stroke-width="1"/>
<text x="650" y="770" font-size="11" font-weight="700" fill="#991b1b">OPEN: Question Title</text>
<text x="650" y="788" font-size="10" fill="#7f1d1d">Description of the open question or risk.</text>

<!-- Prerequisite / dependency — orange -->
<rect x="660" y="580" width="500" height="68" rx="8"
      fill="#fff7ed" stroke="#fed7aa" stroke-width="1"/>
<text x="680" y="600" font-size="11" font-weight="700" fill="#9a3412">Prerequisite: Title</text>
<text x="680" y="618" font-size="10" fill="#7c2d12">Line one of the prerequisite description.</text>
<text x="680" y="634" font-size="10" fill="#7c2d12">Line two if needed.</text>
```

---

## Layout Tips

- **Top margin:** Title at y=36, subtitle at y=56. Cluster/content starts at y=72–100.
- **Spacing:** 16–24px between sibling boxes vertically, 16–20px horizontally between boxes in the same row.
- **Arrow clearance:** End lines 4–6px before the target box edge so the arrowhead doesn't overlap the border.
- **Text wrapping:** SVG has no text wrapping. Break long labels across multiple `<text>` elements with fixed `y` increments of 14–16px (for 10px font) or 18–20px (for 12–13px font).
- **Section comments:** Use `<!-- ═══ SECTION NAME ═══ -->` comments to divide the SVG into readable sections.
- **ViewBox height:** Add up the vertical space used by all sections + callouts + margins and set the height to that value. Don't leave a large empty strip at the bottom.

---

## XML Safety Rules

- `fill="none"` on every `<path>` that represents a line/arrow (not a filled shape)
- `&amp;` not `&` in text; `&lt;` / `&gt;` for angle brackets
- No duplicate attributes on any element
- `rx` takes one value only (e.g., `rx="8"` not `rx="8 8 0 0"`)
- Do not use `<style>` blocks — use inline `font-family`, `font-size`, `fill` attributes

---

## Example Invocations

- `/svg-architecture-diagram` — infer system from open files and task context
- `/svg-architecture-diagram for the connection messaging feature based on spec.md`
- `/svg-architecture-diagram showing how the loyalty-tier service integrates with ops-backend`
