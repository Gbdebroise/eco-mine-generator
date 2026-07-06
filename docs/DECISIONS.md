# DECISIONS — Journal ADR-lite

> Format : date, contexte, décision, alternative rejetée, impact attendu.
> Une entrée par décision technique significative. Voir règle CLAUDE.md #3.

---

## 2026-07-06 (background) — Fond carrière : tuile seamless au lieu d'une vignette tilée

**Contexte** : Au run, le background défilait mal (coutures, cadrage bancal) alors que la
photo était bonne (« sol de carrière »). Inspection : `clay_quarry_far.png` (480×256) et
`clay_quarry_near.png` (480×384) sont des **vignettes encadrées** (scène complète avec
bordure rocheuse / bords déchirés transparents), mais `game.js` les passe dans un
`tileSprite` qui **répète** la texture pour le scroll infini → les bordures se répètent en
bandes qui défilent. Inadéquation asset ↔ technique de rendu, pas un bug d'agent (aucun
agent ne touche `game.js` ni les assets — rappel règle #5 : le pipeline ne produit que
`level_config.json`).

**Décision** : Régénérer la **couche visible** (`_near`, opaque, dessinée au-dessus du
`_far`) en une vraie **tuile de sol raccordable verticalement** :
crop de l'intérieur opaque (boîte 417×346, marge de sécurité) → composite sur teinte terre
→ resize largeur 480 → **feather-wrap** vertical (fondu haut↔bas, f=76) via System.Drawing
en PowerShell. Résultat 480×322, opaque, couture mesurée à 24.5 delta RGB vs 19.8 de
variation interne (≈ imperceptible). Fichier écrit sur `clay_quarry_near.png` →
**aucune modification de `game.js`** (il charge déjà `assets/<biome>_near.png`). Le `_far`
aérien devient totalement masqué (near opaque) : conservé mais non tilé.

**Alternative rejetée** :
- **Recadrage à la volée dans `game.js`** (frame interne du `tileSprite`) → rejeté :
  couture centrale subsistante (image pas vraiment raccordable) et logique de rendu
  alourdie ; corriger l'asset une fois est plus propre et testable.
- **Mirror-tile** (empiler crop + miroir vertical) → rejeté : raccord parfait garanti mais
  symétrie mécanique visible sur les cailloux. Le feather-wrap donne un rendu organique.
- **Backdrop statique** (far aérien étiré, plein écran) → rejeté : perd la sensation de
  vitesse d'un endless runner (le sol ne défile plus).

**Impact attendu** : sol de carrière qui défile proprement, sans bande ni bord déchiré.
Reproductible pour les autres biomes : même recette de génération de tuile à appliquer.

---

## 2026-07-06 — Sprint 4 : fix Reviewer 400 « Duplicate function declaration » + garde-fou

**Contexte** : Au lancement du playground, le pipeline démarre (researcher + coder OK)
puis casse au Reviewer avec `google.genai.errors.ClientError: 400 INVALID_ARGUMENT —
Duplicate function declaration found: read_text_file`. Cause racine : le Reviewer avait
`tools=[fs_read, fs_write]`, et **les deux** toolsets déclaraient `read_text_file`
(`fs_read` = read/list, `fs_write` = write + read pour que le Coder relise le manifeste).
Gemini refuse toute requête où deux function declarations partagent un nom. L'erreur ne
tombait qu'au **1er appel LLM du Reviewer** (3e sub-agent du `SequentialAgent`), d'où le
diagnostic trompeur « le pipeline part bien puis casse ».

