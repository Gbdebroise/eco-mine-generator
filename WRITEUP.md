# Eco-Mine Generator — an agent that turns real mining-site data into playable awareness games

**One line:** Give the agent the name of a real Imerys mining site, and it researches that site's environmental program, then generates a custom, playable 2D awareness game about it — deployed live to the web.

---

## The problem

Mining companies run serious biodiversity programs — bird-banding partnerships, quarry rehabilitation, underground-mine choices to protect water resources — but this work is buried in dense CSR reports almost nobody reads. Communication and HSE-training teams need a fast, engaging way to turn that documentation into something people actually pay attention to.

**Eco-Mine Generator** is an agentic tool for exactly that. A non-technical user types one site name; the agent does the research, designs a level around the site's real environmental facts, writes the game, and ships it. No code is written by hand for each new site.

---

## What it does

```
$ adk run eco_mine_generator    # then: "Generate a game for Beauvoir"
```

1. The agent reads the real CSR data for that site.
2. It extracts the key facts: the mineral, the eco-target to protect, the protected area, the danger.
3. It generates a level configuration for the game, including a biome selection.
4. A fixed Phaser 3 engine renders a top-down endless runner from that config.
5. A one-command deploy publishes it to GitHub Pages.

Type `Clerac` and you collect chamotte clay and band migratory birds with the MNHN while avoiding blasting zones and protected chestnut groves. Type `Beauvoir` and the same engine becomes a lithium underground-mining level that protects the Sioule river. **The code never changes — only the agent-generated config does.**

---

## Architecture

```
   CLI ("Generate a game for Beauvoir")
            |
            v
   ADK SequentialAgent  (orchestration, guaranteed order)
            |
     1. researcher_agent  --[MCP: read_file]-->  imerys_csr_data.txt
            |  (passes structured facts via session state)
            v
     2. coder_agent       --[MCP: write_file]--> public/level_config.json
            |
            v
   Fixed Phaser 3 engine reads the config  ->  playable game
            |
            v
   deploy.sh  ->  GitHub Pages (live URL)
```

**Key design decision:** The agent does not try to emit a full working game in one shot. The game engine is fixed and hand-tested; the agent only generates a small constrained JSON configuration (~15 lines). This collapses the LLM error surface from hundreds of lines of JavaScript to structured data — the professional "fixed engine + data-driven content" pattern.

---

## How it meets the capstone criteria

| Pillar | How this project satisfies it |
|---|---|
| **Multi-agent system (ADK)** | A `SequentialAgent` orchestrates two `LlmAgent`s — a researcher and a coder — passing structured facts via ADK session state. |
| **MCP server** | All file I/O goes through the official `@modelcontextprotocol/server-filesystem` via `McpToolset`. Tool filtering enforces least privilege: researcher = read only, coder = write only. |
| **CLI agent** | The whole flow runs from `adk run`, making the research -> generate -> play loop visible end-to-end. |
| **Deployability** | `deploy.sh` publishes the generated game to GitHub Pages in one command. |

---

## Tech stack

- **Agents:** Google ADK (`SequentialAgent`, `LlmAgent`), Gemini 2.5 Flash (research) + Gemini 2.5 Pro (generation)
- **Tools:** MCP filesystem server over stdio via `McpToolset`
- **Game:** Phaser 3 (vanilla JS, no build step), biome-aware procedural placeholder art
- **Assets:** Imagen 3 for backgrounds, Kenney CC0 for sprites
- **Deploy:** GitHub Pages via `git subtree`

---

## Why the data is real

The four bundled sites — Clerac, Beauvoir (EMILI), Provins, Foufouilloux — are real Imerys operations. The environmental facts come from Imerys public communications and public-debate documents. This grounding makes the output credible rather than a generic eco game.

This project is an **educational tool inspired by** real initiatives, not an official Imerys communication.

---

## Limitations & future work

- Replace local data file with a web-research or PDF-reading MCP server for raw CSR reports.
- Add a third validator agent to verify config JSON before writing.
- Replace procedural placeholder art with real pixel-art assets (same texture keys, no logic change).

---

## Links

- **Code:** <your GitHub repo URL>
- **Live demo:** https://<your-username>.github.io/<your-repo>/
- **Video walkthrough:** <your video URL>
