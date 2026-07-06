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
        │  (web MCP disabled for the demo — CSR-only, see §7)
        │  output_key="csr_summary"  →  session.state
            │
   2. coder_agent        gemini-2.5-pro
        │  reads {csr_summary} from state
        │  MCP: filesystem(read)   → docs/ASSET_MANIFEST.md   (anti-hallucination)
        │  MCP: filesystem(write)  → public/level_config.json
            │
   3. reviewer_agent     gemini-2.5-pro          ◄── NEW (Sprint 4)
        │  MCP: filesystem(read)   → level_config.json + schema + manifest
        │  MCP: filesystem(read)   → docs/clerac_species_reference.json  (curated CNPN/MRAe/DREAL dataset)
        │  MCP: filesystem(write)  → docs/reviews/review_<site>.md   (human-readable verdict)
            │
            ▼
   Fixed Phaser 3 engine (public/game.js, hand-coded) reads the config  →  playable game
```

**Role of each MCP (why the jury sees real tool calls):**

| MCP server | Used by | What it proves in the playground debug view |
|---|---|---|
| `@modelcontextprotocol/server-filesystem` (read view) | Researcher, Coder, Reviewer | `read_text_file` on the CSR, the asset manifest, the generated config, the schema, and the **curated Clérac species dataset** (Reviewer) |
| `@modelcontextprotocol/server-filesystem` (write view) | Coder, Reviewer | `write_file` on `level_config.json` (Coder) and the review report (Reviewer) |
| `tavily-mcp` / `server-fetch` | *(disabled for the demo)* | web enrichment of biodiversity — wired in Sprint 2, **switched off for the demo phase** (network constraints); trivially re-enabled off-VPN |

> **The whole demo pipeline is filesystem-only — deliberately.** We wired web MCP (Tavily + Fetch) into the Researcher in Sprint 2, but the corporate VPN's TLS inspection blocks Tavily on the test machine (see `docs/TAVILY_VPN_INCIDENT.md`). Rather than fight the network on camera, **we prioritized reliability over web enrichment during the demo phase due to network constraints**: the Researcher falls back to the CSR file alone for biodiversity, and the whole run is 100 % local and reproducible. Validation is *stronger* than a live web guess anyway — the Reviewer checks `biodiversity_species` against `docs/clerac_species_reference.json`, a curated dataset built from official sources (CNPN, MRAe Nouvelle-Aquitaine, DREAL Natura 2000, INPN): 51 validated species plus an explicit `especes_incorrectes` list. That read is itself a visible MCP call.

**Key design decision (carried from Sprints 1–3):** the agents never emit game code. They produce a ~50-line constrained `level_config.json`; the Phaser engine is fixed and hand-tested. This collapses the LLM error surface from hundreds of lines of fragile JavaScript to structured data with documented ranges (`docs/level_config_schema.md`). The Reviewer is the third leg of that same reliability strategy: *validate the data, since the data is all the agent controls.*

## 4. The pipeline in action (what the video shows)

1. **Ask for a site** — `Generate a game for Clerac` in the playground.
2. **Researcher** reads `imerys_csr_data.txt` (visible `read_text_file`) and extracts the site's facts and biodiversity **from the CSR alone** (web enrichment is off for the demo). Output: a clean JSON `csr_summary` in session state.
3. **Coder** reads the asset manifest (visible `read_text_file`), writes `public/level_config.json` (visible `write_file`) — labels, biome, five gameplay sections, and the narrative strings.
4. **Reviewer** reads that config back off disk (visible `read_text_file`), reads the curated Clérac dataset (`read_text_file` on `docs/clerac_species_reference.json`), checks the config on three axes, and writes `docs/reviews/review_clerac.md` (visible `write_file`) with a global verdict.
5. **Play it** — the fixed engine renders the top-down runner: collect Chamotte, band migratory birds, dodge dynamite and rival trucks, slow through the protected wetlands, chase the Imerys Green badge.
6. **The generalization beat** — change nothing in the code, ask for **Beauvoir**: same engine, a lithium underground-mining level that protects the Sioule river.

## 5. The Reviewer in detail (validation contract)

The Reviewer runs **as a report**, not a correction loop (decision locked Sprint 4: simpler, safer to demo, no orchestration change — it is appended as the third `sub_agent` of the existing `SequentialAgent`). It reads the freshly-written `public/level_config.json`, the researcher's `csr_summary`, and the curated Clérac reference dataset, evaluates **three axes**, and writes a human-readable verdict to `docs/reviews/review_<site>.md`. Every read and write is an MCP call visible in the playground.

### Axis 1 — Config validity
- The JSON parses and matches the Sprint 3 schema (`docs/level_config_schema.md`): all required keys present, correct types.
- Every value sits inside its **recommended range** (e.g. `dynamite.spawn_weight` ∈ [0.08, 0.20], `difficulty.speed_max_px_per_s` ∈ [400, 560], `green_badge.min_green_points` ∈ [20, 40]).
- No section is emptied and no `spawn_weight` is `0` (that would silently delete a mechanic).
- Any asset path referenced actually exists on disk — checked by reading it via the filesystem MCP (**one more visible MCP call**). A `missing_assets` array, if present, is surfaced, not hidden.

### Axis 2 — Clérac thematic coherence
Validated **mechanically against `docs/clerac_species_reference.json`** — a curated dataset (CNPN, MRAe Nouvelle-Aquitaine, DREAL Natura 2000, INPN) of 51 species really recorded at Clérac, an explicit `especes_incorrectes` list, valid habitats, and site context. The Reviewer does not reason from its own memory; it compares each config entry to this authoritative source.
- Each species in `biodiversity_species` is matched to the dataset: **validated** (e.g. European otter, European mink, kingfisher, nightjar, natterjack toad, Dartford warbler, noctule bat) → OK; **in `especes_incorrectes`** → flagged with the recommended substitution; **unknown** → flagged as "verify — outside reference".
- This axis has real teeth: the dataset records that **European roller, bee-eater and ocellated lizard are Mediterranean species absent from the official Clérac inventories** — a plausible-sounding hallucination a naive researcher (or LLM) will happily emit. The Reviewer catches each and proposes the correct local substitute (roller → Dartford warbler, ocellated lizard → western green lizard).
- The mineral is checked against `site_context.minerai_principal` — **kaolin / chamotte**, not coal, not gold (`error` if wrong). Habitats and commune are checked against the dataset too.
- The read of the dataset is the visible MCP call that grounds this validation — an **auditable** check, not a live web guess.

### Axis 3 — Gameplay balance
Grounded in the real scoring in `public/game.js` (ore `+10`, bird `+15` and `+1` green, grove `−20`/`−3` green, dynamite `−200`/`−10` green, distance `+1` per 10 px; badge = `score ≥ min_score` **AND** `green_points ≥ min_green_points`):
- The **Imerys Green badge is reachable**: with the config's `min_score`/`min_green_points`, an average player *can* clear it (≈ `min_green_points` clean eco collects plus enough ore/distance to pass `min_score`).
- But **not trivial**: the thresholds are not met in ~30 seconds of play.
- A **progressive difficulty curve** is present and calibrated — `speed_start < speed_max`, a sane `distance_to_max_px`, a spawn multiplier that actually rises (curve is not flat).

### Output contract
- **Human-readable file** `docs/reviews/review_<site>.md`: a global verdict (`PASS` / `PASS WITH WARNINGS` / `FAIL`) followed by a per-axis breakdown with the specific values checked.
- **Visible in the playground**: the read of the config, the read of the schema/manifest, the read of the Clérac reference dataset, and the write of the report all appear as MCP `tool_use` events.
- The report does **not** loop back to the Coder (locked decision); a human reads the verdict and decides whether to re-run.

> **Explicit criteria contract** (the list the build in Étape 2 must satisfy) is reproduced verbatim for the reviewer prompt in `docs/AGENT_PROMPTS.md` § Reviewer.

## 6. Results

> *[To be filled after the WSL test pass — see `docs/HANDOFF.md` § Validation.]*
> - Number of MCP `tool_use` events observed in one full run (target, demo config = filesystem-only: read ×N incl. the CSR and the Clérac dataset, write ×2). Web MCP is off for the demo (see §7 / `docs/TAVILY_VPN_INCIDENT.md`).
> - Example generated `level_config.json` (Clérac) — link/inline.
> - Example generated `docs/reviews/review_clerac.md` — link/inline.
> - Reviewer catching an intentionally broken config (off-site species + out-of-range values) — before/after.
> - The generalization: Clérac vs Beauvoir side by side.

## 7. Limits & learnings

- **Reviewer is report-only, not a correction loop.** A feedback loop back to the Coder would be more impressive but riskier to demo and harder to bound (infinite-iteration risk). We chose robustness for the capstone deadline; the loop is documented as future work.
- **Web enrichment is off for the demo — a reliability trade-off.** The Researcher can widen biodiversity via Tavily + Fetch (wired in Sprint 2), but the corporate VPN's TLS inspection blocks Tavily on the test machine (`docs/TAVILY_VPN_INCIDENT.md`). **We prioritized reliability over web enrichment during the demo phase due to network constraints**: the Researcher falls back to the CSR file alone, so the pipeline is 100 % local and reproducible on camera. The cost is thinner biodiversity in a fresh run (only the species the CSR names); the web path is a one-line re-enable off-VPN.
- **Species validation rests on a curated static dataset, not live web search.** The Reviewer checks against `docs/clerac_species_reference.json` — an authoritative, auditable reference (CNPN/MRAe/DREAL/INPN) that is honestly the better choice for a validator than a live web guess. The trade-off: the dataset is maintained by hand, and today only Clérac is covered in that depth (the other three sites fall back to looser CSR-based checks).
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
#    watch: researcher (read CSR) → coder (write) → reviewer (read config + dataset, write report)

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
