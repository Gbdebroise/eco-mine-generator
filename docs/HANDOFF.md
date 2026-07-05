# HANDOFF — Eco-Mine Generator / Mission Clérac

> **Date** : 5 juillet 2026
> **Auteur du projet** : Bertrand
> **Contexte** : Capstone Google × Kaggle AI Agents Intensive Vibe Coding
> **But de ce document** : reprendre le projet dans une nouvelle conversation Claude ou dans Claude Code sans perdre le contexte accumulé.

---

## 🎯 Prompt de démarrage à copier dans le nouveau chat

```
Je reprends le projet Eco-Mine Generator / Mission Clérac (capstone Google × Kaggle 
AI Agents Intensive). Voici le document de handoff qui résume l'état actuel, les 
décisions prises, et la roadmap. Merci de le lire attentivement avant qu'on continue.

[Coller ici le contenu de HANDOFF.md]

Sprint 1 est TERMINÉ (prompts corrigés, preuve MCP, manifeste d'assets). On en est 
au Sprint 2 : enrichissement narratif. Les 2 web MCP (Tavily + Fetch) viennent d'être 
branchés au Researcher dans app/agent.py (étape 2.3). Prochaine action concrète : 
test de connectivité MCP dans le playground + captures debug view (étape 2.4). Stack : 
agents-cli + ADK 2.0 « classique » (SequentialAgent, state via output_key + template). 

IMPORTANT : je développe sur un PC (Windows natif, édition uniquement) et je teste 
sur un autre PC (WSL 2, pipeline complet). Sync via git bundle sur clé USB. 
Ne me propose pas d'exécuter agents-cli, uv run ou pytest sur la machine 
d'édition — ils ne sont pas installés ici.
```

---

## 📌 État actuel du projet (au 5 juillet 2026)

### Contexte d'exécution ⚠️
**Le projet est développé sur deux machines distinctes.**

- **Machine d'édition (celle où tu lis probablement ce doc)** : Windows natif, pas de WSL 2, pas de `uv`, pas de `agents-cli`. Sert uniquement à éditer du code et des docs.
- **Machine de test** : WSL 2 + `uv` + `agents-cli` + Node 24 + MCP servers configurés. C'est là que tourne `agents-cli playground` sur `localhost:8080`.
- **Sync** : `git bundle` sur clé USB (aucun compte GitHub partagé possible entre les deux PC).

Workflow standard : édition → `git commit` → `git bundle create /d/ecomine.bundle master` → clé USB → `git pull /mnt/d/ecomine.bundle master` sur la machine de test → `uv sync` si dépendances changées → `agents-cli playground`.

Ne JAMAIS copier via clé USB : `.venv/`, `__pycache__/`, `.env`, `.pytest_cache/`, `node_modules/` (déjà dans `.gitignore`).

### Ce qui fonctionne
- Pipeline ADK 2.0 `SequentialAgent` (researcher → coder) avec `agents-cli` (playground OK sur `localhost:8080` avec debug view)
- Environnement WSL 2 sur Windows, projet à `C:\Users\bertr\Documents\PROJETS\eco-mine-generator`
- Python 3.12, `uv` pour la gestion des packages, Node.js 24, Pillow 12
- Génération d'un `level_config.json` par le Coder consommé par un `game.js` Phaser 3 hand-coded
- Génération d'une image de fond de Clérac via Imagen 3
- MCP filesystem (`@modelcontextprotocol/server-filesystem`) branché avec filtrage des tools (Researcher = read only, Coder = write only)
- **Web MCP branchés au Researcher (Sprint 2, étape 2.3, commit `95f6b8c`)** : `tavily-mcp` (recherche web, clé `TAVILY_API_KEY`) + `@modelcontextprotocol/server-fetch` (lecture URL), déclarés dans `app/agent.py` (`tools=[fs_read, web_search, web_fetch]`). Le Coder reste filesystem-only. ⚠️ Connectivité **pas encore testée** en playground (étape 2.4).