**Décision** :
1. **Reviewer sur un seul toolset** : nouvelle vue `fs_review` (filtre
   `["read_text_file", "read_file", "list_directory", "write_file"]`) au lieu d'empiler
   `fs_read` + `fs_write`. Un agent = un `McpToolset` → une seule déclaration par nom.
   Les prompts sont inchangés (règle #2 : rien à répercuter dans `AGENT_PROMPTS.md`).
2. **Garde-fou à l'import** : factory `_fs_toolset()` qui enregistre le `tool_filter` de
   chaque vue dans `_TOOLSET_FILTERS`, puis `_assert_unique_tool_names()` exécutée sur
   chaque sub-agent avant `App(...)`. Un chevauchement de filtres sur un même agent lève
   désormais une `ValueError` immédiate et lisible au chargement du module, **avant** tout
   appel réseau — au lieu d'un 400 tardif et opaque.

**Alternative rejetée** :
- **Retirer `read_text_file` de `fs_write`** → rejeté : le Coder en a besoin pour relire
  `docs/ASSET_MANIFEST.md`. Le chevauchement n'est pas le problème ; l'empilement sur un
  même agent l'est.
- **Test pytest seul** (au lieu du garde-fou runtime) → rejeté : ne protège qu'en CI, pas
  le playground local sur la machine WSL. Le garde-fou à l'import échoue vite, sans
  dépendre du lancement des tests. (Un test reste bienvenu plus tard, non exclusif.)
- **Lire le `tool_filter` via un attribut interne d'ADK** → rejeté : pas d'API publique
  stable ; on mémorise le filtre nous-mêmes dans `_TOOLSET_FILTERS`.

**Impact attendu** : pipeline complet researcher → coder → reviewer sans 400 ; toute
future régression de ce type (empilement de toolsets qui se recoupent) échoue au
chargement avec un message explicite plutôt qu'en cours de run.

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

---

## 2026-07-05 — Sprint 4 : agent Reviewer en mode RAPPORT (pas de boucle)

**Contexte** : dernier agent du pipeline (règle capstone : système multi-agent complet
Researcher → Coder → Reviewer). Deux options ouvertes depuis le HANDOFF : (a) **boucle**
de correction (le Reviewer renvoie un `ReviewResult` structuré au Coder via `session.state`,
max 3 itérations) ; (b) **rapport** de validation lisible sans renvoi. Contrainte forte :
deadline serrée (< 1 semaine) + impossibilité de tester sur la machine d'édition + exigence
de démo robuste en playground.

**Décision** : **mode rapport**. Le Reviewer est un 3ᵉ `LlmAgent` (`gemini-2.5-pro`) ajouté
aux `sub_agents` du `SequentialAgent` existant (`researcher → coder → reviewer`) — **aucun
changement d'orchestration**. Il relit `public/level_config.json` sur disque (MCP read),
valide 3 axes (validité schéma/plages, cohérence thématique Clérac, équilibrage badge), et
écrit un rapport Markdown via MCP write dans `docs/reviews/review_<site>.md`. Tools :
`fs_read`, `web_search` (Tavily, fact-check conditionnel d'une espèce douteuse), `fs_write`.
Verdict global `PASS` / `PASS WITH WARNINGS` / `FAIL`.

**Choix confirmé avec l'utilisateur** (AskUserQuestion, Sprint 4) : Reviewer = **Rapport**,
langue **EN**, migration des docs racine vers `docs/`, deadline **serrée**.

**Alternative rejetée — boucle de correction** : plus impressionnante pour le critère
multi-agent (vraie collaboration agent↔agent) mais (a) **plus risquée à démontrer live**,
(b) difficile à borner proprement (gestion des 3 itérations + état partagé), (c) **non
validable** sur la machine d'édition avant la deadline. Documentée comme travail futur
(writeup § Limits & learnings).

**Alternative rejetée — `LoopAgent`** : imposerait de restructurer le `SequentialAgent`
et un contrat de sortie structuré Coder↔Reviewer non testable à temps. Le mode rapport
n'ajoute qu'un `sub_agent`.

**Déviation assumée du spec — nom de fichier** : le spec Sprint 4 demandait
`docs/reviews/review_<timestamp>.md`. Un LLM ne génère pas de timestamp fiable (et
`Date.now()`/horloge indisponibles côté agent). Nom retenu : `review_<site>.md`
(déterministe, lisible, dérivé de `site_name` en minuscules sans accents). Un run écrase
le rapport du site précédent — acceptable ; pour archivage, l'utilisateur renomme.

**Preuve MCP renforcée pour le jury** : un run Reviewer produit `read_text_file`
(config + schéma + manifeste), un `write_file` (rapport), et **optionnellement** un
`tool_use` Tavily quand une espèce est hors liste connue — soit un canal MCP de plus
visible dans la debug view.

**Impact attendu** (à valider sur le PC de test) :
- Run complet `agents-cli playground` : 3 agents visibles, le Reviewer relit le config et
  écrit `docs/reviews/review_clerac.md` avec verdict `PASS`.
- Test ciblé (`tests/manual/run_reviewer.py` + `public/configs/examples/level_config.broken.json`) :
  verdict `FAIL` détectant espèces hors-site (Polar Bear, Bengal Tiger), `spawn_weight` 0,
  `speed_max < speed_start`, seuils badge triviaux/hors-plage, et `missing_assets`.
- `session.state` propage bien Researcher → Coder → Reviewer (`{csr_summary}` consommé par
  le Reviewer) — vérifie que le bug de propagation du Sprint 1 ne réapparaît pas.


---

## 2026-07-06 — Sprint 4 : pivot Tavily → dataset Clérac local (Filesystem MCP)

**Contexte** : la décision Sprint 4 du 5 juil. prévoyait un fact-check Tavily conditionnel
dans le Reviewer pour vérifier une espèce douteuse (« MCP call visible en plus »). En
tentant de brancher `tavily-mcp` côté WSL (VPN Imerys actif en permanence, non
désactivable), le serveur MCP crashe systématiquement au démarrage : les logs ADK
montrent `Failed to create MCP session` en boucle et `ValueError: Tool 'tavily_search'
not found. Available tools: read_file, read_text_file, list_directory` — seul le
Filesystem MCP expose des outils, Tavily n'en fournit aucun. Hypothèse dominante :
inspection TLS d'entreprise du VPN Imerys (self-signed cert observé en curl direct)
qui casse la chaîne de certificats vue par Node. Diagnostic complet dans
`docs/TAVILY_VPN_INCIDENT.md`.

Compte Tavily payant validé (clé OK hors VPN via curl direct), donc l'API elle-même
n'est pas en cause — c'est l'infrastructure réseau côté machine de test qui bloque.

Deuxième constat, indépendant du VPN : les espèces mentionnées jusqu'ici comme
« liste Clérac » (rollier d'Europe, guêpier d'Europe, lézard ocellé) sont en réalité
**méditerranéennes** et n'apparaissent dans aucun document officiel du site Clérac
(avis CNPN Perrin 2022, MRAe Nouvelle-Aquitaine 2022, fiche N2000 FR5400437 Landes
de Montendre). La vraie espèce emblématique de Clérac est la **Fauvette pitchou**
dans les landes à ajoncs. Voir `docs/CLERAC_RESEARCH_REPORT.md`.

**Décision** : le Reviewer n'utilise plus Tavily. Il consomme à la place un dataset
scientifique local `docs/clerac_species_reference.json` (51 espèces validées sur
7 taxons, 12 habitats, 3 espèces incorrectes explicitement signalées avec substitution
recommandée, 3 axes de validation formalisés) lu via **Filesystem MCP** (`fs_read`,
déjà fonctionnel et robuste au VPN). Le dataset est constitué à partir de sources
officielles françaises (CNPN, MRAe, DREAL Nouvelle-Aquitaine, INPN, Imerys corporate,
LPO, Poitou-Charentes Nature) — voir `docs/CLERAC_RESEARCH_REPORT.md` pour la
méthodologie complète.

Le Reviewer garde ses 3 axes et son verdict `PASS` / `PASS WITH WARNINGS` / `FAIL`.
Seul l'Axe 2 (cohérence thématique Clérac) change de source : il lit le JSON au lieu
d'appeler le web. Les tools déclarés dans `app/agent.py` passent de
`[fs_read, web_search, fs_write]` à `[fs_read, fs_write]`. `tavily-mcp` n'est plus
branché au Reviewer (mais reste branché au Researcher pour l'enrichissement biodiversité,
inchangé — le Researcher n'a pas d'impératif de robustesse en démo puisqu'il tourne
avant, et un fallback CSR est déjà en place).

**Alternative rejetée — fix TLS Node (`NODE_EXTRA_CA_CERTS` avec CA Imerys)** :
techniquement propre mais demande d'extraire le CA racine d'entreprise depuis le
Windows certificate store, à refaire sur toute machine de démo. **Rejeté** :
dépendance sur un artefact machine-specific, fragile pour la démo vidéo, et ne
résout pas le problème #2 (espèces incorrectes).

**Alternative rejetée — Brave Search MCP** : drop-in replacement de Tavily, même
domaine externe. **Rejeté** : même risque de blocage VPN Imerys, même fragilité en
démo, et ne résout pas le problème #2.

**Alternative rejetée — Fetch MCP officiel + INPN** : plus pertinent
scientifiquement (source française officielle) mais dépend de la disponibilité
`inpn.mnhn.fr` via VPN et ajoute une couche d'incertitude en démo. **Rejeté** pour
Sprint 4, envisageable comme évolution future post-jury.

**Alternative rejetée — MCP custom autour d'INPN ou GBIF** : discutée mais jugée
disproportionnée pour la deadline (3h de dev estimées) alors que le dataset local
couvre le besoin fonctionnel.

**Alternative rejetée — `NODE_TLS_REJECT_UNAUTHORIZED=0`** : contournement quick &
dirty. **Rejeté** : signal d'alerte sécurité inacceptable dans un writeup ou une
démo jury, et masquerait le problème #2 (espèces incorrectes).

**Impact attendu** :
- Reviewer robuste au VPN Imerys (aucun appel externe, uniquement Filesystem MCP)
- Précision scientifique renforcée : les 3 espèces incorrectes détectées à coup sûr
  (elles sont dans `especes_incorrectes` du JSON avec sévérité `error`), les 51
  espèces validées reconnues par leurs noms français et scientifiques
- Preuve MCP conservée : le Reviewer produit `read_text_file` sur le config,
  le schéma, le manifeste ET le dataset de référence — 4 `tool_use` visibles dans
  la debug view au lieu de 3 précédemment
- Angle writeup renforcé : « nous avons constitué un dataset de référence à partir
  de sources officielles françaises » est plus solide qu'un fact-check Tavily
  ponctuel, et cohérent avec l'exigence de rigueur scientifique sur un sujet
  biodiversité
- HANDOFF § Biodiversité Clérac à mettre à jour (liste actuelle contient les 3
  espèces incorrectes)
- Prompt Reviewer à mettre à jour dans `app/agent.py` et `docs/AGENT_PROMPTS.md`
  (contrat Axe 2 change : lecture du JSON au lieu d'appel web)
- `tavily-mcp` reste branché au **Researcher** (fallback CSR déjà en place si
  le blocage réseau se reproduit là aussi — à valider en playground)

---

## 2026-07-06 — Sprint 4 (démo) : désactivation du web MCP aussi sur le Researcher

**Contexte** : la décision précédente (pivot Tavily → dataset) gardait `tavily-mcp` +
`fetch-mcp` branchés au **Researcher**, en pariant sur un fallback CSR si le VPN bloquait
là aussi. Or le même blocage TLS s'applique au Researcher (il tourne sur la même machine
de test sous VPN Imerys), et un `tool_use` Tavily qui crashe en plein run de démo est un
risque visuel inacceptable devant le jury. On veut un pipeline **entièrement déterministe
et local** pour le tournage.

**Décision** : retirer le web MCP du Researcher pour la démo. `researcher_agent.tools`
passe de `[fs_read, web_search, web_fetch]` à `[fs_read]`. Le Researcher extrait la
biodiversité **du CSR uniquement** (champs `Eco-target` / `Protected area` de la section
SITE), 2 à 6 labels courts, sans invention ni web. Les toolsets `web_search` / `web_fetch`
restent **définis** dans `app/agent.py` (commentés « désactivés démo ») mais branchés sur
aucun agent → ré-enrôlement en une ligne hors VPN. **Supersede** le point « `tavily-mcp`
reste branché au Researcher » de la décision ci-dessus.

**Angle writeup** (validé avec l'utilisateur) : *« we prioritized reliability over web
enrichment during the demo phase due to network constraints »*. Le pipeline devient
100 % filesystem sur les 3 agents — robuste, reproductible, aucune dépendance réseau.

**Conséquence assumée** : biodiversité plus pauvre en run frais (limitée aux espèces/
groupes cités dans le CSR Clérac : oiseaux migrateurs, chauves-souris, oiseaux et insectes
des châtaigneraies). Le `level_config.json` committé (vitrine, 7 espèces validées issues du
dataset) reste la référence de démo pour le jeu ; un run playground CSR-only produira une
liste plus courte — c'est le compromis fiabilité assumé.

**Alternative rejetée — garder Tavily sur le Researcher avec fallback** : le fallback ne
protège pas du bruit visuel (tentative d'appel + erreur loggée) pendant le tournage.
**Rejeté** pour la démo ; réactivable hors VPN.

**Alternative rejetée — faire lire le dataset `clerac_species_reference.json` au Researcher**
(enrichissement local sans web) : donnerait une biodiversité riche ET locale, mais mélange
les rôles (le dataset est l'outil de **validation** du Reviewer, pas une source de génération)
et court-circuite l'intérêt du Reviewer (il validerait des espèces copiées de sa propre
référence). **Rejeté** — on garde la séparation Researcher (extraction CSR) / Reviewer
(validation dataset). Piste possible post-jury si on veut enrichir sans web.

**Impact attendu** (à valider en playground) : run complet sans aucun `tool_use` web ;
Researcher = `read_text_file` (CSR) seul ; `csr_summary.biodiversity_species` = 2-6 labels
issus du CSR ; pipeline reproductible sous VPN.
