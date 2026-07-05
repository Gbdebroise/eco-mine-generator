# DECISIONS — Journal ADR-lite

> Format : date, contexte, décision, alternative rejetée, impact attendu.
> Une entrée par décision technique significative. Voir règle CLAUDE.md #3.

---

## 2026-07-05 — Sprint 1 : correction prompts Researcher et Coder

**Contexte** : Les captures baseline du 5 juil. (`docs/screenshots/sprint1-baseline/`)
montrent que le pipeline `SequentialAgent(researcher → coder)` tourne **de bout en
bout sans erreur** — le refus historique « Je ne suis pas en mesure de générer des
jeux » a déjà été corrigé (commit `9539133`) et n'apparaît plus. Mais deux défauts
restent visibles :
1. **Fences markdown** : la capture *State* (`2026-07-05_13-54-46.png`) montre
   `csr_summary` stocké sous forme de string enveloppée dans ```` ```json … ``` ````,
   malgré l'instruction « Pas de markdown ». Fragile pour tout consommateur qui
   ferait un `json.loads` strict (futur agent Reviewer).
2. **Valeurs verbeuses** : la capture *Events* (`2026-07-05_13-53-06.png`) montre
   `eco_target = "Migratory birds, monitored through annual bird-banding (ringing)
   campaigns with the Museum National d'Histoire Naturelle (MNHN)…"` — une phrase
   entière recopiée du fichier, inadaptée à l'affichage (le moteur `game.js` attend
   des labels courts, ex. `"Migratory Birds (MNHN)"`).

**Décision** : Renforcer **uniquement les deux prompts** dans `app/agent.py`, sans
toucher aux modèles (`gemini-2.5-flash` / `gemini-2.5-pro`), aux tools MCP, à
`output_key`, ni à la structure `SequentialAgent`.
- **Researcher** : (a) déclarer explicitement que sa tâche est l'**extraction
  documentaire** (jamais la génération de jeu) → verrou anti-refus par robustesse ;
  (b) produire des **labels courts** (2-4 mots) fidèles au fichier plutôt que des
  phrases entières ; (c) interdiction stricte des fences (réponse commençant par `{`
  et finissant par `}`).
- **Coder** : (a) **tolérer** d'éventuels fences/texte autour en entrée et ne parser
  que l'objet JSON ; (b) recopier les labels courts sans les rallonger.
- **Passage de state inchangé** : `output_key="csr_summary"` (écrit dans
  `session.state`) + template `{csr_summary}` côté coder. C'est le mécanisme ADK 2.0
  idiomatique, déjà fonctionnel et prouvé par les captures.

**Alternative rejetée** :
- **`output_schema` Pydantic sur le Researcher** (pour forcer un JSON propre sans
  fences) → **rejeté** : en ADK, un `LlmAgent` doté d'un `output_schema` ne peut plus
  appeler d'outils, or le Researcher a besoin du MCP filesystem pour lire le CSR.
  Incompatible.
- **`after_agent_callback` qui strip les fences** → **reporté** : non nécessaire tant
  qu'aucun consommateur ne parse `csr_summary` en JSON strict (le Coder `pro` le
  tolère). À reconsidérer à l'arrivée de l'agent Reviewer (Sprint 4).
- **Introduire un « Context object »** pour passer le state → **rejeté** : n'existe
  pas dans ce montage ADK 2.0 ; `output_key` remplit déjà ce rôle. Le changer
  casserait un pipeline qui marche.

**Impact attendu** (à valider sur le PC de test via `agents-cli playground`) :
- `csr_summary` = JSON propre, sans fences → onglet *State* montre un objet, pas une
  string markdown.
- `eco_target` / `mineral_name` / `danger_obstacle` = labels courts → `ui_strings`
  lisibles à l'écran, cohérents avec le `DEFAULT_CONFIG` de `game.js`.
- Le Researcher n'émet jamais de message de refus.
- `level_config.json` régénéré cohérent avec la version committée le 5 juil.

