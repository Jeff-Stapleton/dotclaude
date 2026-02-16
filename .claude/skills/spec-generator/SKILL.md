---
name: spec-generator
description: Generate specification documents for code repositories following established patterns. Creates well-structured markdown specs with architecture diagrams, code examples, and proper organization. Use when planning features, documenting systems, or creating technical specifications.
---

# Spec Generator Skill

Generate specification documents following established patterns from professional codebases. This skill creates comprehensive, well-structured markdown specifications.

## When to Use

- Planning a new feature or system before implementation
- Documenting an existing system that lacks specs
- Creating architectural design documents
- Writing technical specifications for code review

## Spec File Location

**Convention:** Place specs in a `specs/` directory at the project root.

```
project-root/
├── specs/
│   ├── README.md          # Index of all specs
│   ├── architecture.md
│   ├── feature-system.md
│   └── ...
└── src/
```

## File Naming Convention

Use **kebab-case** (lowercase with hyphens):

| Type | Pattern | Example |
|------|---------|---------|
| System specs | `{name}-system.md` | `auth-system.md`, `tool-system.md` |
| Architecture | `architecture.md` | Top-level system design |
| Features | `{feature-name}.md` | `streaming.md`, `health-check.md` |
| Plans | `{name}-plan.md` | `migration-plan.md` |
| Phases | `{feature}-phase-{n}.md` | `websocket-phase-2.md` |

## Spec File Template

Every spec must follow this structure:

```markdown
# [System/Feature Name]

**Status:** [Planned|Draft|Implemented]
**Version:** 1.0
**Last Updated:** [YYYY-MM-DD]

---

## 1. Overview

Brief description of what this system/feature does and why it exists.

### 1.1 Purpose

What problem does this solve? What is the core functionality?

### 1.2 Goals

- Goal 1
- Goal 2
- Goal 3

### 1.3 Non-Goals

Explicitly list what is NOT in scope:

- Non-goal 1
- Non-goal 2

### 1.4 Related Specifications

- [Related Spec 1](./related-spec.md) - Brief description
- [Related Spec 2](./another-spec.md) - Brief description

---

## 2. Architecture

### 2.1 System Diagram

Use ASCII art for architecture diagrams:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Component A   │────▶│   Component B    │────▶│   Component C   │
│   (purpose)     │     │   (purpose)      │     │   (purpose)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   Component D    │
                        │   (purpose)      │
                        └──────────────────┘
```

### 2.2 Directory/Module Structure

```
src/
├── feature/
│   ├── mod.rs
│   ├── types.rs
│   └── impl.rs
└── ...
```

---

## 3. Core Types

Define the main types/interfaces with code examples:

### 3.1 Primary Type

```rust
pub struct ExampleType {
    pub field_a: String,
    pub field_b: Option<i32>,
}
```

| Field | Type | Description |
|-------|------|-------------|
| `field_a` | `String` | Description of field_a |
| `field_b` | `Option<i32>` | Description of field_b |

### 3.2 Traits/Interfaces

```rust
pub trait ExampleTrait {
    fn method_a(&self) -> Result<(), Error>;
    fn method_b(&self, input: String) -> Output;
}
```

| Method | Purpose |
|--------|---------|
| `method_a()` | Description of method_a |
| `method_b()` | Description of method_b |

---

## 4. Implementation Details

### 4.1 Flow/Process

Describe the step-by-step process:

1. **Step 1** - Description
2. **Step 2** - Description
3. **Step 3** - Description

### 4.2 State Machine (if applicable)

```
┌─────────┐
│ State A │  (trigger event)
└────┬────┘
     │
     ▼
┌─────────┐
│ State B │  (processing)
└────┬────┘
     │
     ▼
┌───────────┐
│ State C   │  (complete)
└───────────┘
```

---

## 5. Configuration

### 5.1 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VAR_NAME` | Yes | - | Description |
| `OPTIONAL_VAR` | No | `default` | Description |

### 5.2 Configuration File

