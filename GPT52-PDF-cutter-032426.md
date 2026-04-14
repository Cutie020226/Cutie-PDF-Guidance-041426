# Technical Specification — FDA 510(k) Review Studio v2.9  
## Regulatory Command Center: **Nordic WOW Edition (Painter Studio + Note Keeper)**

**Deployment Targets (2026-ready):**  
- **Primary:** Hugging Face Spaces (Streamlit)  
- **Secondary:** Localized enterprise container environments (air-gapped capable)

**Core Purpose:**  
A hyper-efficient, agentic, human-in-the-loop workspace that accelerates end-to-end review of complex FDA-style 510(k) submissions—spanning multi-document ingestion, advanced interactive PDF trimming, OCR/structured extraction, agent orchestration (agents.yaml), embedded regulatory datasets, and a comprehensive observability suite—while maintaining a calming Nordic UX.

**What’s new in v2.9 (while preserving all original v2.8 features):**  
1. **New WOW UI system**: Light/Dark themes, English/Traditional Chinese, plus **20 painter-inspired styles** with a **Jackpot randomizer**.  
2. **WOW visualization upgrades (3 new)**: **WOW Interactive Indicator**, **Live Log**, **WOW Interactive Dashboard**.  
3. **Credential UX upgrade**: Users can input API keys in-app **only when missing from environment**; keys are masked and never exposed if env keys exist.  
4. **Agent run control**: Before executing each agent, users can modify prompt, max tokens (**default 12,000**), and model (including specified OpenAI/Gemini/Anthropic/Grok choices). Users can edit each agent’s output (Text/Markdown) before feeding the next agent.  
5. **New tab: AI Note Keeper**: Paste text/markdown → transform into organized markdown → edit in Text/Markdown view → run “Keep Prompt on the Note” (model-selectable) or use **AI Magics** (6 features including keyword highlighting with color choice).  
6. **Three additional WOW AI features (new)** added to the WOW module suite (for a total of **8** WOW modules).

---

## 1. Executive Summary

FDA 510(k) Review Studio v2.9 extends v2.8’s core strengths—granular PDF trimming with multiple engines, direct multimodal prompting against cut documents, sequential agent orchestration with editable handoffs, macro summary generation, and the WOW AI module suite—by introducing **aesthetic personalization without sacrificing regulatory rigor**, and by significantly upgrading **observability and “operator confidence” tooling**.

In real review settings, the reviewer’s success depends on two simultaneous capabilities:

1. **Microscopic control**: precise page-level isolation, evidence anchoring, labeling claim verification, contradiction detection, and gap discovery.
2. **Macroscopic situational awareness**: understanding which step is running, what changed, what failed, what it cost, and what remains incomplete—without hunting through logs or guessing context.

v2.9 meets these needs via three “WOW visualization” features:  
- **WOW Interactive Indicator** (high-signal pipeline state and health)  
- **Live Log** (streaming, filterable, exportable operational and reasoning trace)  
- **WOW Interactive Dashboard** (token/cost/latency/risk/completeness coverage cockpit)

Finally, v2.9 introduces **AI Note Keeper**, enabling reviewers to rapidly normalize messy notes, meeting minutes, and ad hoc findings into structured markdown, then refine and enhance them with six AI Magics. This reduces “lost work” and bridges the gap between formal output artifacts and the reviewer’s ongoing thinking.

---

## 2. Expanded Design Goals & Explicit Non-Goals

### 2.1 Primary Design Goals
**G1 — Time-to-first-insight reduction:**  
Enable reviewers to ingest large, chaotic submission sets and reach defensible insights quickly through trimming, direct document prompting, and fast agent runs.

**G2 — Human-in-the-loop at every critical boundary:**  
- Users control page selection, OCR strategy, prompt instructions, model choice, token limits, and agent handoffs.  
- Users can edit agent output before it becomes downstream input.

**G3 — Traceability and defensibility by default:**  
Every claim should map back to a file/page anchor wherever possible, and dashboards should surface “unanchored” risk.

**G4 — Provider agility with consistent execution contract:**  
Support Gemini, OpenAI, Anthropic, Grok with normalized behavior across a unified orchestration system.

**G5 — Calm, localized, and aesthetic UI without reducing clarity:**  
Nordic design remains the baseline, augmented by painter styles as optional “skins” that do not change information architecture.

