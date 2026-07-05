# ARCHITECTURE — Pipeline agents & MCP

> Voir aussi `AGENT_PROMPTS.md` (instructions littérales) et `DECISIONS.md` (ADR-lite).
> À jour : 2026-07-05 (Sprint 4 — ajout du 3ᵉ agent Reviewer, mode rapport).

## Vue d'ensemble

Pipeline ADK 2.0 « classique » : `SequentialAgent(researcher → coder → reviewer)`.
Le state passe via `output_key="csr_summary"` (écrit dans `session.state`) puis
est ré-injecté dans les prompts du Coder ET du Reviewer via le template `{csr_summary}`.

Depuis le Sprint 4, un 3ᵉ agent **Reviewer** (`gemini-2.5-pro`) clôt le pipeline. Il
**relit** `public/level_config.json` sur disque (MCP read — visible au jury), le valide
sur 3 axes (schéma/plages, cohérence thématique Clérac, équilibrage badge), fact-checke
au besoin une espèce douteuse via Tavily (MCP call conditionnel), puis **écrit** un
rapport `docs/reviews/review_<site>.md` (MCP write). **Mode rapport** : aucun renvoi au
Coder (décision Sprint 4 — voir `DECISIONS.md`).

```
                          ┌───────────────────────────────────────────┐
                          │        MCP servers (stdio, via npx)        │
                          ├───────────────────────────────────────────┤
                          │                                           │
  ┌──────────────────┐    │  ┌─────────────────────────────┐          │
  │  researcher_agent │────┼─▶│ filesystem  (read-only view)│  fs_read │
  │  gemini-2.5-flash │    │  │  read_text_file / list_dir  │          │
  │                   │    │  └─────────────────────────────┘          │
  │  EXTRACTEUR CSR   │────┼─▶│ tavily-mcp  (recherche web) │ web_search│
  │  + recherche web  │    │  │  TAVILY_API_KEY depuis .env │          │
  │                   │────┼─▶│ fetch-mcp   (lecture URL)   │ web_fetch │
  └────────┬─────────┘    │  └─────────────────────────────┘          │
           │              │                                           │
   output_key=            │  ┌─────────────────────────────┐          │
   "csr_summary"          │  │ filesystem (read+write view)│  fs_write │
   (session.state)        │  │  write_file / read_text_file│          │
           │              │  └─────────────────────────────┘          │
           ▼              │              ▲                            │
  ┌──────────────────┐    │              │                            │
  │   coder_agent    │────┼──────────────┘                            │
  │  gemini-2.5-pro  │    │  (filesystem UNIQUEMENT — pas de web)      │
  │  {csr_summary}   │    └───────────────────────────────────────────┘
  │  → level_config  │
  └────────┬─────────┘
           │ (level_config.json écrit sur disque, puis relu par le Reviewer)
           ▼              ┌───────────────────────────────────────────┐
  ┌──────────────────┐    │  ┌─────────────────────────────┐          │
  │  reviewer_agent  │────┼─▶│ filesystem (read+write)     │ fs_read/  │
  │  gemini-2.5-pro  │    │  │  read config+schema+manifest│ fs_write  │
  │  {csr_summary}   │    │  │  write review_<site>.md     │          │
  │  → review report │────┼─▶│ tavily (fact-check espèce)  │ web_search│
  │  (RAPPORT)       │    │  └─────────────────────────────┘          │
  └──────────────────┘    └───────────────────────────────────────────┘
```

## Accès MCP par agent

| Agent | filesystem (read) | filesystem (write) | tavily (web search) | fetch (URL) |
|-------|:---:|:---:|:---:|:---:|
| **researcher_agent** | ✅ `fs_read` | — | ✅ `web_search` | ✅ `web_fetch` |
| **coder_agent** | ✅ (via `fs_write`) | ✅ `fs_write` | — | — |
| **reviewer_agent** | ✅ `fs_read` | ✅ `fs_write` | ✅ `web_search` | — |

- Le **Reviewer** relit `public/level_config.json` + `docs/level_config_schema.md`
  (+ tout asset référencé) via `fs_read`, fact-checke une espèce douteuse via `web_search`
  (Tavily), et écrit `docs/reviews/review_<site>.md` via `fs_write`. Pas de `fetch`.

- Le **Researcher** lit le CSR (`app/imerys_csr_data.txt`), et — depuis Sprint 2 —
  peut enrichir le contexte biodiversité/narratif via Tavily (découverte de sources)
  puis Fetch (lecture du contenu des URLs découvertes).
- Le **Coder** reste volontairement confiné au filesystem : il lit
  `docs/ASSET_MANIFEST.md` (contrainte anti-hallucination) et écrit
  `public/level_config.json`. Aucun accès web.

## Détails d'implémentation

Tous les serveurs MCP sont déclarés programmatiquement dans `app/agent.py` via
`McpToolset` + `StdioConnectionParams` (lancés en stdio par `npx`). Il n'y a
**aucune** config MCP dans `agents-cli-manifest.yaml` (métadonnées projet seulement).

| Toolset | Commande | Filtre d'outils |
|---------|----------|-----------------|
| `fs_read` | `npx -y @modelcontextprotocol/server-filesystem <PROJECT_DIR>` | `read_text_file`, `read_file`, `list_directory` |
| `fs_write` | `npx -y @modelcontextprotocol/server-filesystem <PROJECT_DIR>` | `write_file`, `read_text_file` |
| `web_search` | `npx -y tavily-mcp` (env `TAVILY_API_KEY`) | — (tous outils Tavily) |
| `web_fetch` | `npx -y @modelcontextprotocol/server-fetch` | — (tous outils Fetch) |

## Preuve MCP pour le jury

Chaque appel MCP est visible dans la debug view du playground
(`agents-cli playground` → `localhost:8080`). Un run complet produit :
- **Researcher** : `read_text_file` (CSR) + `tool_use` Tavily + Fetch ;
- **Coder** : `read_text_file` (manifeste) + `write_file` (`level_config.json`) ;
- **Reviewer** : `read_text_file` (config + schéma) + `write_file` (rapport) +
  **optionnellement** un `tool_use` Tavily si une espèce sort de la liste connue.

Soit un pipeline qui exerce les 3 serveurs MCP (filesystem read+write, Tavily, Fetch) sur
les 3 agents — la démonstration multi-agent + multi-MCP attendue par le jury capstone.
