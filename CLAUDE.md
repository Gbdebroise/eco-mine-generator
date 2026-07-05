# Eco-Mine Generator / Mission Clérac — Guide Agent Codeur

Projet capstone **Google × Kaggle AI Agents Intensive Vibe Coding** : jeu endless
runner Phaser 3 dont le contenu est généré dynamiquement par une pipeline
multi-agents ADK 2.0. Thème : carrière de kaolin Imerys à Clérac
(Charente-Maritime), mining vs biodiversité.

## 📚 Où trouver le contexte

**Toujours lire `docs/HANDOFF.md` en début de session** : état actuel, décisions,
roadmap, prochaine action.

Documents détaillés dans `docs/` :

| Fichier | Contenu | Consulter avant de… |
|---------|---------|---------------------|
| `HANDOFF.md` | **Source de vérité** : état, décisions, roadmap | Toute session |
| `PROJECT_CONTEXT.md` | Vision, pitch capstone, contraintes jury | Comprendre le "pourquoi" |
| `ARCHITECTURE.md` | Pipeline agents, ADK 2.0, MCPs, flux state | Toucher `app/agent.py` |
| `DECISIONS.md` | Journal ADR-lite | Proposer un nouveau choix technique |
| `ROADMAP.md` | 4 sprints avec cases à cocher | Planifier une session de travail |
| `AGENT_PROMPTS.md` | Instructions littérales des 3 agents | Modifier un prompt d'agent |
| `ASSET_MANIFEST.md` | Liste exhaustive des assets réels sur disque | Référencer un asset dans le code |
| `GAMEPLAY_SPEC.md` | Scoring, obstacles, badges, narratif | Modifier `game.js` ou `level_config.json` |

## 🛠️ Environnement technique

- **OS** : WSL 2 sur Windows (natif Windows interdit — casse les MCP `npx`)
- **Chemin projet** : `/mnt/c/Users/bertr/Documents/PROJETS/eco-mine-generator` (côté WSL)
- **Python** : 3.12 (pas 3.14)
- **Package manager** : `uv` uniquement (jamais `pip` ni `venv`)
- **Node** : 24.x
- **Framework agents** : ADK 2.0 « classique » — `SequentialAgent(researcher_agent → coder_agent)`, passage de state via `output_key` + template `{csr_summary}` (PAS le graph workflow `@node`/`Workflow`/`Event` : voir `app/agent.py` et `docs/AGENT_PROMPTS.md`)
- **Wrapper** : `agents-cli` — installé via `uv tool install google-agents-cli`
- **Playground debug view** : `http://localhost:8080` — c'est LA source de vérité pour prouver les appels MCP au jury

## ⚠️ Règles projet

