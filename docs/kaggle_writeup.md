# Eco-Mine Generator — turning a real mining site's biodiversity record into a game an agent writes itself

> **Status: skeleton + intentions (Sprint 4).** Sections 1–5, 7, 8 are final-draft prose.
> Section 6 (Results) and the video/screenshot links in Section 9 are placeholders to be
> filled after the WSL test pass and the recording. See `docs/HANDOFF.md` for state.
> Language: **EN** (international Kaggle jury). Sources: `app/imerys_csr_data.txt`,
> `docs/ARCHITECTURE.md`, `docs/level_config_schema.md`.

---

## 1. Hook

At the Clérac kaolin quarry in Charente-Maritime, Imerys blasts refractory clay out of an open pit **and** runs an annual bird-banding program with France's Muséum National d'Histoire Naturelle — the same pit is a stopover for migratory birds, and whole chestnut groves are left unmined so bats can roost. That tension between extraction and biodiversity is real, it is documented, and almost nobody reads the report it lives in. **Eco-Mine Generator is a multi-agent pipeline that reads that record and writes a small, playable awareness game about it — one site name in, one custom level out, no game code written by hand.**

## 2. Problem & original angle

Mining companies publish serious environmental commitments — bird monitoring, quarry rehabilitation, deliberate underground-mining choices to spare a river — buried in dense CSR PDFs. Communication and HSE-training teams have no fast way to turn that documentation into something people actually engage with.

The original angle is twofold:

- **A real, specific, grounded subject** rather than a generic "eco game": four actual Imerys sites (Clérac, Beauvoir/EMILI, Provins, Foufouilloux), with facts drawn from public Imerys communications and public-debate documents.
- **Multi-agent, not one-shot.** The interesting engineering claim is *reliability through decomposition*: a **Researcher** extracts and web-enriches the facts, a **Coder** turns them into a tightly-constrained level config, and a **Reviewer** independently validates that config against the schema, the site's real biodiversity, and playability — before a human ever looks at it. Each agent has one job and least-privilege tools.

Why multi-agent is the right shape here, not decoration: the failure modes are *different in kind* at each stage (a researcher hallucinates a species; a coder emits out-of-range or off-schema values; a level can be un-winnable). A single prompt cannot separate "did we get the facts right" from "is the JSON valid" from "is the badge reachable." Three agents with three narrow contracts can.

## 3. Architecture

```
   CLI / playground  ("Generate a game for Clerac")
            │
            ▼
   ADK 2.0  SequentialAgent  (guaranteed order, state via output_key + {template})
            │
   1. researcher_agent   gemini-2.5-flash
        │  MCP: filesystem(read)  → app/imerys_csr_data.txt   (the site's CSR facts)
        │  MCP: tavily(search)    → real regional species
        │  MCP: fetch(url)        → read a discovered source
        │  output_key="csr_summary"  →  session.state
            │
   2. coder_agent        gemini-2.5-pro
        │  reads {csr_summary} from state
        │  MCP: filesystem(read)   → docs/ASSET_MANIFEST.md   (anti-hallucination)
        │  MCP: filesystem(write)  → public/level_config.json
            │
   3. reviewer_agent     gemini-2.5-pro          ◄── NEW (Sprint 4)
        │  MCP: filesystem(read)   → public/level_config.json + schema + manifest
        │  MCP: tavily(search)     → verify a doubtful species
        │  MCP: filesystem(write)  → docs/reviews/review_<site>.md   (human-readable verdict)
            │
            ▼
   Fixed Phaser 3 engine (public/game.js, hand-coded) reads the config  →  playable game
```

**Role of each MCP (why the jury sees real tool calls):**

| MCP server | Used by | What it proves in the playground debug view |
|---|---|---|
| `@modelcontextprotocol/server-filesystem` (read view) | Researcher, Coder, Reviewer | `read_text_file` on the CSR, the asset manifest, the generated config, the schema |
| `tavily-mcp` | Researcher, Reviewer | web-search `tool_use` — the Researcher enriches biodiversity; the Reviewer *fact-checks* a doubtful species |
| `@modelcontextprotocol/server-fetch` | Researcher | reads the content of a discovered URL |
| `@modelcontextprotocol/server-filesystem` (write view) | Coder, Reviewer | `write_file` on `level_config.json` (Coder) and the review report (Reviewer) |