**G6 — Operational transparency:**  
Users should always know: what’s running, what finished, what failed, how much it cost, how long it took, and what data artifacts were produced.

### 2.2 Strict Non-Goals
- Not a legally binding FDA determination system; outputs are advisory.  
- Not a persistent multi-user RAG/vector database platform by default (session-ephemeral processing remains the standard).  
- Not a long-term PHI/proprietary hosting solution; session purge and minimal retention are core.

---

## 3. System Architecture Overview (v2.9)

### 3.1 High-Level Layers
1. **WOW UI + Nordic Painter Studio Layer**  
2. **Ingestion + Queue + Trimming Layer (5 engines)**  
3. **Direct Document Prompting Layer (cut-PDF multimodal)**  
4. **OCR Matrix + Consolidation Layer**  
5. **Agent Orchestration Layer (agents.yaml; step-by-step execution)**  
6. **Macro Summary Engine (3,000–4,000 words target)**  
7. **WOW AI Module Suite (8 modules total)**  
8. **Embedded Datasets + Unified Search Layer**  
9. **Observability Layer (3 WOW visualization features + exportable logs)**  
10. **Security & Credential Broker Layer (env-first; masked fallback inputs)**

### 3.2 Session & Artifact Model (Ephemeral-first)
Artifacts are session-scoped objects with explicit lifecycle states:

- **Raw Upload Artifact** (original PDFs)  
- **Trim Specification** (page ranges + engine choice)  
- **Cut PDF Artifact** (downloadable)  
- **Extracted Text Artifact(s)** (OCR/text extraction results)  
- **Consolidated Master Artifact** (with anchors)  
- **Agent Outputs** (versioned; editable)  
- **Macro Summary Versions** (version history)  
- **WOW Module Outputs** (tables, flags, dashboards)  
- **Note Keeper Notes** (structured markdown, versions, enhancements)

By default, all artifacts are cleared on session termination or user-triggered purge.

---

## 4. WOW UI: Nordic Painter Studio (Themes, Language, 20 Styles + Jackpot)

### 4.1 Global UI Controls (Persistent Header)
- **Theme Toggle:** Light / Dark  
- **Language Toggle:** English / Traditional Chinese (繁體中文)  
- **Painter Style Selector:** 20 presets (optional skin)  
- **Jackpot Style Button:** random selection of painter style with animation and “lock-in” confirmation  
- **Accessibility Quick Toggles:** font size scaling, contrast boost, reduced motion

All UI toggles must **not** change underlying document content, anchors, or model outputs unless explicitly requested (e.g., “AI output language preference”).

### 4.2 Localization Requirements
- UI strings fully localized EN / zh-TW (menus, tooltips, errors, confirmations).  
- Date/time formatting localized (ISO standard optional).  
- **AI Output Language Preference (separate from UI):**  
  - Auto (default)  
  - English  
  - Traditional Chinese  
This preference injects a standardized instruction into model calls, without translating source documents.

### 4.3 Painter-Inspired Style Presets (20)
These are **inspired** palettes/typography/motion profiles (not copying artworks). Each preset defines: background surfaces, accent color, chart palette, and button style.

1. Monet Mist  
2. Van Gogh Vivid Night  
3. Hokusai Wave Blue  
4. Klimt Gilded Calm  
5. Picasso Minimal Line  
6. Dali Surreal Sand  
7. Kandinsky Geometry Pop  
8. Rothko Deep Fields  
9. Vermeer Quiet Pearl  
10. Turner Atmospheric Gold  
11. Cézanne Structured Earth  
12. Matisse Cutout Bright  
13. Pollock Speckle Neutral  
14. Rembrandt Ember Shadow  
15. Frida Botanical Jewel  
16. Magritte Sky Paradox  
17. Chagall Dream Indigo  
18. Edward Hopper Still Noon  
19. Georgia O’Keeffe Desert Bloom  
20. Ukiyo-e Ink Wash

**Jackpot Mode:**  
- “Jackpot tokens” are a purely UI-level playful mechanic (no gambling, no money).  
- User can click Jackpot to randomize style; option to “pin” current style for session.  
- Jackpot respects accessibility (“reduced motion” disables spinning/animated transitions).

---

## 5. WOW Visualizations (3 New Features)

### 5.1 WOW Interactive Indicator (Pipeline Health + Stage)
A compact, always-visible status component (top strip or right-side rail) that provides:

