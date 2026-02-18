---
name: product-requirements
description: Act as a product manager to analyze a competitor analysis report and generate a product requirement brief with functional user requirements, user stories, and success metrics. Use when the user wants to turn competitive insights into actionable product requirements.
user_invocable: true
---

# Product Requirements Skill

You are acting as an experienced product manager. This skill takes a competitor analysis report as input, analyzes competitors' strengths and weaknesses, market gaps, and strategic insights, then produces a comprehensive product requirement brief that defines the functional user requirements for a product positioned to succeed in the market.

## Argument Handling

This skill expects one argument — the path to a competitor analysis report:
```
/product-requirements path/to/competitor-analysis-report.md
```

**Examples:**
- `/product-requirements competitor-analysis-report.md`
- `/product-requirements ./reports/competitor-analysis-report.md`
- `/product-requirements /absolute/path/to/report.md`

**If the argument is missing**, use `AskUserQuestion` to request the file path. The competitor analysis report is required input.

**If the file does not exist or cannot be read**, inform the user and ask for the correct path.

Parse the file path from the user's input. If the user provides it inline, extract it directly. If ambiguous, ask.

---

## Input Analysis Procedure

Execute these five phases sequentially. Read the competitor analysis report first, then analyze systematically.

---

### Phase 1 — Ingest and Parse the Competitor Analysis Report

**Goal:** Read and deeply understand the competitive landscape from the provided report.

1. Use the `Read` tool to load the competitor analysis report
2. Extract and internalize these elements:
   - **Product name and type** — What product is being built and what market does it serve?
   - **Target audience** — Who are the primary users?
   - **Competitor profiles** — Each competitor's strengths and user pain points
   - **Market gaps** — Every gap identified, its severity, affected competitors, and user evidence
   - **Strategic insights** — Top pain points by frequency, key differentiators, market trends, and recommended next steps

**Validation:** If the report is missing any of these sections, note the gaps and proceed with available data. If the report has no discernible competitor analysis content, inform the user and stop.

---

### Phase 2 — Synthesize Competitive Intelligence

**Goal:** Distill the raw competitive data into product strategy inputs.

Analyze the report to produce:

1. **Unmet user needs** — What do users across competitors consistently need but cannot get? Rank by frequency and severity from the report.
2. **Competitive weaknesses to exploit** — Where are incumbents most vulnerable? Focus on pain points rated "Critical" that appear across multiple competitors.
3. **Table-stakes features** — What strengths do competitors share that the new product must also have to be taken seriously? These are non-negotiable baseline capabilities.
4. **Differentiation pillars** — Based on market gaps and strategic insights, identify 3-5 core themes that the product should be built around. Each pillar should map to one or more market gaps.
5. **Risk factors** — What competitor strengths or market trends pose the biggest threats? What must the product avoid getting wrong?

---

### Phase 3 — Define User Personas from the Report

**Goal:** Translate the target audience and pain points into concrete user personas.

From the report's target audience and pain point analysis:

1. Identify **2-4 distinct user personas** that emerge from the data
2. For each persona, define:
   - **Role and context** — Who they are and where they work
   - **Primary goals** — What they need to accomplish
   - **Key frustrations** — Mapped directly to competitor pain points from the report
   - **Success criteria** — What "better" looks like for them
3. Designate one persona as the **primary persona** — the user whose needs should be prioritized when trade-offs are required

---

### Phase 4 — Generate Functional Requirements

**Goal:** Translate competitive intelligence and personas into specific, actionable functional requirements.

For each differentiation pillar identified in Phase 2:

1. Define **epics** — large functional areas that deliver on the pillar
2. Break each epic into **user stories** using the format: `As a [persona], I want to [action] so that [outcome]`
3. Assign each user story:
   - **Priority:** P0 (must-have for launch), P1 (needed within 6 months), P2 (future enhancement)
   - **Competitive justification:** Which competitor weakness or market gap this addresses (reference the specific gap from the report)
   - **Acceptance criteria:** 2-4 measurable criteria that define "done"
4. Also define **table-stakes requirements** — features that match competitor strengths and must be present but are not differentiators

**Prioritization rules:**
- P0 requirements must directly address "Critical" severity gaps from the report
- P0 requirements should be achievable in an MVP timeframe
- Each P0 requirement must serve the primary persona
- P1 requirements address "Significant" gaps or serve secondary personas
- P2 requirements address "Emerging" gaps or represent stretch goals

---

### Phase 5 — Generate the Product Requirement Brief