**Key design decision (carried from Sprints 1–3):** the agents never emit game code. They produce a ~50-line constrained `level_config.json`; the Phaser engine is fixed and hand-tested. This collapses the LLM error surface from hundreds of lines of fragile JavaScript to structured data with documented ranges (`docs/level_config_schema.md`). The Reviewer is the third leg of that same reliability strategy: *validate the data, since the data is all the agent controls.*

## 4. The pipeline in action (what the video shows)

1. **Ask for a site** — `Generate a game for Clerac` in the playground.
2. **Researcher** reads `imerys_csr_data.txt` (visible `read_text_file`), then calls **Tavily** and **Fetch** to widen biodiversity beyond the file (European roller, bee-eater, natterjack toad…). Output: a clean JSON `csr_summary` in session state.
3. **Coder** reads the asset manifest (visible `read_text_file`), writes `public/level_config.json` (visible `write_file`) — labels, biome, five gameplay sections, and the narrative strings.
4. **Reviewer** reads that config back off disk (visible `read_text_file`), checks it on three axes, optionally fact-checks one species via **Tavily**, and writes `docs/reviews/review_clerac.md` (visible `write_file`) with a global verdict.
5. **Play it** — the fixed engine renders the top-down runner: collect Chamotte, band migratory birds, dodge dynamite and rival trucks, slow through the protected wetlands, chase the Imerys Green badge.
6. **The generalization beat** — change nothing in the code, ask for **Beauvoir**: same engine, a lithium underground-mining level that protects the Sioule river.

## 5. The Reviewer in detail (validation contract)

The Reviewer runs **as a report**, not a correction loop (decision locked Sprint 4: simpler, safer to demo, no orchestration change — it is appended as the third `sub_agent` of the existing `SequentialAgent`). It reads the freshly-written `public/level_config.json` and the researcher's `csr_summary`, evaluates **three axes**, and writes a human-readable verdict to `docs/reviews/review_<site>.md`. Every read/write and every fact-check is an MCP call visible in the playground.

### Axis 1 — Config validity
- The JSON parses and matches the Sprint 3 schema (`docs/level_config_schema.md`): all required keys present, correct types.
- Every value sits inside its **recommended range** (e.g. `dynamite.spawn_weight` ∈ [0.08, 0.20], `difficulty.speed_max_px_per_s` ∈ [400, 560], `green_badge.min_green_points` ∈ [20, 40]).
- No section is emptied and no `spawn_weight` is `0` (that would silently delete a mechanic).
- Any asset path referenced actually exists on disk — checked by reading it via the filesystem MCP (**one more visible MCP call**). A `missing_assets` array, if present, is surfaced, not hidden.

### Axis 2 — Clérac thematic coherence
- Every species in `biodiversity_species` belongs to the site's real list: **European roller, bee-eater, nightjar, natterjack toad, ocellated lizard, orchids, local insects, migratory birds, cave bats** (Clérac); the allowlist is site-specific and grounded in `imerys_csr_data.txt`.
- **No off-site species** — no tiger, no polar bear, no irrelevant Mediterranean flora.
- The mineral is **kaolin / chamotte clay** — not coal, not gold.
- If a species is *not* on the known list, the Reviewer does not guess: it calls **Tavily** to check whether that species is credibly present at Clérac / its region, and records the finding. **This is an extra visible MCP call — and a genuine agentic fact-check, not a hard-coded string match.**