### Ce qui ne fonctionne pas (problèmes identifiés lors du test du 3 juillet)
1. **Message d'erreur du Researcher** : *« Je ne suis pas en mesure de générer des jeux »* → ✅ **résolu** (Sprint 1, commit `9539133`). Cause réelle : le MCP filesystem ne résolvait pas le chemin du CSR → researcher sans données → refus. Fix : chemin `app/imerys_csr_data.txt` + lecture obligatoire. Les captures baseline du 5 juil. montrent un run complet sans erreur.
2. **Jeu généré sans données Clérac** : le config est peut-être bien produit mais soit vide soit non consommé par `game.js`
3. **MCP calls non prouvés** au jury (bloquant pour le challenge)
4. **Hallucinations d'assets** : le Coder référence des fichiers qui n'existent pas sur le disque
5. **Fond d'écran de tuiles avec espaces visibles** entre chaque tuile répétée

---

## 🏗️ Architecture technique (ADK 2.0)

**Stack :**
- `agents-cli` (wrapper autour d'ADK 2.0) pour scaffolding, playground, éval, déploiement
- ADK 2.0 **« classique »** : `SequentialAgent` orchestrant deux `LlmAgent` (`researcher_agent` → `coder_agent`). ⚠️ Ce n'est PAS un graph workflow `@node`/`Workflow`/`Event` — voir `app/agent.py` (code réel) et `docs/AGENT_PROMPTS.md`. La mention « graph workflow » des versions antérieures de ce doc était erronée.
- Modèles : `gemini-2.5-flash` pour Researcher, `gemini-2.5-pro` pour Coder
- MCP : `@modelcontextprotocol/server-filesystem` avec tool filtering
- Frontend jeu : Phaser 3, `game.js` hand-coded qui lit `level_config.json`
- Génération images : Imagen 3
- Post-processing images : Pillow (justifié pour le tile slicing du background)

**Pipeline agents :**
```
Researcher (extrait données Clérac depuis fichiers + web)
    ↓ session.state["csr_summary"]
Coder (génère level_config.json ~50 lignes)
    ↓ écrit public/level_config.json (disque)
Reviewer [✅ CRÉÉ Sprint 4] (relit le config, valide 3 axes, écrit un RAPPORT
    docs/reviews/review_<site>.md — mode rapport, pas de renvoi au Coder)
```

**Workflow debug/preuve MCP :**
- `agents-cli playground` → UI sur `localhost:8080` avec debug view
- Debug view affiche chronologiquement les événements `tool_use` / `tool_result` MCP
- Screenshots/captures vidéo de cette UI = preuve pour le jury

---

## 🧠 Décisions techniques prises

| Date | Décision | Raison |
|------|----------|--------|
| Antérieur | Config-driven generation (pas de génération complète de `game.js`) | Le LLM hallucine trop souvent du code Phaser complexe |
| Antérieur | `uv` au lieu de pip/venv | Rapide, standard agents-cli |
| Antérieur | Python 3.12 (pas 3.14) | Compat écosystème ADK |
| Antérieur | Kenney Racing Pack au lieu de `top-down-vehicles` (inexistant) | Vérification asset proactive |
| 3 juillet | **agents-cli au lieu d'adk direct** | Scaffolding + playground + observabilité + déploiement en un |
| 3 juillet | **ADK 2.0 « classique »** : `SequentialAgent(researcher → coder)`, state via `output_key` + template `{csr_summary}` | Plus fiable qu'un orchestrateur LLM ; le graph workflow `@node`/`Workflow`/`Event` n'a jamais été le code réel (correction 5 juil.) |
| 3 juillet | **WSL 2 sur Windows** | Meilleure compat MCP (npx), supporté officiellement par agents-cli |
| 3 juillet | **Manifeste d'assets en dur dans le prompt du Coder** | Contrer les hallucinations de chemins |
| 3 juillet | **Ajout d'un 3ème agent Reviewer** | Valider assets + richesse données + suggérer améliorations |
| 5 juillet | **Reviewer en mode RAPPORT** (pas de boucle), 3ᵉ `sub_agent` du `SequentialAgent` | Plus sûr à démontrer + aucun changement d'orchestration ; boucle = travail futur (décision verrouillée avec l'utilisateur) |
| 5 juillet | **Writeup + vidéo en EN**, docs racine migrés vers `docs/` | Jury international ; anti-drift (une seule source par doc) |
| 3 juillet | **Ajout d'un web MCP au Researcher** | Enrichir la biodiversité au-delà des fichiers locaux |
| 3 juillet | **Playground UI comme preuve MCP pour le jury** | Debug view montre chaque tool_use / tool_result |
| 3 juillet | **Documentation structurée dans le repo** | 8 fichiers markdown : voir section suivante |

