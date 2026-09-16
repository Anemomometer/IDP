# UI PRD — Clinical Trial NLP
### Analytics Dashboard & Review Interface
**Patent Reference:** US20250252261A1
**Version:** 1.0

---

## 1. Purpose

This document specifies the user-facing dashboard for the Clinical Trial NLP system — the screens, components, interactions, and states a researcher/reviewer will use to search PubMed, inspect extracted evidence, review/correct extractions, and export results.

**Primary user:** a researcher or clinical reviewer with domain knowledge but not necessarily an ML background. The UI must make model output (entities, relations, assertions, confidence scores) understandable at a glance and easy to verify or correct.

---

## 2. User Goals

- Search or ingest PubMed abstracts relevant to a topic.
- Quickly see what entities/relations/assertions were extracted from each abstract, in context.
- Trust or distrust an extraction based on a visible confidence score.
- Correct a wrong extraction with minimal friction.
- Search/filter across the whole accumulated evidence base (not just one abstract).
- Export a filtered set of evidence records for use elsewhere.

---

## 3. Information Architecture / Screens

1. Ingest / Search
2. Abstract Detail (Highlighted Text + Extractions)
3. Relation View
4. Evidence Database (Search & Filter table)
5. Review Queue (Human-in-the-loop correction)
6. Evaluation Dashboard (P/R/F1, confusion matrix)

---

## 4. Screen 1: Ingest / Search

**Purpose:** Entry point. User pulls new abstracts into the system or revisits prior queries.

**Components:**
- Search bar: free-text query (e.g., "metformin AND type 2 diabetes") submitted to the PubMed API.
- "Fetch Abstracts" button — triggers ingestion pipeline; shows a loading state ("Fetching abstracts...", "Running extraction...").
- Recent queries list (chips/tags), clickable to re-run.
- Result count summary once ingestion completes (e.g., "12 new abstracts processed, 3 already in database").
- Each processed abstract shown as a card: title, PMID, snippet, "View Extractions" button linking to Screen 2.

**States:**
- Empty state (no queries yet) — short explainer + example query.
- Loading state — progress indicator, non-blocking if possible.
- Error state — PubMed API failure or rate limit, with retry option.

---

## 5. Screen 2: Abstract Detail (Inline Highlighting)

**Purpose:** Core review surface. Shows the raw abstract text with extracted entities/relations highlighted inline, so a user can verify extractions in their original context.

**Components:**
- Abstract header: title, PMID, publication metadata.
- Full abstract text rendered with inline color-coded highlights:
  - Disease → color A (e.g., blue)
  - Drug → color B (e.g., green)
  - Sample Size → color C (e.g., orange)
  - Endpoint → color D (e.g., purple)
- Assertion indicator overlay on relation-bearing spans:
  - **Positive** — solid underline / checkmark icon
  - **Negated** — strikethrough or "no" icon, red accent
  - **Conditional** — dashed underline / "if" icon, amber accent
- Hover/click on any highlighted span → tooltip/popover showing:
  - Entity type or relation type
  - Confidence score (numeric + small bar)
  - Quick actions: Approve / Correct / Reject
- Sidebar panel: list of all entities and relations extracted from this abstract, mirroring the inline highlights, for users who prefer a list view over reading highlighted prose.
- Legend: fixed color key for entity types and assertion states, always visible or one click away.

**Interaction notes:**
- Highlighting must not obscure readability of the underlying text (use subtle background highlight + colored underline, not solid blocks).
- Confidence score should be visually encoded (e.g., highlight opacity or a small badge) in addition to the numeric value, so low-confidence extractions are visually distinguishable at a glance.

---

## 6. Screen 3: Relation View

**Purpose:** Abstract away raw text and show extracted relationships directly, useful for scanning many findings quickly.

**Components:**
- Table or card list of relations for the current abstract (or across a filtered set, see Screen 4):

  | Subject Entity | Relation Type | Object Entity | Assertion | Confidence | Source Abstract |
  |---|---|---|---|---|---|

- Optional graph/node view (stretch goal): entities as nodes, relation type as labeled edges, assertion status as edge color/style.
- Filter chips at top: filter by relation type, assertion type, minimum confidence.

**Interaction notes:**
- Clicking a row jumps back to Screen 2 with the corresponding span scrolled into view and highlighted.

---

## 7. Screen 4: Evidence Database (Search & Filter)

**Purpose:** Query the full accumulated evidence base across all ingested abstracts, not just one at a time.