### Axis 3 — Gameplay balance
Grounded in the real scoring in `public/game.js` (ore `+10`, bird `+15` and `+1` green, grove `−20`/`−3` green, dynamite `−200`/`−10` green, distance `+1` per 10 px; badge = `score ≥ min_score` **AND** `green_points ≥ min_green_points`):
- The **Imerys Green badge is reachable**: with the config's `min_score`/`min_green_points`, an average player *can* clear it (≈ `min_green_points` clean eco collects plus enough ore/distance to pass `min_score`).
- But **not trivial**: the thresholds are not met in ~30 seconds of play.
- A **progressive difficulty curve** is present and calibrated — `speed_start < speed_max`, a sane `distance_to_max_px`, a spawn multiplier that actually rises (curve is not flat).

### Output contract
- **Human-readable file** `docs/reviews/review_<site>.md`: a global verdict (`PASS` / `PASS WITH WARNINGS` / `FAIL`) followed by a per-axis breakdown with the specific values checked.
- **Visible in the playground**: the read of the config, the read of the manifest, the optional Tavily fact-check, and the write of the report all appear as MCP `tool_use` events.
- The report does **not** loop back to the Coder (locked decision); a human reads the verdict and decides whether to re-run.

> **Explicit criteria contract** (the list the build in Étape 2 must satisfy) is reproduced verbatim for the reviewer prompt in `docs/AGENT_PROMPTS.md` § Reviewer.

## 6. Results

> *[To be filled after the WSL test pass — see `docs/HANDOFF.md` § Validation.]*
> - Number of MCP `tool_use` events observed in one full run (target: filesystem read ×N, Tavily ×≥1, fetch ×≥1, write ×2).
> - Example generated `level_config.json` (Clérac) — link/inline.
> - Example generated `docs/reviews/review_clerac.md` — link/inline.
> - Reviewer catching an intentionally broken config (off-site species + out-of-range values) — before/after.
> - The generalization: Clérac vs Beauvoir side by side.

## 7. Limits & learnings

- **Reviewer is report-only, not a correction loop.** A feedback loop back to the Coder would be more impressive but riskier to demo and harder to bound (infinite-iteration risk). We chose robustness for the capstone deadline; the loop is documented as future work.
- **Species fact-checking depends on web search quality.** Tavily can miss or over-return; the Reviewer flags doubt rather than asserting, which is the honest behavior but not a hard guarantee.
- **No reliable clock inside the agent**, so reviews are named `review_<site>.md` (deterministic, meaningful) rather than by timestamp — a small, deliberate deviation from the original spec.
- **The data is real but not exhaustively re-verified against the latest CSR** — the source file says so explicitly. This is an educational tool *inspired by* real initiatives, not an official Imerys communication.
- **What worked:** the "fixed engine + constrained config + independent validator" pattern. Almost every failure we hit across four sprints was an *agent producing bad data*, and moving validation into its own agent with its own tools (rather than more prompt rules) is what made the output trustworthy.

## 8. Reproducibility

Prerequisites (WSL 2): `uv`, `agents-cli`, Node 24, MCP servers reachable via `npx`, and a `TAVILY_API_KEY` in `.env`.

```bash
# 1. install
agents-cli install

# 2. run the full pipeline interactively (debug view on localhost:8080)
agents-cli playground
#    then type:  Generate a game for Clerac
#    watch: researcher (read + Tavily + Fetch) → coder (write) → reviewer (read + write)

# 3. play the generated game (no agent needed)
cd public && python -m http.server 8000
#    open http://localhost:8000/                         (loads level_config.json)
#    or   http://localhost:8000/?config=configs/examples/level_config.sprint3.json
```

The three agents live in `app/agent.py`; their literal prompts are in `docs/AGENT_PROMPTS.md`; the config contract is `docs/level_config_schema.md`.

## 9. Appendix

- **Video walkthrough:** *[link — Sprint 4 Étape 4]*
- **Playground screenshots (MCP proof):** `docs/screenshots/` *[to be added]*
- **Example generated config:** `public/configs/examples/level_config.sprint3.json`
- **Example Reviewer report:** `docs/reviews/review_clerac.md` *[generated on WSL test pass]*
- **Code:** *[GitHub repo URL — jury-only mirror]*
- **Architecture & decisions:** `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`