### Questions techniques encore ouvertes
- **Choix du web MCP** : `mcp-server-fetch` (simple GET/scrape) vs `mcp-server-tavily` (recherche web) vs `mcp-server-brave-search` ? → recommandation actuelle : les deux (Tavily pour découvrir URLs, fetch pour récupérer contenu)
- ~~**Boucle Reviewer**~~ : ✅ **résolu** (Sprint 4). Choix = **mode rapport** dans le `SequentialAgent` à 3 nodes (pas de `LoopAgent`). Voir `DECISIONS.md`.
- ~~**Passage state entre agents en ADK 2.0**~~ : ✅ **résolu** (lecture de `app/agent.py`, 5 juil.). Le researcher a `output_key="csr_summary"` → sa réponse texte est écrite dans `session.state["csr_summary"]` ; le coder la récupère via le template `{csr_summary}` dans son instruction. Pas de `Context object`, pas d'edges explicites.

---

## 📂 Structure documentaire du repo

**État au 5 juillet 2026** :
```
eco-mine-generator/
├── CLAUDE.md                    ✅ créé — lu auto par Claude Code
├── GEMINI.md                    ✅ créé — lu auto par Gemini CLI (contenu synchronisé avec CLAUDE.md)
└── docs/
    ├── HANDOFF.md               ✅ ce document
    ├── ARCHITECTURE.md          ✅ créé (5 juil.) — pipeline, MCP wiring diagram
    ├── DECISIONS.md             ✅ créé — journal ADR-lite
    ├── AGENT_PROMPTS.md         ✅ créé — instructions littérales des agents
    └── ASSET_MANIFEST.md        ✅ créé — inventaire réel des assets (layout kenney/)
```

**Restent à créer dans `docs/`** :
```
├── PROJECT_CONTEXT.md       ← vision, pitch capstone, contraintes jury
├── ROADMAP.md               ← les 4 sprints avec cases à cocher (dupliqué ici pour l'instant)
└── GAMEPLAY_SPEC.md         ← scoring, obstacles, badges, narratif
```

---

## 🗺️ Roadmap 4 sprints