---

## 2026-07-05 — Contrainte d'assets du Coder via manifeste MCP

**Contexte** : Problème récurrent d'hallucination de chemins d'assets (le Coder
référençait des fichiers absents du disque — cf. règle CLAUDE.md #1). On vient de
constituer `docs/ASSET_MANIFEST.md` (inventaire réel, layout `public/assets/kenney/`).
Il faut que le Coder s'y contraigne au moment de générer `level_config.json`.

**Décision** : Ajouter une section `CONTRAINTE D'ASSETS` au prompt du Coder qui lui
impose de **lire `docs/ASSET_MANIFEST.md` via `read_text_file` (MCP filesystem)** avant
d'écrire le config, de n'utiliser QUE les chemins listés, de signaler tout asset absent
dans un champ `missing_assets` (au lieu d'inventer), et de vérifier que chaque chemin
commence par `assets/`.

**Pourquoi le manifeste dans `docs/` et pas en dur dans le prompt** :
- Source de vérité **unique et versionnée** : un seul endroit à mettre à jour quand on
  ajoute/retire un asset ; le prompt ne dérive jamais du disque.
- **Auditabilité** : le manifeste est relu par un humain et (bientôt) par le Reviewer ;
  un prompt gonflé de centaines de chemins n'est ni lisible ni diffable proprement.

**Pourquoi le Coder LIT le manifeste via MCP (au lieu d'injection au prompt-time)** :
- **Preuve MCP pour le jury** : la lecture génère un `tool_use` `read_text_file` visible
  dans la debug view du playground — démonstration exigée par le capstone.
- **Fraîcheur** : le Coder lit toujours la version courante du fichier sur disque, pas
  une copie figée au moment du build du prompt.
- **Cohérence architecturale** : même canal MCP que le Researcher (`app/imerys_csr_data.txt`).

**Alternative rejetée** : Lister les assets directement dans l'instruction system du
Coder → **rejeté** car (a) ça alourdit massivement le prompt (1133 fichiers), (b) ce
n'est pas maintenable (double source de vérité prompt/disque, dérive garantie), (c) on
perd la preuve MCP (aucun `tool_use` généré).

**Impact attendu** : le Coder produit un `tool_use read_text_file('docs/ASSET_MANIFEST.md')`
avant `write_file`, ne référence aucun chemin hors manifeste, et déclare les manques via
`missing_assets`. Note : le schéma actuel du config ne porte encore aucun chemin d'asset
(`game.js` charge via `OBJECT_ASSETS`), donc la contrainte est surtout un garde-fou +
preuve MCP tant que le config ne référence pas d'assets. À valider dans la debug view.

---

## 2026-07-05 - Ajout web MCP au Researcher

**Contexte** : la biodiversité et le contexte narratif ne peuvent pas venir
uniquement de `imerys_csr_data.txt` (trop pauvre).

**Décision** : Tavily pour la découverte de sources + fetch pour la lecture du
contenu. Les deux MCP sont branchés **au Researcher uniquement** (`tools=[fs_read,
web_search, web_fetch]` dans `app/agent.py`) ; le Coder reste confiné au filesystem.
Clé `TAVILY_API_KEY` passée au serveur `tavily-mcp` via `env` depuis `.env`. Prompts
Researcher/Coder **inchangés à ce stade** (l'exploitation des nouveaux outils sera
prompted dans une étape ultérieure, une fois la config MCP validée en playground).

**Alternative rejetée** : fetch seul (impossible de découvrir de nouvelles URLs sans
moteur de recherche).

**Alternative rejetée** : Brave (Tavily est spécifiquement conçu pour les agents IA,
meilleurs résultats structurés).

**Impact attendu** (à valider sur le PC de test via `agents-cli playground`) : un run
Researcher qui interroge le web produit des `tool_use` Tavily puis Fetch visibles dans
la debug view, en plus du `read_text_file` sur le CSR. Prérequis : `TAVILY_API_KEY`
présente dans `.env`, et disponibilité des paquets npm `tavily-mcp` /
`@modelcontextprotocol/server-fetch` au premier `npx`.

---

## 2026-07-05 — Sprint 2 : contrat narratif (biodiversité, intro, in-game, récap)

**Contexte** : étapes 2.5→2.8. Le jeu affichait des labels bruts sans contexte. On veut
un contenu narratif **généré par les agents** (argument capstone) : biodiversité élargie,
histoire d'intro, messages éducatifs en jeu, récap de fin.

**Décision** : étendre le **contrat de données** du pipeline sans changer les rôles
(règle CLAUDE.md #5 : le Coder ne produit qu'un `level_config.json`, `game.js` est le
moteur fixe qui le consomme).
- **Researcher** (extraction + web) ajoute 2 clés à `csr_summary` : `headline_fact`
  (phrase source) et `biodiversity_species` (4-8 espèces réelles, web-enrichies).
- **Coder** (assemblage + narration) ajoute `biodiversity_species` (passthrough) et 3
  textes dans `ui_strings` : `intro_story`, `eco_facts[]`, `end_recap`.
- **`game.js`** (édité à la main) gagne : une `StoryScene` (intro avant menu), une
  bannière 2s `showFact()` sur collecte éco (rotation `eco_facts`), et un écran de fin
  enrichi (`end_recap` + espèces). `DEFAULT_CONFIG` porte des valeurs Clérac par défaut.

**Séparation des responsabilités** — pourquoi l'intro/facts/recap côté **Coder** et pas
Researcher : le Researcher est `flash`, cadré « extraction, jamais de génération » ; la
rédaction narrative est une tâche créative confiée au Coder `pro`, qui compose déjà les
`ui_strings`. Le Researcher fournit la matière première (espèces + fait source).

**Alternative rejetée** : intro/facts générés par le Researcher → **rejeté**, brouille
le verrou anti-refus « tu fais de l'extraction, pas de la génération » et mélange data et
prose dans `csr_summary`.

**Alternative rejetée** : intro affichée directement dans le `MenuScene` → **rejeté**,
l'écran (480×640) est déjà chargé (titre, légende, bouton) ; une `StoryScene` dédiée est
plus lisible et n'entre pas en collision avec le layout existant.

**Alternative rejetée** : faire générer le HTML/JS du jeu par le Coder → **rejeté**
(règle #5, source d'hallucinations). Toute nouveauté visuelle passe par une clé de config
+ un rendu hand-coded dans `game.js`.

**Impact attendu** (à valider en playground, étape 2.4) : `level_config.json` gagne
`biodiversity_species` + `intro_story`/`eco_facts`/`end_recap` ; le jeu affiche l'intro,
des faits en cours de partie, et un récap contextualisé. `game.js` reste rétro-compatible
(merge `DEFAULT_CONFIG` → clés manquantes = fallback Clérac).

---

## 2026-07-05 — Sprint 3 : extension du schéma config (5 sections gameplay)

**Contexte** : le gameplay se limitait à 3 spawns (mineral/bird/blast+grove) et une rampe
de vitesse en dur (`speed += 25` toutes les 10 s). Insuffisant pour un jury (mécaniques
variées, difficulté qui monte). On veut enrichir SANS violer la règle #5 (config-driven :
l'agent ne touche pas `game.js`).

**Décision** : ajouter **5 sections top-level** au `level_config.json` — `obstacles.dynamite`,
`zones.water`, `entities.enemy_trucks`, `difficulty`, `thresholds.green_badge` — toutes
**optionnelles avec défauts** dans le loader de `game.js` (`mergeConfig`). Le contrat complet
est figé dans le nouveau `docs/level_config_schema.md`, avec un exemple canonique
`public/configs/examples/level_config.sprint3.json`. Le prompt du Coder reçoit les 5 sections
+ des plages de valeurs + un garde-fou « jamais de `spawn_weight` à 0 ».

**Rétro-compatibilité** : exigence explicite du sprint. Un config Sprint 2 (sans ces sections)
doit booter à l'identique → chaque section absente est complétée par `DEFAULT_CONFIG`, et
`difficulty.speed_start_px_per_s` retombe sur le `scrolling_speed` legacy.

**Alternative rejetée** : renommer/supprimer `scrolling_speed` au profit de `difficulty` →
**rejeté**, casserait les configs existants. On le garde comme fallback.

**Alternative rejetée** : faire générer les nouvelles mécaniques en code Phaser par le Coder →
**rejeté** (règle #5). Data-only + moteur hand-coded.

**Impact attendu** : `agents-cli` produit un config avec les 5 sections remplies dans les
plages ; `game.js` v4 les consomme. À valider en playground + rendu manuel.

---

## 2026-07-05 — Sprint 3 : `game.js` en ES modules (`src/difficulty.js`, `src/leaderboard.js`)

**Contexte** : le sprint demande deux modules réutilisables et testables — `getDifficulty`
(courbe de difficulté) et une API leaderboard (`add`/`getTop`/`clear`) — en vue de l'éval du
Sprint 4. `game.js` était jusque-là un unique `<script>` classique référençant le global
`Phaser` (CDN).

**Décision** : passer le chargement de `game.js` en `<script type="module">` (dans
`public/index.html`) et extraire la logique dans `public/src/difficulty.js` +
`public/src/leaderboard.js` avec de vrais `export`. `game.js` les `import`. Phaser reste un
global CDN (accessible depuis un module). Les deux modules sont **purs / dégradation douce**
(pas de dépendance Phaser) → importables tels quels en Node pour les tests Sprint 4.

**Alternative rejetée** : scripts classiques attachant `window.Difficulty` / `window.Leaderboard`
→ **rejeté**, moins propre pour l'éval (pas d'`import` direct, pollution du global). Choix
confirmé avec l'utilisateur.

**Conséquence / limite** : les ES modules imposent de servir le jeu en HTTP (`python -m
http.server`) — l'ouverture directe en `file://` est cassée par la politique CORS des modules.
Sans impact : le workflow de test passe déjà par un serveur HTTP.

---

## 2026-07-05 — Sprint 3 : override `?config=` + dynamite distincte du `blast`

**Contexte** : (1) besoin de tester le config d'exemple Sprint 3 sans lancer d'agent ni
écraser le `level_config.json` live. (2) La dynamite (malus, non fatale) et la « Blasting
Zone » (`blast`, game over) sont deux dangers de nature différente.

**Décision** :
- **`?config=<chemin>`** : `BootScene` lit un paramètre d'URL optionnel et charge ce config
  à la place de `level_config.json`. Non destructif, testable :
  `http://localhost:8000/?config=configs/examples/level_config.sprint3.json`. Choix confirmé
  avec l'utilisateur.
- **Dynamite ≠ blast** : la dynamite (`obstacles.dynamite`) applique `score_malus` +
  `green_malus` et continue la partie ; le `blast` historique (`danger_obstacle`) reste un
  game over immédiat, au même titre que le nouveau `enemy_truck`. Deux groupes physiques
  distincts dans `game.js`.

**Alternative rejetée** : copier l'exemple sur `public/level_config.json` pour le tester →
**rejeté**, destructif (écrase la sortie d'agent) et non rejouable. Le `?config=` est
non-invasif.

**Alternative rejetée** : réutiliser le sprite/groupe `blast` pour la dynamite → **rejeté**,
sémantique et effet opposés (fatal vs malus) ; garder deux entités évite les bugs de collision.

**Impact attendu** : test manuel du gameplay Sprint 3 possible sans pipeline ; scoring et
game over cohérents (blast + enemy_truck = fatal ; dynamite + grove = malus).