**Components:**
- Filter panel:
  - Drug (text/autocomplete)
  - Disease (text/autocomplete)
  - Relation type (multi-select)
  - Assertion type (multi-select: Positive/Negated/Conditional)
  - Confidence threshold (slider, e.g., min 0.0–1.0)
  - Review status (Unreviewed / Approved / Corrected / Rejected)
- Results table: same columns as Relation View, sortable by any column, paginated.
- "Export" button — exports current filtered view as CSV or JSON.
- Row count / summary bar (e.g., "184 relations match your filters").

**Interaction notes:**
- Filters should combine with AND logic; show active filters as removable chips above the table.
- Empty results state should suggest loosening filters.

---

## 8. Screen 5: Review Queue (Human-in-the-Loop)

**Purpose:** Dedicated workflow for reviewers to work through unreviewed or low-confidence extractions systematically, rather than only reviewing incidentally while browsing.

**Components:**
- Queue list, default sorted by lowest confidence first (surfacing the extractions most likely to need correction).
- Each queue item shows: abstract snippet with the relevant span highlighted, extracted type/relation/assertion, confidence score.
- Action buttons per item:
  - **Approve** (confirms extraction as-is)
  - **Correct** (opens inline edit: change entity type, relation type, or assertion label; free-text override for the span if needed)
  - **Reject** (marks extraction as invalid/removes it from trusted evidence)
- Bulk actions: "Approve all above X% confidence" (optional convenience action, used carefully).
- Progress indicator: "42 of 210 reviewed this session."

**Interaction notes:**
- Every action here writes to the `review_log` (see Technical PRD, Section 5) with reviewer identity and timestamp.
- Corrected extractions should be visually distinguished from model-original extractions elsewhere in the UI (e.g., a small "edited" tag).

---

## 9. Screen 6: Evaluation Dashboard

**Purpose:** Show model performance for project reporting/demo purposes (not a daily-use screen for end reviewers, but needed for milestone reporting and the final demo/viva).

**Components:**
- Task selector tabs: NER | Relation Extraction | Assertion Detection
- Confusion matrix visualization per task.
- Table of per-class Precision/Recall/F1.
- Macro-averaged P/R/F1 summary metric cards at top.
- Version/date of the evaluation run (to compare across milestones: Core NLP → Integrated System → Complete App → Final Project).

---

## 10. Visual Design Guidelines

- Color coding must be colorblind-safe (avoid relying on red/green alone to distinguish assertion status — pair color with icon/pattern, e.g., checkmark/strikethrough/dashed-line as done in Screen 2).
- Confidence scores always shown numerically, never color/opacity alone, for accessibility and precision.
- Consistent legend/key present on any screen that uses the color coding (Screens 2 and 3 minimum).
- Typography: clear hierarchy between abstract body text (readable, larger line-height) and UI chrome/metadata (smaller, secondary color) so highlighted extractions don't compete visually with dense scientific prose.
- Loading and error states defined for every screen that depends on an external call (PubMed ingestion, model inference, export).

---

## 11. Key User Flows

**Flow A — New Search to Verified Evidence**
1. User enters query on Screen 1, clicks Fetch.
2. Pipeline ingests + processes abstracts.
3. User opens an abstract (Screen 2), reviews highlighted spans.
4. User approves/corrects extractions inline.
5. Approved evidence now appears as "reviewed" in Screen 4 filters.

**Flow B — Systematic Review Session**
1. User opens Review Queue (Screen 5).
2. Works through lowest-confidence items first.
3. Approves/corrects/rejects each.
4. Session progress tracked; queue shrinks over time.

**Flow C — Evidence Lookup for a Specific Question**
1. User goes to Evidence Database (Screen 4).
2. Filters by Drug = "X", Assertion = "Positive", min confidence 0.7.
3. Reviews resulting relation rows.
4. Exports filtered set for external use (e.g., a literature review document).

---

## 12. Acceptance Criteria (UI)

- A user can go from entering a search query to seeing color-coded highlighted extractions in an abstract without leaving the app.
- A user can identify, without reading a tooltip, which color corresponds to which entity type (legend always accessible).
- A user can distinguish a positive, negated, and conditional finding visually, not just via a raw label.
- A user can filter the evidence database by at least drug, disease, assertion type, and confidence, and export the results.
- A user can correct a wrong extraction in 3 clicks or fewer from the abstract detail view.