- **Current Stage:** Ingestion / Trimming / OCR / Consolidation / Agent N / Macro Summary / WOW Module / Export  
- **Health Signals:** provider connectivity, credential readiness, memory pressure, token pressure  
- **Actionable Micro-Controls:** pause streaming, cancel current call, retry last step, open Live Log filtered to current step  
- **Evidence Integrity Gauge:** percentage of summary claims currently anchor-mapped vs unanchored (updates after Evidence Mapping runs)

Design: minimal, high-legibility, semantic colors strictly enforced (error red, warning amber, success green, regulatory deficiency coral).

### 5.2 Live Log (Streaming Operational + Reasoning Trace)
A dedicated panel/tab that displays real-time events:

**Log types (filterable):**
- System events (file upload, trim executed, artifacts created)  
- Provider events (request started, latency, timeouts, retries)  
- Token/cost events (estimated tokens, completion tokens, cost estimate)  
- Agent events (agent start/end, model used, max tokens, temperature)  
- Safety events (blocked content, policy refusal summaries)  
- Redaction events (confirmation that secrets were masked)

**Live Log behaviors:**
- Streaming append (no UI freeze)  
- Severity filters: Debug / Info / Warning / Error / Critical  
- Artifact pointer links: click a log line to open the artifact snapshot produced at that moment  
- Export: sanitized log export (no keys, no raw secrets)

### 5.3 WOW Interactive Dashboard (Mission Control 2.0)
A cockpit-style dashboard combining operational and regulatory readiness signals:

**Panels:**
- **Pipeline Timeline:** clickable nodes (trim → OCR → agent outputs → summary versions)  
- **Token & Cost Monitor:** by provider, by agent, by document prompting session  
- **Latency Monitor:** p50/p95 per provider/model  
- **Coverage & Completeness:**  
  - % pages trimmed vs retained  
  - OCR success ratio  
  - evidence anchor coverage  
  - checklist pass/fail counts (Gatekeeper output)  
- **Risk Radar Visualization:** from Regulatory Risk Radar module  
- **Inconsistency Heatmap:** contradictions by section (intended use, labeling, dimensions, sterilization, software)  
- **Export Readiness Score:** indicates whether required artifacts exist for audit bundle

Dashboard design must remain Nordic: minimal clutter, strong spacing, high contrast text, restrained color usage.

---

## 6. Credential Management (Env-first, UI fallback, non-disclosure)

### 6.1 Credential Broker Rules
- **Primary source:** environment variables/secrets provided by Hugging Face Spaces or enterprise container secrets.  
- **Fallback:** in-app user entry **only when env keys are missing**.

### 6.2 UX Requirements
- If env key exists for a provider:  
  - The UI shows provider as “Connected via Environment”  
  - **No input field is displayed** (prevent shoulder-surfing and accidental exposure)
- If env key is missing:  
  - Show masked input field (“Enter API key for this session”)  
  - Key is stored in **volatile session memory only**  
  - Never written to disk, logs, exports, or config files  
  - “Clear credentials” button removes session keys immediately

### 6.3 Providers
- Gemini API (emphasis: gemini-2.5-flash, gemini-2.5-flash-lite, gemini-3-flash-preview)  
- OpenAI API (gpt-4o-mini, gpt-4.1-mini)  
- Anthropic API (selectable Anthropic models; admin may whitelist specific model IDs)  
- Grok API (grok-4-fast-reasoning, grok-3-mini)

---

## 7. Ingestion, Queue, Trimming, and Export (Preserved + Enhanced)

### 7.1 Upload Protocol (Preserved)
- Drag-and-drop multi-PDF upload  
- Pre-flight checks: page count, encryption detection, corruption hints, xref sanity  
- Staged registry table with metadata

### 7.2 Interactive Trimming (Preserved)
- Range syntax: supports complex page selections  
- Visual page preview (as available within resource constraints)  
- Choose one of **five trimming engines** (as defined in v2.8 spec) with contextual guidance

### 7.3 Download Cut PDF (Preserved)
- After trimming, user can download cut artifact instantly  
- Optional: include a “chain-of-custody metadata page” as an admin-configurable setting (off by default to avoid altering source reproduction expectations)

---

## 8. Direct Document Prompting Layer (Preserved + Integrated with WOW Visuals)

