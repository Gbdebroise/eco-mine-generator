# ARCHITECTURE — Pipeline agents & MCP

> Voir aussi `AGENT_PROMPTS.md` (instructions littérales) et `DECISIONS.md` (ADR-lite).
> À jour : 2026-07-06 (Sprint 4 — Reviewer mode rapport + validation par dataset local ;
> web MCP désactivé sur le Researcher pour la démo).

## Vue d'ensemble

Pipeline ADK 2.0 « classique » : `SequentialAgent(researcher → coder → reviewer)`.
Le state passe via `output_key="csr_summary"` (écrit dans `session.state`) puis
est ré-injecté dans les prompts du Coder ET du Reviewer via le template `{csr_summary}`.

**Pour la démo, le pipeline est 100 % filesystem** : le web MCP (Tavily + Fetch) est
désactivé sur le Researcher (contraintes réseau / VPN — voir `DECISIONS.md` §2026-07-06 et
`TAVILY_VPN_INCIDENT.md`). Le Researcher retombe sur le CSR seul pour la biodiversité.

Depuis le Sprint 4, un 3ᵉ agent **Reviewer** (`gemini-2.5-pro`) clôt le pipeline. Il
**relit** `public/level_config.json` sur disque (MCP read — visible au jury), le valide
sur 3 axes (schéma/plages, cohérence thématique Clérac, équilibrage badge) en comparant les
espèces au **dataset local** `docs/clerac_species_reference.json` (MCP read — pas de web),
puis **écrit** un rapport `docs/reviews/review_<site>.md` (MCP write). **Mode rapport** :
aucun renvoi au Coder (décision Sprint 4 — voir `DECISIONS.md`).

```
                          ┌───────────────────────────────────────────┐
                          │        MCP servers (stdio, via npx)        │
                          ├───────────────────────────────────────────┤
                          │                                           │
  ┌──────────────────┐    │  ┌─────────────────────────────┐          │
  │  researcher_agent │────┼─▶│ filesystem  (read-only view)│  fs_read │
  │  gemini-2.5-flash │    │  │  read_text_file / list_dir  │          │
  │  EXTRACTEUR CSR   │    │  └─────────────────────────────┘          │
  │  (CSR seul —      │    │   tavily-mcp / fetch-mcp : DÉSACTIVÉS      │
  │   web désactivé)  │    │   pour la démo (définis mais non branchés) │
  └────────┬─────────┘    │                                           │
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
  │  {csr_summary}   │    │  │  + clerac_species_reference │          │
  │  → review report │    │  │  write review_<site>.md     │          │
  │  (RAPPORT)       │    │  └─────────────────────────────┘          │
  └──────────────────┘    │   (pas de web — dataset local)            │
                          └───────────────────────────────────────────┘
```

## Accès MCP par agent

| Agent | filesystem (read) | filesystem (write) | tavily (web search) | fetch (URL) |
|-------|:---:|:---:|:---:|:---:|
| **researcher_agent** | ✅ `fs_read` | — | ❌ *(désactivé démo)* | ❌ *(désactivé démo)* |
| **coder_agent** | ✅ (via `fs_write`) | ✅ `fs_write` | — | — |
| **reviewer_agent** | ✅ `fs_read` | ✅ `fs_write` | — | — |

> **Démo = filesystem uniquement.** Aucun agent n'appelle le web. `web_search`/`web_fetch`
> restent définis dans `app/agent.py` mais ne sont branchés sur aucun agent — ré-enrôlement
> trivial hors VPN (les rajouter à `researcher_agent.tools`).

- Le **Reviewer** relit `public/level_config.json` + `docs/level_config_schema.md`
  (+ tout asset référencé) **et le dataset `docs/clerac_species_reference.json`** via
  `fs_read`, compare mécaniquement les espèces à ce dataset (pas de web), et écrit
  `docs/reviews/review_<site>.md` via `fs_write`.

- Le **Researcher** lit le CSR (`app/imerys_csr_data.txt`) et en extrait la biodiversité
  **depuis ce seul fichier** : le web MCP branché au Sprint 2 est **désactivé pour la démo**
  (contraintes réseau / VPN). La biodiversité générée se limite donc aux espèces/groupes
  cités dans le CSR.
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
| `web_search` *(désactivé démo)* | `npx -y tavily-mcp` (env `TAVILY_API_KEY`) | défini, non branché |
| `web_fetch` *(désactivé démo)* | `npx -y @modelcontextprotocol/server-fetch` | défini, non branché |

## Preuve MCP pour le jury

Chaque appel MCP est visible dans la debug view du playground
(`agents-cli playground` → `localhost:8080`). Un run complet (config démo) produit :
- **Researcher** : `read_text_file` (CSR) ;
- **Coder** : `read_text_file` (manifeste) + `write_file` (`level_config.json`) ;
- **Reviewer** : `read_text_file` (config + schéma + `clerac_species_reference.json`) +
  `write_file` (rapport).

Soit un pipeline **100 % filesystem** qui exerce les deux vues MCP (read + write) sur les
3 agents — démonstration multi-agent + MCP, robuste et reproductible sans réseau. Le web
MCP (Tavily/Fetch) reste disponible dans le code pour un ré-enrôlement hors VPN.
