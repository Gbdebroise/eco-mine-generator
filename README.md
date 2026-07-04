# Eco-Mine Generator

**An AI agent that turns a real mining site's environmental data into a playable awareness game — and deploys it to the web.**

Give it one input — a site name — and a multi-agent pipeline researches that site's biodiversity program, designs a custom 2D game level around the real facts, and ships it live.

> Built for the Google x Kaggle *AI Agents Intensive — Vibe Coding* capstone.

---

## What it does

```
$ adk run eco_mine_generator
> Generate a game for Clerac
```

The agent reads the real CSR data for Clerac (chamotte clay, bird-banding with the Museum National d'Histoire Naturelle, protected chestnut groves), writes a level config, and the game engine renders a top-down endless runner from it.

Ask for **Beauvoir** instead and the *same engine* becomes a lithium underground-mining level protecting the Sioule river. **No code changes — only the agent-generated config does.**

Bundled real sites: **Clerac**, **Beauvoir (EMILI)**, **Provins**, **Foufouilloux**.

---

## Architecture

```
   CLI: "Generate a game for Beauvoir"
            |
            v
   ADK SequentialAgent  (guaranteed order)
            |
   1. researcher_agent --[MCP: read_file]--> imerys_csr_data.txt
            |   (structured facts via session state)
            v
   2. coder_agent      --[MCP: write_file]--> public/level_config.json
            |
            v
   Fixed Phaser 3 engine reads the config --> playable game
            |
            v
   deploy.sh --> GitHub Pages (live URL)
```

---

## Project structure

```
eco-mine-generator/
├── eco_mine_generator/
│   ├── __init__.py
│   ├── agent.py               # ADK agents (SequentialAgent + researcher + coder)
│   └── imerys_csr_data.txt    # real site data (read by the agent via MCP)
├── public/
│   ├── index.html
│   ├── game.js                # fixed Phaser 3 engine
│   ├── assets/                # sprites and backgrounds (Kenney CC0 + Imagen)
│   └── level_config.json      # written by the agent (via MCP)
├── generate_assets.py         # generates backgrounds with Imagen
├── deploy.sh                  # one-command deploy to GitHub Pages
├── WRITEUP.md                 # Kaggle submission writeup
├── ASSETS_GUIDE.md            # asset sourcing guide
└── README.md
```

---

## Quickstart

```bash
# 1. Install dependencies
pip install google-adk mcp google-genai pillow
# Node.js / npx required for the MCP filesystem server

# 2. Auth
gcloud auth application-default login

# 3. Run the agent
adk run eco_mine_generator
# then type: Generate a game for Clerac

# 4. Play locally
cd public && python -m http.server 8000
# open http://localhost:8000

# 5. Generate backgrounds (optional)
python generate_assets.py --biome clay_quarry

# 6. Deploy
bash deploy.sh
```

---

## Capstone criteria

| Pillar | Implementation |
|---|---|
| **Multi-agent (ADK)** | `SequentialAgent` with researcher + coder `LlmAgent` |
| **MCP server** | `@modelcontextprotocol/server-filesystem` via `McpToolset` |
| **CLI agent** | End-to-end from `adk run` |
| **Deployability** | `deploy.sh` to GitHub Pages |

---

## Tech stack

ADK · Gemini 2.5 Flash + Pro · MCP filesystem server · Phaser 3 · Imagen 3 · GitHub Pages

---

## Data & credits

Site data from Imerys public communications (imerys.com, emili.imerys.com).
Educational tool — not an official Imerys communication.

## Links

- **Live demo:** https://<your-username>.github.io/<your-repo>/
- **Video:** <your video URL>