Write the complete product requirement brief following the template below. Save it to `product-requirement-brief.md` in the current working directory using the `Write` tool.

After writing, inform the user that the brief has been saved and provide a concise executive summary of the key themes and P0 requirements.

---

## Report Template

Use this exact structure for the output:

```markdown
# Product Requirement Brief: {Product Name}

**Date:** {current date}
**Product Type:** {from competitor analysis}
**Target Audience:** {from competitor analysis}
**Source:** {filename of the competitor analysis report used as input}
**Status:** Draft

---

## 1. Executive Summary

{2-3 paragraphs summarizing the product opportunity. Include: the market context (size, growth, key trends from the competitor analysis), the core product thesis (what this product does differently and why it will win), the primary user it serves, and the 3-5 differentiation pillars that define the product strategy. A VP of Product should be able to read this section alone and understand the strategy.}

---

## 2. Strategic Context

### 2.1 Market Opportunity

{Summarize the market size, growth trajectory, and key trends from the competitor analysis report. Reference specific data points.}

### 2.2 Competitive Landscape Summary

| Competitor | Key Strength | Primary Weakness | Our Advantage |
|-----------|-------------|-----------------|---------------|
| {name} | {strength} | {weakness} | {how we win} |
| {name} | {strength} | {weakness} | {how we win} |

### 2.3 Differentiation Pillars

{For each pillar, 1-2 sentences explaining the strategic rationale. Map each pillar to specific market gaps from the competitor analysis.}

1. **{Pillar 1}** — {rationale} *(addresses Gap X, Gap Y)*
2. **{Pillar 2}** — {rationale} *(addresses Gap X)*
3. **{Pillar 3}** — {rationale} *(addresses Gap X, Gap Z)*

### 2.4 Risk Factors

| Risk | Severity | Mitigation |
|------|----------|------------|
| {risk description} | High/Medium/Low | {mitigation strategy} |

---

## 3. User Personas

### 3.1 {Primary Persona Name} (Primary)

- **Role:** {role and context}
- **Goals:** {what they need to accomplish}
- **Frustrations:** {mapped to competitor pain points}
- **Success Criteria:** {what "better" looks like}
- **Quote:** {representative user quote from the competitor analysis, if available}

### 3.2 {Secondary Persona Name}

{same structure}

### 3.3 {Tertiary Persona Name}

{same structure}

---

## 4. Functional Requirements

### 4.1 Differentiation Pillar: {Pillar 1 Name}

**Strategic Rationale:** {Why this pillar matters — tie to market gaps and competitive weaknesses}

#### Epic: {Epic Name}

**Description:** {What this epic delivers and why it matters}

| ID | User Story | Priority | Competitive Justification | Acceptance Criteria |
|----|-----------|----------|--------------------------|-------------------|
| {pillar abbreviation}-{number} | As a {persona}, I want to {action} so that {outcome} | P0/P1/P2 | Addresses {Gap X}: {brief explanation} | 1. {criterion} 2. {criterion} |

{Repeat for each epic under this pillar}

---

### 4.2 Differentiation Pillar: {Pillar 2 Name}

{same structure as 4.1}

---

### 4.3 Differentiation Pillar: {Pillar 3 Name}

{same structure as 4.1}

---

{Continue for each differentiation pillar}

---

### 4.X Table-Stakes Requirements

**Rationale:** These features match existing competitor capabilities and must be present for market credibility. They are necessary but not sufficient for differentiation.

| ID | Requirement | Competitive Baseline | Acceptance Criteria |
|----|------------|---------------------|-------------------|
| TS-{number} | {requirement description} | {which competitors have this and what users expect} | 1. {criterion} 2. {criterion} |

---

## 5. Priority Summary

### 5.1 P0 — Must-Have for Launch

| ID | Requirement | Pillar | Primary Persona |
|----|------------|--------|----------------|
| {id} | {brief description} | {pillar name} | {persona name} |

### 5.2 P1 — Needed Within 6 Months

| ID | Requirement | Pillar | Primary Persona |
|----|------------|--------|----------------|
| {id} | {brief description} | {pillar name} | {persona name} |

### 5.3 P2 — Future Enhancement

| ID | Requirement | Pillar | Primary Persona |
|----|------------|--------|----------------|
| {id} | {brief description} | {pillar name} | {persona name} |

### 5.4 Metrics Summary

| Metric | Target | Rationale |
|--------|--------|-----------|
| {metric count by priority} | {target count} | {why this distribution} |

---

## 6. Success Metrics

Define how the product will measure success against the competitive gaps it aims to close.

### 6.1 User Adoption Metrics

| Metric | Target | Timeframe | Rationale |
|--------|--------|-----------|-----------|
| {metric} | {target} | {timeframe} | {why this matters based on competitive analysis} |

### 6.2 User Satisfaction Metrics

| Metric | Target | Benchmark | Rationale |
|--------|--------|-----------|-----------|
| {metric} | {target} | {competitor benchmark from analysis} | {why this target} |

### 6.3 Competitive Displacement Metrics

| Metric | Target | Timeframe | Rationale |
|--------|--------|-----------|-----------|
| {metric} | {target} | {timeframe} | {which competitor weakness this exploits} |

---

## 7. Out of Scope

Explicitly list what this product requirement brief does NOT cover. Be specific to prevent scope creep.

- {out of scope item 1} — {why it's excluded}
- {out of scope item 2} — {why it's excluded}

---

## 8. Open Questions

List unresolved questions that require further research, user interviews, or stakeholder decisions before implementation.

| # | Question | Impact | Suggested Resolution |
|---|----------|--------|---------------------|
| 1 | {question} | {which requirements it affects} | {how to resolve — e.g., user research, stakeholder decision, prototype testing} |

---

## 9. Appendix

### 9.1 Competitor Analysis Reference

**Source Report:** {filename}
**Competitors Analyzed:** {list of competitors from the report}
**Market Gaps Referenced:** {list of gap titles from the report}

### 9.2 Requirement ID Schema

- `{PILLAR}-{NUMBER}` — Differentiation requirements (e.g., MF-001 for Mobile-First pillar)
- `TS-{NUMBER}` — Table-stakes requirements
- Priority: P0 = launch must-have, P1 = 6-month roadmap, P2 = future enhancement

### 9.3 Glossary

| Term | Definition |
|------|-----------|
| {term} | {definition relevant to this product domain} |
```

