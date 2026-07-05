# HANDOFF — Eco-Mine Generator / Mission Clérac

> **Date** : 3 juillet 2026
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

On en est au Sprint 1 : corriger l'architecture de la pipeline (message d'erreur du 
Researcher, preuve MCP, hallucinations d'assets). Prochaine action concrète : 
réécrire les instructions des agents Researcher et Coder. Stack : agents-cli 
+ ADK 2.0 « classique » (SequentialAgent, state via output_key + template). 

IMPORTANT : je développe sur un PC (Windows natif, édition uniquement) et je teste 
sur un autre PC (WSL 2, pipeline complet). Sync via git bundle sur clé USB. 
Ne me propose pas d'exécuter agents-cli, uv run ou pytest sur la machine 
d'édition — ils ne sont pas installés ici.
```

---

## 📌 État actuel du projet (au 3 juillet 2026)

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
    ↓ session.state["clerac_data"]
Coder (génère level_config.json ~15 lignes)
    ↓ session.state["level_config"]
Reviewer [À CRÉER] (valide assets, richesse données, suggère améliorations)
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
| 3 juillet | **Ajout d'un web MCP au Researcher** | Enrichir la biodiversité au-delà des fichiers locaux |
| 3 juillet | **Playground UI comme preuve MCP pour le jury** | Debug view montre chaque tool_use / tool_result |
| 3 juillet | **Documentation structurée dans le repo** | 8 fichiers markdown : voir section suivante |

### Questions techniques encore ouvertes
- **Choix du web MCP** : `mcp-server-fetch` (simple GET/scrape) vs `mcp-server-tavily` (recherche web) vs `mcp-server-brave-search` ? → recommandation actuelle : les deux (Tavily pour découvrir URLs, fetch pour récupérer contenu)
- **Boucle Reviewer** : simple `SequentialAgent` avec 3 nodes ou `LoopAgent` qui itère jusqu'à validation ?
- ~~**Passage state entre agents en ADK 2.0**~~ : ✅ **résolu** (lecture de `app/agent.py`, 5 juil.). Le researcher a `output_key="csr_summary"` → sa réponse texte est écrite dans `session.state["csr_summary"]` ; le coder la récupère via le template `{csr_summary}` dans son instruction. Pas de `Context object`, pas d'edges explicites.

---

## 📂 Structure documentaire du repo

**Déjà en place (3 juillet 2026)** :
```
eco-mine-generator/
├── CLAUDE.md                    ✅ créé — lu auto par Claude Code
├── GEMINI.md                    ✅ créé — lu auto par Gemini CLI (contenu synchronisé avec CLAUDE.md)
└── docs/
    └── HANDOFF.md               ✅ ce document