### 8.1 Persistent Prompt on Cut Document (Preserved)
- Dual-pane: document renderer + prompt workspace  
- Model selection optimized for Gemini multimodal use cases  
- “Skill description” editable; default regulatory skill provided

### 8.2 New Enhancements
- Live Log automatically tags events as “Doc Prompting Session”  
- Dashboard shows token/cost/latency for document prompting separate from agents  
- Output can be saved as:  
  - Note Keeper entry  
  - Agent pre-input snippet  
  - Evidence snippet pinned to a page anchor

---

## 9. OCR Matrix and Consolidation (Preserved)

### 9.1 OCR Paths
- Embedded text extraction first  
- Fallback OCR for scanned pages  
- Optional AI-assisted extraction templates (narrative/table/labeling)

### 9.2 Anchor Injection (Preserved)
- Stable tags: filename, document ID, original page number  
- Anchors are immutable and used by Evidence Mapping

---

## 10. Agent Orchestration (agents.yaml) — Step-by-Step Editable Execution

### 10.1 Configuration Source
- agents.yaml defines ordered agents with:  
  - agent id/name  
  - provider  
  - model id  
  - system instructions  
  - user instructions  
  - temperature  
  - max tokens (default configurable; per agent override allowed)

### 10.2 Per-Agent Pre-Run Override (New Requirement)
Before running each agent, user can modify:

- **Prompt:** system and/or user prompt (with template helper)  
- **Max tokens:** default **12,000** (warn if model limits lower)  
- **Model:** choose from approved list:  
  - gpt-4o-mini, gpt-4.1-mini  
  - gemini-2.5-flash, gemini-2.5-flash-lite, gemini-3-flash-preview  
  - anthropic models (whitelisted)  
  - grok-4-fast-reasoning, grok-3-mini

The UI must display compatibility warnings (context window, tool limits, streaming support).

### 10.3 Editable Handoff (Enhanced)
After an agent completes:

- Output is shown in a dual toggle: **Text view** / **Markdown view**  
- User can edit directly (remove hallucinations, add commentary, reformat)  
- User must explicitly click **“Commit as Next Input”** to pass forward  
- The system stores both:  
  - raw model output (read-only snapshot)  
  - user-edited committed output (becomes downstream input)

### 10.4 Agent Run Observability
- WOW Interactive Indicator shows current agent, status, and token pressure  
- Live Log records parameters (model, max tokens, temperature, retries)  
- Dashboard summarizes costs and latency per agent

---

## 11. Macro Summary Generation Engine (Preserved)

- Produces 3,000–4,000 word structured FDA-style summary  
- Persistent revision: version history, compare versions, rollback  
- Revisions can be prompted in EN or zh-TW based on AI Output Language Preference

---

## 12. WOW AI Module Suite (Now 8 Modules)

### 12.1 Original 5 Modules (Preserved)
1. **Evidence Mapping System** — maps claims to anchors, flags unsupported claims  
2. **Consistency Guardian** — detects contradictions across sections/docs  
3. **Regulatory Risk Radar** — scores likely pain points, radar visualization  
4. **Completeness Heuristic Gatekeeper** — RTA-style checklist status  
5. **Labeling and Claims Inspector** — extracts claims and checks support strength

### 12.2 Three Additional WOW AI Features (New)
These are designed to be high-impact, regulator-aligned, and evidence-oriented.

#### 6) Predicate Comparison Matrix Builder (WOW-Predicate Matrix)
**Goal:** reduce time spent building equivalence arguments.  
**Inputs:** consolidated artifact, extracted device characteristics, embedded clearance datasets (if available), user-provided predicate names (optional).  
**Outputs:**  
- Candidate predicate shortlist (with confidence and reasons)  
- Side-by-side matrix: indications, technology, materials, energy source, sterility, biocomp endpoints, software level of concern, performance tests  
- “Equivalence Weak Points” flags (where data is missing or mismatched)  
**Visualization:** matrix view + highlighted deltas.

#### 7) Standards & Guidance Crosswalk (WOW-Standards Crosswalk)
**Goal:** make consensus standards usage auditable and gap-visible.  
**Outputs:**  
- Extracted list of cited standards and guidance documents  
- For each: where cited (anchors), what claims rely on it, and whether test evidence appears present  
- Flags: outdated versions, missing declarations, ambiguous test conditions  
**Dashboard hooks:** increases Export Readiness Score when complete.