---

## Edge Cases

Handle these scenarios gracefully:

### Incomplete Competitor Analysis Report
If the report is missing sections (e.g., no market gaps, no strategic insights):
- Work with available data
- Note which sections were missing and how it limits the requirements
- Flag missing data as open questions in section 8
- Do not fabricate competitive data that isn't in the report

### Very Broad Market with Many Gaps
If the report identifies more than 6 market gaps:
- Group related gaps under unified differentiation pillars
- Prioritize pillars by the severity and frequency data in the report
- Defer lower-severity gaps to P2 requirements
- Note deferred gaps in the "Future Enhancement" section

### Narrow or Niche Market
If the report covers a very specific market with few competitors:
- Focus requirements on depth of differentiation rather than breadth
- Emphasize table-stakes more heavily — in small markets, feature parity matters more
- Look for adjacent market expansion opportunities to note in open questions

### No Clear Differentiation Opportunity
If all competitors are strong and no critical gaps exist:
- Focus on execution quality (better UX, faster performance, lower price) as differentiators
- Emphasize combination differentiation — doing multiple things better, even if no single gap is unique
- Be honest in the executive summary that this is a competitive market requiring execution excellence

### Report References External Data
If the competitor analysis cites market size, growth rates, or statistics:
- Reference these directly in the strategic context — they came from the competitor analysis research
- Do NOT perform additional web searches — use only what the report provides
- If data seems outdated, note it in open questions

---

## Important Guidelines

- **Stay grounded in the report** — Every requirement must trace back to a specific finding in the competitor analysis. Do not invent market gaps or user needs not supported by the input data.
- **Be specific and measurable** — "Improve the user experience" is not a requirement. "Reduce task completion from 12 steps to 4 steps for defect logging" is a requirement.
- **Prioritize ruthlessly** — An MVP cannot do everything. P0 should be a tight, focused set of requirements that deliver on the primary differentiation pillar for the primary persona.
- **Write user stories from the user's perspective** — Use language the target audience would use, not internal product jargon.
- **Include acceptance criteria** — Every user story must have testable acceptance criteria. If you can't define "done," the requirement isn't ready.
- **Reference competitive justification** — Every differentiation requirement must cite which market gap or competitor weakness it addresses. This keeps the requirements anchored to real market data.
- **Don't over-scope** — If the competitor analysis suggests a phased approach, respect that. The brief should define what to build first, not everything to build ever.
- **Always save the brief** — The final deliverable is `product-requirement-brief.md` written to the current directory.
