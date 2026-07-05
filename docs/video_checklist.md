# Video shooting checklist (Sprint 4)

> Run through this on the **WSL test machine** before recording. Script: `docs/video_script.md`.
> You record; this list only prepares the environment. Target: one clean ≤ 4:00 take, 1080p+.

## The day before
- [ ] Pull the latest bundle (`git pull /mnt/d/ecomine.bundle master`) and `uv sync`.
- [ ] `agents-cli install` succeeds; `agents-cli info` shows the three agents + MCP toolsets.
- [ ] `TAVILY_API_KEY` present in `.env` (not synced via bundle — set it locally).
- [ ] Full pipeline dry-run once: `Generate a game for Clerac` → PASS report written to
      `docs/reviews/review_clerac.md`. Fix any issue now, not on camera.
- [ ] Game built & tested: `cd public && python -m http.server 8000` → play a full run,
      confirm dynamite / water / enemy trucks / **Green badge** all trigger.
- [ ] Beauvoir run works too (the generalization beat), in case you extend the take.

## Environment prep (just before recording)
- [ ] **Pre-warm `npx`**: run the pipeline once so all MCP servers are cached (no cold-start
      lag on camera).
- [ ] Playground open at `localhost:8080`, **history cleared** (clean slate).
- [ ] **MCP-call counter visible in frame** — this is the key jury proof; verify it's on screen
      before you hit record.
- [ ] Browser tab ready at `http://localhost:8000/` (served over HTTP — never `file://`).
- [ ] `app/agent.py` open in the editor at the three-agent + `McpToolset` section.
- [ ] `docs/reviews/review_clerac.md` closed (you'll open it live after the Reviewer runs).
- [ ] Windows arranged: split screen playground + game, editor a keystroke away.

## Audio / capture
- [ ] Mic tested, no echo, room quiet.
- [ ] Recording at 1080p minimum, continuous take preferred.
- [ ] Screen text legible at target resolution (bump font sizes in terminal/editor if needed).

## Content beats to hit (from the script)
- [ ] Clérac tension named in the **first spoken line** (hook not buried).
- [ ] Terminal/debug view clearly shows MCP calls: filesystem **read** → Tavily → Fetch
      (Researcher), **write** (Coder), **read** + **write** (Reviewer).
- [ ] Reviewer verdict (**PASS**) shown on screen from `review_clerac.md`.
- [ ] Game plays on screen: dynamite, water slowdown, enemy truck, **Green badge** earned.
- [ ] Conclusion states one honest limit (report-only, no correction loop).
- [ ] Total duration ≤ 4:00.

## Subtitles / delivery
- [ ] Spoken track + captions in **EN** (international jury).
- [ ] Export, verify audio sync, then attach the link in `docs/kaggle_writeup.md` § 9 and § 6.