1. **Avant tout ajout ou référence d'asset** → vérifier qu'il existe dans `docs/ASSET_MANIFEST.md`. Le Coder ne doit JAMAIS référencer un asset absent du manifeste (problème d'hallucination récurrent).
2. **Avant toute modification de prompt d'agent** → lire `docs/AGENT_PROMPTS.md`, mettre à jour ce fichier ET le code en même temps.
3. **Avant toute décision technique nouvelle** → ajouter une entrée dans `docs/DECISIONS.md` (format ADR-lite : date, décision, raison, alternative rejetée).
4. **Après chaque session significative** → mettre à jour `docs/ROADMAP.md` (cases à cocher) et `docs/HANDOFF.md` (état actuel).
5. **Config-driven generation** : le Coder ne produit qu'un `level_config.json` (~15 lignes), jamais du code Phaser complet. Le `game.js` est hand-coded et stable.
6. **Preuve MCP** : chaque fonctionnalité qui utilise le MCP doit être testable et démontrable via la debug view du playground. C'est une exigence du jury capstone.
7. **Ne jamais commit de clés API** : `.env` doit rester dans `.gitignore`.

## 🎯 Sprint en cours

**Sprint 4 — Reviewer, démo & writeup Kaggle** (voir `docs/HANDOFF.md` pour l'état détaillé)

Pipeline désormais à **3 agents** : `SequentialAgent(researcher → coder → reviewer)` dans
`app/agent.py`. Le **Reviewer** (mode **rapport**, décision verrouillée) relit le
`level_config.json`, le valide sur 3 axes (schéma/plages, cohérence thématique Clérac,
équilibrage badge) et écrit `docs/reviews/review_<site>.md`.

Priorité immédiate : **validation WSL** — Reviewer sur config cassé
(`tests/manual/run_reviewer.py` → verdict FAIL attendu), puis pipeline complet en playground
(verdict PASS + `write_file` du rapport visible), puis tournage vidéo et remplissage de
`docs/kaggle_writeup.md` § Results.

---

## 💻 Contexte d'exécution (IMPORTANT)

**Ce projet se développe sur deux machines distinctes.**

### Machine actuelle (édition uniquement)
- **Rôle** : édition de code, discussion, rédaction de docs
- **OS** : Windows natif (PAS de WSL 2 ici, pas de pipeline installé)
- **NE PAS exécuter** : `agents-cli`, `uv run`, `pytest`, ou tout script Python du projet
- Si un test est nécessaire, il faut **suggérer la commande** à lancer sur l'autre PC, jamais l'exécuter ici

### Machine de test (exécution)
- **Rôle** : exécution du pipeline, `agents-cli playground`, captures debug view, tests
- **OS** : WSL 2 avec `uv`, `agents-cli`, Node 24, MCP servers configurés
- **Chemin** : équivalent WSL du projet (ex. `/mnt/c/.../eco-mine-generator`)

### Sync entre les deux via Git bundle sur clé USB

Aucun compte GitHub partagé possible → sync manuelle par fichier bundle.

**Après une session d'édition sur cette machine** :
```bash
git add .
git commit -m "Sprint X: description concise"
git bundle create /d/ecomine.bundle master     # /d/ = clé USB
```

**Sur la machine de test** :
```bash
git pull /mnt/d/ecomine.bundle master           # /mnt/d/ = clé USB en WSL 2
uv sync                                          # reconstruire l'env si dépendances changées
agents-cli playground                            # tester
```

### Ne JAMAIS copier via la clé USB
- `.venv/` — reconstructible avec `uv sync`
- `__pycache__/`, `.pytest_cache/` — caches Python
- `.env` — clés API, configurer manuellement sur chaque PC
- `node_modules/` — reconstructible avec `npm install`

Ces exclusions sont dans `.gitignore` donc automatiquement ignorées par `git bundle`.

### Règle pour l'assistant IA

Sur cette machine, l'assistant ne peut PAS vérifier lui-même le comportement du code. Il doit :
1. Proposer les modifications de code/prompts
2. Suggérer les commandes à lancer sur l'autre PC (`agents-cli playground`, `pytest`, etc.)
3. Attendre les retours de test de l'utilisateur avant d'itérer
4. Rappeler à l'utilisateur de commit + bundle avant la sync

---

## 🏗️ Phases de développement (agents-cli standard)

### Phase 1 : Comprendre les besoins
Avant d'écrire du code, comprendre les besoins du projet, les contraintes et les critères de succès. Toujours lire `docs/HANDOFF.md` d'abord.

### Phase 2 : Implémenter
Implémenter la logique agent dans `app/`. Utiliser `agents-cli playground` pour tester interactivement. Itérer selon les retours utilisateur.

### Phase 3 : Boucle d'évaluation (phase d'itération principale)
Commencer avec 1-2 cas d'éval, exécuter `agents-cli eval generate`, puis `agents-cli eval grade`, itérer en faisant des modifs et en relançant les deux commandes jusqu'à satisfaction. Compter 5-10+ itérations. Une fois une baseline établie, utiliser `agents-cli eval compare` (diffs de régression), `agents-cli eval analyze` (clustering des modes d'échec), et `agents-cli eval optimize` (auto-tuning des prompts).

### Phase 4 : Tests pré-déploiement
Exécuter `uv run pytest tests/unit tests/integration`. Corriger jusqu'à ce que tous les tests passent.

### Phase 5 : Déploiement en dev
**Nécessite l'approbation explicite de l'utilisateur.** Exécuter `agents-cli deploy` uniquement après confirmation utilisateur.

### Phase 6 : Déploiement en production
Demander à l'utilisateur : Option A (single-project simple) ou Option B (pipeline CI/CD complet avec `agents-cli infra cicd`).

## 📟 Commandes de développement

| Commande | Objectif |
|----------|----------|
| `agents-cli playground` | Test interactif local (debug view sur localhost:8080) |
| `agents-cli install` | Installer les dépendances du projet |
| `agents-cli lint` | Vérifier la qualité du code |
| `agents-cli info` | Afficher config + skills installées |
| `uv run pytest tests/unit tests/integration` | Tests unitaires et d'intégration |
| `agents-cli eval dataset synthesize` | Synthétiser des scénarios multi-turn |
| `agents-cli eval generate` | Exécuter l'agent sur le dataset, produire des traces |
| `agents-cli eval grade` | Évaluer les traces |
| `agents-cli eval compare` | Comparer deux résultats (régression) |
| `agents-cli eval analyze` | Clusteriser les modes d'échec |
| `agents-cli eval metric list` | Lister les métriques SDK |
| `agents-cli eval optimize` | Auto-tuner les prompts |
| `agents-cli infra single-project` | Configurer l'infra projet (Terraform) |
| `agents-cli deploy` | Déployer en dev |
| `agents-cli scaffold enhance` | Ajouter target de déploiement ou CI/CD |
| `agents-cli scaffold upgrade` | Upgrader le projet vers la dernière version |

## 🧭 Guidelines opérationnelles

- **Préservation du code** : ne modifier que le code directement ciblé par la demande. Préserver le code environnant, les valeurs de config (ex. `model`), les commentaires et le formatage.
- **NE JAMAIS changer le modèle** sauf demande explicite.
- **Erreurs 404 sur modèle** : corriger `GOOGLE_CLOUD_LOCATION` (ex. `global` au lieu de `us-east1`), pas le nom du modèle.
- **Import des tools ADK** : importer l'instance du tool, pas le module : `from google.adk.tools.load_web_page import load_web_page`
- **Exécuter Python avec `uv`** : `uv run python script.py`. Lancer `agents-cli install` en premier.
- **Arrêter sur erreurs répétées** : si la même erreur apparaît 3+ fois, corriger la cause racine au lieu de retry.
- **Conflits Terraform** (Error 409) : utiliser `terraform import` au lieu de retry la création.

## 🧭 Workflow type de session

1. Ouvrir `docs/HANDOFF.md` → identifier la prochaine action
2. Ouvrir les docs `docs/*.md` pertinents au type de modification
3. Modifier le code + mettre à jour les docs concernés en parallèle
4. Tester dans `agents-cli playground` avec capture debug view si MCP touché
5. Mettre à jour `docs/ROADMAP.md` et `docs/HANDOFF.md` en fin de session