```toml
[section]
key = "value"
```

---

## 6. API (if applicable)

### 6.1 Endpoints

#### `POST /api/endpoint`

**Request:**
```json
{
  "field": "value"
}
```

**Response:**
```json
{
  "result": "success"
}
```

---

## 7. Security Considerations

- **Authentication:** How is access controlled?
- **Authorization:** What permissions are required?
- **Data Protection:** How is sensitive data handled?

---

## 8. Error Handling

### 8.1 Error Types

```rust
pub enum ExampleError {
    NotFound(String),
    InvalidInput(String),
    Internal(String),
}
```

### 8.2 Recovery Strategies

| Error | Recovery |
|-------|----------|
| `NotFound` | Return 404, log warning |
| `InvalidInput` | Return 400 with details |
| `Internal` | Return 500, log error, alert |

---

## 9. Testing Strategy

- **Unit Tests:** Test individual functions
- **Integration Tests:** Test component interactions
- **Property-Based Tests:** Test invariants with proptest

---

## 10. Design Decisions

### 10.1 Why [Decision A]?

Explain the rationale for key architectural decisions.

**Alternatives considered:**
1. Alternative approach 1 - Why rejected
2. Alternative approach 2 - Why rejected

**Trade-offs:**
- Pro: Benefit of chosen approach
- Con: Limitation of chosen approach

---

## 11. Implementation Notes

References to actual implementation:

- Main implementation: `src/feature/mod.rs`
- Types defined in: `src/feature/types.rs`
- Tests in: `src/feature/tests.rs`

---

## 12. Future Enhancements

- [ ] Planned feature 1
- [ ] Planned feature 2
- [ ] Planned feature 3
```

## Index File (specs/README.md)

Always maintain an index file:

```markdown
# [Project Name] Specifications

Design documentation for [brief project description].

## [Category 1]

| Spec | Code | Purpose |
|------|------|---------|
| [spec-name.md](./spec-name.md) | [src/module](../src/module/) | Brief description |

## [Category 2]

| Spec | Code | Purpose |
|------|------|---------|
| [another-spec.md](./another-spec.md) | [src/other](../src/other/) | Brief description |
```

## Markdown Formatting Rules

1. **Headers:** H1 for title, H2 for major sections (numbered), H3 for subsections
2. **Code Blocks:** Always specify language (`rust`, `json`, `bash`, etc.)
3. **Tables:** Use for comparisons, field definitions, API params
4. **ASCII Diagrams:** Use box-drawing characters for architecture
5. **Bold:** Use `**bold**` for emphasis and key terms
6. **Inline Code:** Use backticks for identifiers, paths, commands
7. **Separators:** Use `---` between major sections

## Status Values

- **Planned** - Spec written, implementation not started
- **Draft** - Implementation in progress, spec may change
- **Implemented** - Complete and stable

## ASCII Box Characters Reference

```
Corners: ┌ ┐ └ ┘
Lines:   ─ │
T-joins: ┬ ┴ ├ ┤
Cross:   ┼
Arrows:  ▶ ▼ ◀ ▲ → ← ↓ ↑
```

## Step-by-Step Process

1. **Determine spec type:** Is this a system, feature, plan, or architecture doc?
2. **Create file:** Use proper naming convention in `specs/` directory
3. **Add header:** Title, metadata (status, version, date)
4. **Write Overview:** Purpose, goals, non-goals, related specs
5. **Add Architecture:** Diagrams, module structure
6. **Define Types:** Core types with code examples and tables
7. **Detail Implementation:** Flow, state machines, configuration
8. **Document API:** Endpoints, request/response formats
9. **Address Security:** Auth, authz, data protection
10. **Add Testing:** Testing strategy and approach
11. **Explain Decisions:** Rationale for key choices
12. **Update Index:** Add entry to specs/README.md

## Example Usage

**User:** "Create a spec for the notification system"

**Response:** Create `specs/notification-system.md` following the template above, then update `specs/README.md` to include it in the index.
 