```

**Restent à créer dans `docs/`** :
```
├── PROJECT_CONTEXT.md       ← vision, pitch capstone, contraintes jury
├── ARCHITECTURE.md          ← pipeline, ADK 2.0, MCPs, flux de données
├── DECISIONS.md             ← journal ADR-lite (tableau ci-dessus l'amorce)
├── ROADMAP.md               ← les 4 sprints avec cases à cocher
├── AGENT_PROMPTS.md         ← instructions littérales des 3 agents
├── ASSET_MANIFEST.md        ← table exhaustive assets réels + URLs sources
└── GAMEPLAY_SPEC.md         ← scoring, obstacles, badges, narratif
```

**Plan de rédaction restant :**
- **Option A** (rapide) : rédiger les 4 docs stratégiques (PROJECT_CONTEXT, DECISIONS, ROADMAP, GAMEPLAY_SPEC) dans le chat, copier-coller dans le repo
- **Option B** : rédiger les 3 docs techniques (ARCHITECTURE, AGENT_PROMPTS, ASSET_MANIFEST) dans Claude Code qui a accès au code réel

---

## 🗺️ Roadmap 4 sprints

### Sprint 1 — Correction bloquants (1-2 jours) 🚨 EN COURS
- [ ] Fixer les prompts Researcher/Coder pour résoudre le message d'erreur
- [x] Vérifier passage de données via `session.state` en ADK 2.0 — ✅ `output_key="csr_summary"` + template `{csr_summary}` (pas de Context object)
- [ ] Prouver appels MCP via playground debug view (captures pour le jury)
- [ ] Créer `ASSET_MANIFEST.md` exhaustif
- [ ] Ajouter manifeste au prompt du Coder + validation post-génération
- [ ] Vérifier que `level_config.json` contient les données Clérac ET que `game.js` les affiche

### Sprint 2 — Enrichissement narratif (1-2 jours)
- [ ] Ajouter web MCP au Researcher (fetch + Tavily probable)
- [ ] Étendre biodiversité au-delà des chênes : rollier d'Europe, guêpier, engoulevent, crapaud calamite, lézard ocellé, loutre, orchidées, bruyères, azuré du serpolet, oedipode
- [ ] Générer histoire d'intro contextualisée (« Bertrand, ingénieur Imerys, vous appelle en renfort... »)
- [ ] Messages contextuels en cours de jeu (pop-up 2s à chaque collecte)
- [ ] Récap de fin avec faits Clérac + espèces sauvées

### Sprint 3 — Polish gameplay (1-2 jours)
- [ ] Nouveaux obstacles : bâtons de dynamite (avec explosion Pillow), trous, zones d'eau, camions adverses colorés
- [ ] Nuages de poussière derrière le camion joueur (Phaser ParticleEmitter)
- [ ] Sacs et big bags collectibles (icônes à trouver)
- [ ] Produits issus des minéraux (idée à préciser)
- [ ] Transformation en oiseau/animal au-delà d'un seuil de points Green
- [ ] Difficulté progressive (`speed *= 1.1` tous les 500m, nouveaux obstacles tous les 1000m)
- [ ] Pseudo joueur + leaderboard (localStorage ou window.storage shared)
- [ ] Badge Imerys Green (SVG arbre doré, débloqué si score > 5000 ET points Green > 30)
- [ ] Fond d'écran diversifié via Pillow (tile slicer avec blend des bords)

### Sprint 4 — Reviewer agent + démo (1 jour)
- [ ] Créer 3ème agent Reviewer dans le `SequentialAgent` ADK 2.0 (ajouter un `LlmAgent` aux `sub_agents`)
- [ ] Reviewer valide assets, note richesse contenu, suggère améliorations
- [ ] Capture démo vidéo montrant les 3 agents + debug view MCP
- [ ] Writeup Kaggle
- [ ] Script vidéo 5 minutes

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

**Étape immédiate** : commencer Sprint 1, action 1 → **réécrire les instructions du Researcher et du Coder**.

Pour ça il faut (sur la machine d'édition) :
1. Ouvrir le code actuel de `app/agent.py` (Claude Code idéal ici)
2. Extraire les prompts existants → les mettre dans `docs/AGENT_PROMPTS.md`
3. Les réécrire en tenant compte de :
   - Le Researcher doit accepter la sous-tâche « extrait données Clérac » sans refuser
   - Le Coder doit consommer explicitement `state["clerac_data"]`
   - Le Coder doit référencer UNIQUEMENT les assets du manifeste
4. `git add . && git commit -m "Sprint 1: fix agent prompts"`
5. `git bundle create /d/ecomine.bundle master` (clé USB)

Puis (sur la machine de test) :
6. `git pull /mnt/d/ecomine.bundle master`
7. `agents-cli playground` → tester dans le debug view sur `localhost:8080`
8. Capturer les événements `tool_use` / `tool_result` MCP pour le jury

**Question à trancher avant** : version exacte d'ADK 2.0 utilisée et syntaxe précise pour passer le state entre nodes (à confirmer en regardant le code réel côté Claude Code).

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

*Fin du document HANDOFF. À jour au 3 juillet 2026.*
