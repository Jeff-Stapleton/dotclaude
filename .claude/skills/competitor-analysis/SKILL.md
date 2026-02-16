---
name: competitor-analysis
description: Research competitors, analyze user feedback from reviews/forums/social media, and identify market gaps. Use when the user wants competitive analysis, market research, or product positioning insights.
user_invocable: true
---

# Competitor Analysis Skill

You are performing a comprehensive competitor analysis. This skill uses WebSearch to research competitors, analyze real user feedback, and produce a structured markdown report identifying market gaps and strategic opportunities.

## Argument Handling

This skill expects three arguments in the format:
```
/competitor-analysis "ProductName" "product type" "target audience"
```

**Examples:**
- `/competitor-analysis "Figma" "design tool" "UI/UX designers"`
- `/competitor-analysis "Linear" "project management tool" "engineering teams"`
- `/competitor-analysis "Auto Claude" "autonomous coding tool" "software developers"`

**If any arguments are missing or unclear**, use `AskUserQuestion` to collect them before proceeding. All three are required:

1. **Product Name** — The product being analyzed (your product or a product you're researching)
2. **Product Type** — The category/market (e.g., "design tool", "CI/CD platform", "note-taking app")
3. **Target Audience** — Who uses this type of product (e.g., "frontend developers", "product managers")

Parse the arguments from the user's input. If the user provides them inline (e.g., `/competitor-analysis "Slack" "team messaging" "remote teams"`), extract them directly. If ambiguous, ask.

## Research Procedure

Execute these four phases sequentially. Use `WebSearch` for all research. Make parallel WebSearch calls within each phase where possible to maximize efficiency.

---

### Phase 1 — Identify Competitors

**Goal:** Find 3-5 direct competitors in the same market category.

Run 3-4 WebSearch calls (in parallel):

1. `"{product type} alternatives 2026"` — finds alternative products
2. `"best {product type} tools"` — finds top-rated products in the category
3. `"{product type} vs"` — finds common comparison queries
4. `"{product name} competitors"` — finds direct competitor mentions

**After collecting results:**
- Select the 3-5 most relevant, direct competitors
- Prioritize competitors that serve the same target audience
- Exclude tangentially related products (e.g., if analyzing a "design tool", exclude general project management tools unless they directly compete)
- If fewer than 3 competitors are found, broaden search terms (e.g., search for the broader category)

**Output to yourself:** List of competitors with a one-line description of each.

---

### Phase 2 — Research User Feedback

**Goal:** For each competitor, find real user pain points, complaints, and missing features.

For each competitor, run 2-3 WebSearch calls (parallelize across competitors):

1. `"{competitor name} reviews complaints problems"` — general review sentiment
2. `"{competitor name} reddit issues site:reddit.com"` — Reddit discussions and complaints
3. Choose one based on product type:
   - For developer tools: `"{competitor name} issues site:github.com"` — GitHub issues and bug reports
   - For consumer/SaaS products: `"{competitor name} app store reviews complaints"` — app store feedback
   - For B2B tools: `"{competitor name} G2 reviews problems"` — enterprise review sites

**For each competitor, extract:**
- **Pain points** — What do users consistently complain about?
- **Missing features** — What do users wish the product had?
- **UX complaints** — What's frustrating about the user experience?
- **Performance issues** — Speed, reliability, scalability problems
- **Pricing complaints** — Cost concerns, value perception

**Cite sources** — For each pain point, note where it came from (Reddit, GitHub, review site, forum, etc.).

---

### Phase 3 — Market Gap Analysis

**Goal:** Cross-reference pain points to find patterns and opportunities. No additional searches needed.

Analyze the collected data:

1. **Cross-reference pain points** — Which complaints appear across multiple competitors?
2. **Identify unserved needs** — What problems does no competitor solve well?
3. **Find differentiation opportunities** — Where could a new entrant or the analyzed product stand out?
4. **Assess severity** — Rank gaps by how frequently and passionately users mention them
5. **Map to audience** — Which gaps matter most to the target audience?

Classify each gap as:
- **Critical** — Mentioned by many users across multiple competitors, high frustration
- **Significant** — Common complaint but workarounds exist
- **Emerging** — Growing concern, mentioned in recent discussions

---

### Phase 4 — Generate Report

Write a comprehensive markdown report following the template below. Save it to `competitor-analysis-report.md` in the current working directory using the `Write` tool.

After writing, inform the user that the report has been saved and provide a brief summary of the key findings.

---

## Report Template

Use this exact structure for the output report:

```markdown
# Competitor Analysis: {Product Name}

**Date:** {current date}
**Product Type:** {product type}
**Target Audience:** {target audience}

---

## Executive Summary

{2-3 paragraph overview of the competitive landscape. Include: number of competitors analyzed, the most critical market gaps found, and the single biggest opportunity for differentiation. This should be actionable — a product leader should be able to read just this section and understand the key takeaway.}

---

## Competitor Profiles

### {Competitor 1 Name}

**Overview:** {1-2 sentence description of what they do and their market position}

**Strengths:**
- {strength 1}
- {strength 2}
- {strength 3}

**User Pain Points:**

| Pain Point | Severity | Source | Opportunity |
|-----------|----------|--------|-------------|
| {description} | Critical/Significant/Emerging | {Reddit/GitHub/G2/etc.} | {how this could be addressed} |
| {description} | ... | ... | ... |

---

### {Competitor 2 Name}
{same structure as above}

---

### {Competitor 3 Name}
{same structure as above}

---

{Continue for each competitor analyzed}

---

## Market Gaps

{Overview paragraph explaining the gap analysis methodology and key patterns.}

### Gap 1: {Gap Title}

- **Description:** {what's missing or broken across the market}
- **Affected Competitors:** {which competitors have this problem}
- **Severity:** Critical / Significant / Emerging
- **User Evidence:** {specific quotes or paraphrased feedback with sources}
- **Opportunity Size:** High / Medium / Low
- **Suggested Approach:** {brief idea for how to address this gap}

### Gap 2: {Gap Title}
{same structure}

### Gap 3: {Gap Title}
{same structure}

{Continue for each identified gap}

---

## Strategic Insights

### Top Pain Points by Frequency
1. {most common pain point across all competitors} — mentioned by {X} competitors
2. {second most common} — mentioned by {X} competitors
3. {third most common} — mentioned by {X} competitors

### Key Differentiators to Pursue
- **{differentiator 1}:** {why this matters and how to execute}
- **{differentiator 2}:** {why this matters and how to execute}
- **{differentiator 3}:** {why this matters and how to execute}

### Market Trends
- {trend 1 observed from research}
- {trend 2 observed from research}
- {trend 3 observed from research}

### Recommended Next Steps
1. {actionable recommendation 1}
2. {actionable recommendation 2}
3. {actionable recommendation 3}

---

## Research Metadata

**Queries Used:**
{list all WebSearch queries executed during research}

**Sources Consulted:**
{list key URLs and sources referenced}

**Limitations:**
{note any gaps in research — limited results for certain competitors, paywalled content, regional bias, etc.}

**Methodology:**
Competitive analysis performed via web research using Claude Code's WebSearch tool. User feedback sourced from public forums, review sites, and developer communities. Pain points validated by cross-referencing across multiple independent sources.
```

---

## Edge Cases

Handle these scenarios gracefully:

### No Competitors Found
If searches return no clear competitors:
- Frame this as a **first-mover opportunity**
- Search for adjacent categories or broader market segments
- Look for indirect competitors (different approach to the same problem)
- Note this in the report's Executive Summary

### Limited Search Results
If search results are sparse for a competitor:
- Document the limitation in the report
- Continue analysis with available data
- Note confidence level for that competitor's analysis (Low/Medium/High)
- Try alternative search queries before giving up

### Internal/Niche/Developer Tools
For tools that aren't widely reviewed:
- Search GitHub issues and discussions: `"{tool} site:github.com"`
- Search StackOverflow: `"{tool} site:stackoverflow.com"`
- Search Hacker News: `"{tool} site:news.ycombinator.com"`
- Search for comparison blog posts and technical reviews

### Partial Search Failures
If some WebSearch calls fail or return errors:
- Continue with successful results
- Note which searches failed in Research Metadata
- Do not halt the entire analysis — partial data is still valuable

### Very Crowded Markets
If there are many competitors (>10 found):
- Focus on the top 5 by market presence and relevance to the target audience
- Mention additional competitors briefly in the Executive Summary
- Prioritize competitors the target audience is most likely using

---

## Important Guidelines

- **Be objective** — Report facts from user feedback, not opinions. Cite sources.
- **Be specific** — "Users complain about slow performance" is weak. "Multiple Reddit threads report 10+ second load times for large projects (r/competitor, 2025)" is strong.
- **Prioritize recency** — Weight recent feedback (2024-2026) more heavily than older complaints that may be resolved.
- **Include positive signals** — Note what competitors do well, not just their failures. Understanding strengths is as important as finding gaps.
- **Stay in scope** — Research the product type and audience specified. Don't expand scope without asking.
- **Always save the report** — The final deliverable is `competitor-analysis-report.md` written to the current directory.