#### 8) Test Coverage Gap Analyzer (WOW-Test Gaps)
**Goal:** reveal missing verification/validation coverage.  
**Outputs:**  
- Expected test domains inferred from device type/claims (software, EMC, biocomp, sterilization, shelf life, packaging, usability, cybersecurity)  
- Evidence present vs absent with anchor links  
- Severity scoring and “next questions to ask sponsor” suggestions  
**Visualization:** coverage bar chart + severity table.

---

## 13. AI Note Keeper (New Tab)

### 13.1 Primary Workflow
1. User pastes **text or markdown** into an input panel.  
2. System transforms into **organized markdown** with:  
   - title  
   - summary  
   - key findings  
   - open questions  
   - evidence snippets  
   - action items  
   - decision log (optional)  
3. User edits in **Text view / Markdown view** (toggle).  
4. User can either:  
   - **Keep Prompt on the Note** (persistent chat-like refinement)  
   - Apply **AI Magics** (one-click transformations)

### 13.2 “Keep Prompt on the Note”
- Model selection identical to agent selector  
- Supports iterative refinement while preserving version snapshots  
- Can export note into the main pipeline as:  
  - agent input seed  
  - macro summary appendix  
  - audit bundle attachment

### 13.3 AI Magics (6 Features; includes keyword color)
1. **AI Formatting (Regulatory Markdown)**  
   - Normalizes headings, numbering, tables, and consistent terminology.

2. **AI Keywords Highlighter (Color-Selectable)**  
   - User enters keywords or phrases  
   - User selects highlight color (from accessible palette)  
   - Output adds consistent markup conventions (and a legend) to highlight occurrences.

3. **AI Executive Brief (1-page)**  
   - Generates a concise brief: what matters, risks, missing evidence, recommended next steps.

4. **AI Action Items & Questions Generator**  
   - Produces sponsor questions, reviewer tasks, and a checklist of follow-ups.

5. **AI Terminology Harmonizer (EN/zh-TW aware)**  
   - Normalizes device names, abbreviations, and translations across the note set.

6. **AI Evidence-to-Note Binder**  
   - Converts pasted evidence snippets into a structured “quote → interpretation → risk → anchor placeholder” format to improve defensibility.

### 13.4 Note Keeper Storage & Export
- Session-scoped by default  
- Export options: markdown file, or inclusion in audit bundle  
- Optional enterprise mode: secure volume storage with retention policies

---

## 14. Embedded Datasets, Search, Holistic Device View (Preserved)

- Unified fuzzy search across: clearance records, adverse events, UDI, recalls  
- Holistic device view dashboard remains available and can now feed:  
  - Predicate Matrix Builder  
  - Risk Radar calibration  
  - Standards Crosswalk suggestions

---

## 15. Security, Privacy, and Reliability Contracts (Enhanced)

### 15.1 Key Protections
- Env-first key sourcing; UI fallback masked; never logged  
- Session purge destroys: PDFs, cut PDFs, OCR text, consolidated artifacts, agent outputs, summaries, notes, logs (unsanitized), and session credentials

### 15.2 Redaction and Safe Logging
- Live Log is sanitized by design  
- Export logs are sanitized and reviewed for:  
  - credentials  
  - raw secrets  
  - accidental prompt injection strings that include sensitive data

### 15.3 Reliability
- Preflight verification before expensive steps  
- Retry policies per provider (bounded retries)  
- Partial progress preservation and resumable steps  
- Low-resource mode for Hugging Face constraints:  
  - lower preview resolution  
  - page caps per trim operation  
  - automatic model downgrades when user approves

---

## 16. Deployment Specification (Hugging Face Spaces + Enterprise)

### 16.1 Packaging & Configuration
- Streamlit app as single cohesive UI  
- agents.yaml stored in repo with canonical defaults  
- Provider secrets managed via HF Spaces secrets or enterprise secret manager  
- Optional “admin policy file” controlling:  
  - model whitelist  
  - maximum file sizes  
  - maximum pages per session  
  - log verbosity  
  - retention mode (ephemeral vs persistent)

### 16.2 Observability in HF Spaces
- Live Log designed to avoid UI blocking (streaming append)  
- Dashboard caches computed aggregates to reduce recomputation overhead

---

## 17. Acceptance Criteria (v2.9)

The system is ready when:

1. Light/Dark themes function across all tabs without layout breakage.  
2. English/Traditional Chinese localization covers UI strings, errors, tooltips.  
3. 20 painter styles apply cleanly without reducing legibility; Jackpot randomizer works and respects reduced motion.  
4. WOW Interactive Indicator shows correct stage/health and links into logs.  
5. Live Log streams events, filters correctly, exports sanitized logs.  
6. WOW Interactive Dashboard displays timeline, cost/latency, risk and completeness signals.  
7. Credential broker behavior is correct: env keys hide input; missing env keys prompt masked session entry only.  
8. Ingestion, trimming (5 engines), and cut PDF download work as in v2.8.  
9. Direct document prompting works with Gemini models and produces saved outputs.  
10. Agent execution is sequential and editable: user can modify prompt/model/max tokens before each run; user can edit outputs in Text/Markdown view and commit to next agent.  
11. Macro summary generates 3,000–4,000 words and supports versioned revision prompts.  
12. WOW modules include original 5 + new 3, with outputs visible and exportable.  
13. AI Note Keeper transforms pasted content into organized markdown, supports Text/Markdown editing, “Keep Prompt,” and all 6 AI Magics including keyword highlight with color selection.  
14. Total purge irreversibly clears artifacts and session credentials.

---

## Appendix — 20 Comprehensive Follow-up Questions

1. For the 20 painter-inspired styles, do you want them applied **only to UI chrome** (backgrounds/buttons/charts), or should they also affect **document rendering frames and annotation colors** (while preserving readability)?  
2. Should Jackpot mode be purely random, or should it support **weighted randomness** (e.g., prefer high-contrast styles in dark theme)?  
3. In Traditional Chinese UI mode, should the system also default AI Output Language Preference to zh-TW, or keep it independent (current spec keeps it independent)?  
4. For the WOW Interactive Indicator, which pipeline stages must be represented at minimum: ingestion, trimming, OCR, consolidation, agents, macro summary, WOW modules, export—any others (e.g., dataset search)?  
5. For Live Log, do you want to include a **“reasoning trace”** style log (summarized, not raw chain-of-thought) for compliance audits, or only operational telemetry?  
6. For the WOW Interactive Dashboard, should cost be shown as **estimated** only, or should we implement provider-specific accounting when available (some providers may not return precise cost data)?  
7. Should the dashboard include a **“Regulatory Readiness Index”** that combines Gatekeeper + Evidence coverage + Test Gaps into a single score, or keep them separate to avoid oversimplification?  
8. For credential entry fallback, should users be allowed to input **multiple provider keys simultaneously**, or only prompted as-needed when they select a model from that provider?  
9. Do you require support for **per-agent provider switching** even if the agents.yaml specifies a different provider (current spec allows override)?  
10. Should the system enforce **hard limits** on max tokens per model (clamp), or allow user entry and then preflight-block if unsupported?  
11. When users edit an agent output before handoff, do you want an automatic **diff view** (raw vs edited) stored in the timeline for auditability?  
12. Should direct document prompting outputs be allowed to automatically populate into the Macro Summary context, or remain manual “pin to pipeline” to prevent contamination?  
13. For the Predicate Comparison Matrix Builder, should it require the user to confirm a predicate list before generating the final matrix, or auto-generate candidates end-to-end?  
14. For Standards & Guidance Crosswalk, do you want a maintained internal library of “common standards by device type,” or should it rely purely on document citations and datasets?  
15. For Test Coverage Gap Analyzer, should it output only gaps, or also propose **minimal acceptable test plans** (clearly labeled as suggestions)?  
16. In AI Note Keeper, should keyword highlighting modify only the rendered markdown view, or also insert explicit markup into the saved markdown file (current spec inserts markup + legend)?  
17. Should AI Note Keeper notes be linkable to anchors (file/page) from the main consolidated artifact so that notes become evidence-traceable?  
18. For HF Spaces deployment, what are the expected upper bounds for: maximum PDF size (MB), max pages per session, and max concurrent users (even if Streamlit is single-session per container)?  
19. Should the Export Center generate cryptographic hashes for each artifact (summary, logs, module outputs) to support non-repudiation after export?  
20. Are there any regulatory or organizational requirements to support **role-based access controls** (reviewer vs admin) in enterprise mode, even if HF Spaces remains single-user/session-oriented?
