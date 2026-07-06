# Eco-Mine Generator — 4-minute demo script (EN)

> **Language: EN** (international Kaggle jury). Sprint 4 version — features the full
> three-agent pipeline (Researcher → Coder → **Reviewer**) and keeps the **MCP-call counter
> visible on screen** throughout the pipeline segment. Supersedes the old 5-min root
> `VIDEO_SCRIPT.md` (2-agent, deploy-focused). Shooting checklist: `docs/video_checklist.md`.
>
> Narration target ≈ 150 words/min. Record on the WSL test machine. Do NOT open `file://` —
> serve `public/` over HTTP (ES modules). Pre-warm `npx` once before recording so the MCP
> servers are cached.

---

## 0:00 – 0:30 — Hook (the Clérac tension, first line)

**On screen:** title card "Eco-Mine Generator", then a fast scroll through a dense CSR PDF.

**Say:**
"At the Clérac kaolin quarry in France, Imerys blasts clay out of an open pit — and runs a
yearly bird-banding program with the national natural-history museum in the very same pit.
That tension between mining and biodiversity is real, it's documented, and it's buried in
reports nobody reads. So I built a multi-agent system that reads that record and writes a
playable awareness game about it. You give it one thing: a site name."

---

## 0:30 – 1:30 — Architecture (three agents, MCP)

**On screen:** the pipeline diagram — CLI → ADK `SequentialAgent` → Researcher [MCP: read +
Tavily + Fetch] → Coder [MCP: write] → **Reviewer** [MCP: read config + read Clérac dataset +
write] → fixed Phaser engine. Briefly show `app/agent.py` with the three `LlmAgent`s and `McpToolset`.

**Say:**
"It's a three-agent pipeline on Google's ADK. A **Researcher** reads the site's data and
enriches its biodiversity from the web. A **Coder** turns those facts into a small, constrained
level config. And a **Reviewer** independently validates that config — the schema, the real
Clérac species, and whether the game is actually winnable — before a human sees it. Every agent
talks to the filesystem and the web through MCP servers, with least-privilege tool filtering.
The game engine itself is fixed — the agents only generate data. That's what makes it reliable."

---

## 1:30 – 3:00 — Pipeline live (the core — MCP counter on screen)

**On screen:** the playground at `localhost:8080`, history cleared, **MCP-call counter visible
in frame**. Type slowly:

    Generate a game for Clerac

**Say (while it runs):**
"Watch the debug view. The **Researcher** calls the filesystem MCP to read the real CSR —
chamotte clay, bird-banding with the MNHN, chestnut groves left unmined for bats — then calls
**Tavily** and **Fetch** to widen the biodiversity: European otter, kingfisher, natterjack toad.
It hands that to the **Coder**, which reads the asset manifest and writes `level_config.json` —
again, through MCP. Count the tool calls climbing."

**On screen:** the Reviewer step in the debug view.

**Say:**
"Now the **Reviewer** kicks in. It reads the config back off disk, then reads a curated Clérac
species dataset — built from official French environmental sources — and checks the config on
three axes: valid schema and in-range values, only real Clérac species, and a
reachable-but-not-trivial Green badge. That dataset is what lets it reject plausible-sounding
but wrong species — a European roller, say, which is actually Mediterranean and never recorded
here. On this config: everything checks out. It writes the verdict to
`docs/reviews/review_clerac.md`. **PASS**."

**On screen:** open `docs/reviews/review_clerac.md`, scroll the three axes and the verdict.

---

## 3:00 – 3:45 — The generated game (dynamite, water, trucks, badge)

**On screen:** browser, `http://localhost:8000/`, play ~40 seconds.

**Say:**
"And here's what the agents produced. Collect chamotte, band the migratory birds for Green
points. Dynamite explodes and costs you — but doesn't end the run. Rival trucks do. Slow down
through the protected wetland zones. Every label, every fact, every threshold came from the
real site data. Push your score and your Green points high enough and you earn the **Imerys
Green badge** — the win condition the Reviewer just certified as reachable."

**On screen:** the badge celebration screen.

---

## 3:45 – 4:00 — Conclusion (learnings, limits)

**On screen:** the four real sites (Clérac, Beauvoir, Provins, Foufouilloux), then the repo URL.

**Say:**
"Three agents, one MCP-backed pipeline, four real Imerys sites. The honest limit: the Reviewer
reports rather than auto-corrects — a feedback loop is the next step. But the pattern held: a
fixed engine, a constrained config, and an independent validator agent turned a dense CSR report
into a game you can actually play. Code and writeup are linked below."

---

## Notes for the edit

- Keep the **MCP-call counter in frame** for the entire 1:30–3:00 segment — it's the single
  strongest proof for the jury.
- When the Reviewer reads `docs/clerac_species_reference.json`, make sure that `read_text_file`
  is visible in the debug view — it's the call that grounds the species validation.
- **VPN / Tavily contingency:** the corporate VPN blocks Tavily's TLS on the test machine
  (`docs/TAVILY_VPN_INCIDENT.md`). If the Researcher's Tavily/Fetch calls fail on camera, either
  record off-VPN, or trim the "widen the biodiversity" line and lean on the CSR read — the
  Reviewer's dataset read (the stronger MCP beat) is unaffected.
- To show the Reviewer *catching* a bad species on camera, run `tests/manual/run_reviewer.py`
  on the broken fixture as an optional B-roll (verdict FAIL, roller flagged) — but keep the main
  take on the clean Clérac config (PASS).
- If time runs long, trim the game-play segment (3:00–3:45), never the pipeline segment.
- Subtitles: script is EN. If a FR audience is ever targeted, add FR subtitles — but the spoken
  track and captions stay EN for the international jury.