### Sprint 1 — Correction bloquants (1-2 jours) ✅ TERMINÉ (5 juillet 2026)
- [x] Fixer les prompts Researcher/Coder pour résoudre le message d'erreur — ✅ commit `9539133` (cause : chemin CSR non résolu) + durcissement prompts commit `06553a2`
- [x] Vérifier passage de données via `session.state` en ADK 2.0 — ✅ `output_key="csr_summary"` + template `{csr_summary}` (pas de Context object)
- [x] Prouver appels MCP via playground debug view (captures pour le jury) — ✅ captures baseline `docs/screenshots/sprint1-baseline/` (run complet sans erreur)
- [x] Créer `ASSET_MANIFEST.md` exhaustif — ✅ commits `25ee8e7` / `d9c1bc6` (layout `public/assets/kenney/`)
- [x] Ajouter manifeste au prompt du Coder + validation post-génération — ✅ commit `735b822` (contrainte d'assets + `missing_assets`)
- [x] Vérifier que `level_config.json` contient les données Clérac ET que `game.js` les affiche — ✅ validé sur captures baseline (labels courts, biome cohérent)

### Sprint 2 — Enrichissement narratif (1-2 jours) 🚨 EN COURS
- [x] **2.1** — Compte Tavily créé, clé API dans `.env` sur PC de test
- [x] **2.2** — Configurer `tavily-mcp` et `fetch-mcp` (dans `app/agent.py`, PAS le manifest — la config MCP est programmatique via `McpToolset`, pas dans `agents-cli-manifest.yaml`)
- [x] **2.3** — Brancher les 2 nouveaux MCP au Researcher (pas au Coder) — ✅ commit `95f6b8c`, `tools=[fs_read, web_search, web_fetch]`
- [ ] **2.4** — Test de connectivité MCP dans le playground + captures ← **POINT DE VALIDATION** (PC de test) : valide 2.3 **et** le batch 2.5-2.8 ci-dessous
- [x] **2.5** — Modifier le prompt Researcher pour exploiter le web — ✅ *code écrit, non testé* : nouvelle ÉTAPE 3 Tavily→Fetch dans `app/agent.py`
- [x] **2.6** — Étendre la biodiversité au-delà des chênes — ✅ *code écrit, non testé* : champ `biodiversity_species[]` (4-8 espèces web/CSR) + `headline_fact` en sortie Researcher. Espèces cibles : rollier d'Europe, guêpier, engoulevent, crapaud calamite, lézard ocellé, loutre, orchidées, bruyères, azuré du serpolet, oedipode
- [x] **2.7** — Générer histoire d'intro contextualisée — ✅ *code écrit, non testé* : `ui_strings.intro_story` généré par le Coder, rendu par une nouvelle `StoryScene` dans `game.js`
- [x] **2.8** — Messages contextuels in-game + récap de fin — ✅ *code écrit, non testé* : `ui_strings.eco_facts[]` (bannière 2s sur collecte éco) + `ui_strings.end_recap` (écran GAME OVER avec espèces défendues)

> ⚠️ **2.5-2.8 sont codés mais PAS encore validés** (machine d'édition, pas de pipeline).
> La prochaine session sur le PC de test doit faire UNE passe playground qui couvre 2.4
> (connectivité MCP) + vérifier que le Researcher renvoie `biodiversity_species`, que le
> Coder produit `intro_story`/`eco_facts`/`end_recap`, et que `game.js` les affiche
> (StoryScene → menu → faits in-game → récap). Voir « Prochaines actions ».

### Sprint 3 — Gameplay & Meta (1-2 jours) 🚨 EN COURS (code écrit, non testé)
- [x] Dynamite (explosion particules + camera shake, malus non fatal) — ✅ *code écrit* : `obstacles.dynamite` + `hitDynamite()` dans `game.js` v4
- [x] Zones d'eau (bande de ralentissement) — ✅ *code écrit* : `zones.water` + `spawnWaterZone()`/`playerInWater()`
- [x] Camions ennemis colorés (game over) — ✅ *code écrit* : `entities.enemy_trucks` + groupe `enemyTrucks`
- [x] Difficulté progressive (courbe config-driven) — ✅ *code écrit* : module `public/src/difficulty.js` (`getDifficulty`) + section `difficulty`
- [x] Pseudo joueur + leaderboard (localStorage) — ✅ *code écrit* : module `public/src/leaderboard.js` + `LeaderboardScene`
- [x] Badge Imerys Green (seuils config) — ✅ *code écrit* : `thresholds.green_badge` + `BadgeScene` (placeholder `assets/ui/badge_green.png`)
- [x] Schéma config étendu + exemple + prompt Coder — ✅ `docs/level_config_schema.md`, `public/configs/examples/level_config.sprint3.json`, `app/agent.py`
- [ ] Nuages de poussière derrière le camion joueur (Phaser ParticleEmitter) — reporté
- [ ] Sacs et big bags collectibles (icônes à trouver) — reporté
- [ ] Produits issus des minéraux (idée à préciser) — reporté
- [ ] Transformation en oiseau/animal au-delà d'un seuil de points Green — reporté
- [ ] Fond d'écran diversifié via Pillow (tile slicer avec blend des bords) — reporté

> ⚠️ **Tout le Sprint 3 est codé mais PAS validé** (machine d'édition). Prochaine session
> PC de test : servir `public/` et ouvrir
> `?config=configs/examples/level_config.sprint3.json` (rendu manuel), puis un run
> `agents-cli playground` pour vérifier que le Coder remplit les 5 sections. Voir
> `CHANGELOG.md` § Validation. `game.js` charge désormais en **ES module** → servir en
> HTTP (pas d'ouverture `file://`).

### Sprint 4 — Reviewer agent + démo (1 jour) 🚨 EN COURS (code+docs écrits, non testés)
- [x] Créer 3ème agent Reviewer dans le `SequentialAgent` ADK 2.0 — ✅ `reviewer_agent` ajouté aux `sub_agents` (`app/agent.py`), **mode rapport** (décision verrouillée)
- [x] Reviewer valide config sur 3 axes (schéma/plages, cohérence Clérac, équilibrage badge) → écrit `docs/reviews/review_<site>.md` — ✅ *code écrit, non testé*
- [x] Fixture cassée + runner de test Reviewer — ✅ `public/configs/examples/level_config.broken.json` + `tests/manual/run_reviewer.py`
- [x] Writeup Kaggle (EN) — ✅ `docs/kaggle_writeup.md` (squelette + intentions ; Results à remplir après tests)
- [x] Script vidéo (4 min, EN, 3 agents + compteur MCP) + checklist — ✅ `docs/video_script.md`, `docs/video_checklist.md`
- [ ] **Validation WSL** : Reviewer sur config cassé (FAIL attendu) + pipeline complet playground (PASS) + atteignabilité badge ← **PROCHAINE ACTION**
- [ ] Tourner la vidéo + remplir `docs/kaggle_writeup.md` § Results avec les chiffres réels (nb MCP calls, exemples configs/reviews)

---

## 🎮 Spec gameplay proposée (à valider)

### Système de points
- **Distance** : 1 pt/m
- **Collectibles miniers** :
  - Sac normal : 10 pts
  - Big bag : 50 pts
  - Minerai rare (kaolin pur, chamotte) : 100 pts
- **Collectibles biodiversité** (comptent double pour le badge) :
  - Œuf/nid : 25 pts + 1 point Green
  - Plante rare : 30 pts + 1 point Green
  - Sauvetage animal (transformation) : 200 pts + 5 points Green
- **Malus** :
  - Dynamite : -50 pts + ralentissement 2s
  - Écraser animal : -100 pts + -3 points Green
  - Camion adverse : game over
- **Multiplicateurs** :
  - Green Streak : x2 après 5 collectes bio sans dégât
  - Vitesse : x1.5 après 1000m, x2 après 2000m
- **Badge Imerys Green** : score > 5000 ET points Green > 30

### Obstacles
- Dynamite au sol (explosion en particules)
- Trous dans la route (sauter avec espace)
- Zones d'eau (contourner, ce sont des zones de biodiversité)
- Camions adverses (rouge/orange, apparaissent après 1500m, game over)
- Nuages de poussière (effet visuel derrière le joueur)
- Zones de biodiversité protégées (ralenti forcé si traversées)

### Narratif
- **Intro** : histoire générée par Researcher depuis web + fichiers
- **In-game** : pop-ups éducatifs à chaque collecte
- **Fin** : récap espèces sauvées + faits Clérac + badge éventuel

---

## 🌿 Biodiversité Clérac (à valider par le Researcher)

Site : carrière kaolin Imerys à Clérac, Charente-Maritime.

- **Faune** : rollier d'Europe, guêpier d'Europe, engoulevent, crapaud calamite, lézard ocellé, loutre
- **Flore** : chêne tauzin, orchidées (Ophrys), bruyères, genêts
- **Insectes** : azuré du serpolet, oedipode
- **Contexte industriel** : kaolin, chamotte, argile réfractaire

Le Researcher doit générer ces listes automatiquement via web MCP, pas les avoir en dur.

---

## 🔧 Prochaines actions concrètes

**Étape immédiate** : **UNE passe de validation playground** couvrant 2.4 (connectivité MCP) + le batch 2.5-2.8 (déjà codé sur la machine d'édition, jamais exécuté).

Sur la machine de test (WSL 2) :
1. `git pull /mnt/d/ecomine.bundle master`
2. Vérifier que `TAVILY_API_KEY` est présente dans le `.env` local (non synchronisé via bundle)
3. `uv sync` si besoin, puis `agents-cli playground` → `localhost:8080`
4. Lancer un run complet → vérifier dans la debug view :
   - `tool_use` **Tavily** puis **Fetch** côté Researcher (2.4 + 2.5), en plus du `read_text_file` du CSR
   - `csr_summary` contient `biodiversity_species` (4-8 espèces) + `headline_fact` (2.6)
   - `level_config.json` écrit par le Coder contient `intro_story` / `eco_facts` / `end_recap` (2.7 + 2.8)
5. Capturer ces événements pour le jury
6. **Rendu jeu** (testable sans agent) : servir `public/` (ex. `python -m http.server` dans `public/`) et vérifier `StoryScene` (intro) → menu → bannières de faits en jeu → écran GAME OVER avec récap + espèces. Le `level_config.json` committé porte déjà des valeurs Clérac étendues.

**⚠️ Point de vigilance identifié à l'édition** : la commande `npx @modelcontextprotocol/server-fetch` suit la consigne donnée, mais le serveur fetch officiel de référence est en **Python** (`uvx mcp-server-fetch`), pas npm. Si le premier `npx` renvoie un `404 npm`, basculer sur `uvx mcp-server-fetch` ou un port npm tiers (`fetcher-mcp`, `@kazuph/mcp-fetch`) — voir la note dans `docs/DECISIONS.md`.

**⚠️ 2e point** : les noms exacts des outils Tavily/Fetch ne sont pas connus (2.4 non fait). Les prompts les désignent de façon générique. Si l'agent n'appelle pas le bon outil, préciser le nom réel (visible dans la debug view / `agents-cli info`) dans le prompt Researcher.

**Après validation** : cocher définitivement 2.4-2.8, puis passer au Sprint 3 (polish gameplay).

---

## 📝 Notes personnelles

- Bertrand préfère un travail step-by-step avec instructions explicites
- Préférence pour manuel plutôt qu'automatisé quand feasible
- Toujours vérifier structure via `list_directory` (depth: 3) après scaffolding
- Pattern d'écriture fichiers : `mode: rewrite` premier chunk puis `mode: append`
- Assets Kenney : les noms ne matchent pas toujours la réalité, toujours vérifier

---

## 🔗 Ressources externes

- agents-cli : https://google.github.io/agents-cli/
- ADK docs : https://google.github.io/adk-docs/
- Kenney Racing Pack : https://kenney.nl/assets/racing-pack
- OpenGameArt animal-pack-redux (fallback)
- Phaser 3 : https://phaser.io/

---

*Fin du document HANDOFF. À jour au 5 juillet 2026. Sprints 2–3 codés (validation WSL en
attente) ; **Sprint 4** : Reviewer (mode rapport) + writeup + script vidéo écrits, validation
WSL à faire (Reviewer sur config cassé → FAIL, pipeline complet → PASS, badge atteignable).*
