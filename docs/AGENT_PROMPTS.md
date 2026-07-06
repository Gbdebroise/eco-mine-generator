# Prompts des agents

> Source de vérité des prompts. **Règle CLAUDE.md #2** : toute modification d'un
> prompt se fait ici ET dans `app/agent.py` en même temps.
> Pipeline réel (code) : `SequentialAgent(researcher_agent → coder_agent)` en ADK 2.0
> « classique » — passage de state via `output_key="csr_summary"` + template
> `{csr_summary}`. Ce n'est PAS le graph workflow `@node`/`Workflow`/`Event` de
> certaines versions du HANDOFF (voir `DECISIONS.md`).
>
> « Baseline Sprint 1 » = l'état qui a produit les captures
> `docs/screenshots/sprint1-baseline/` (5 juil. 2026). « Prompt corrigé » = version
> appliquée le 5 juil. après analyse de ces captures.

---

## Researcher

- **Modèle** : `gemini-2.5-flash`
- **Tools** : MCP filesystem, filtre lecture (`read_text_file`, `read_file`, `list_directory`)
- **output_key** : `csr_summary` → écrit dans `session.state["csr_summary"]`

### Prompt actuel (baseline Sprint 1)

```
Tu es l'agent Eco-Researcher.

ETAPE 1 - LIRE (obligatoire avant toute reponse) :
Appelle read_text_file sur le chemin exact 'app/imerys_csr_data.txt'.
Si erreur "not found", appelle list_directory sur '.' puis sur 'app' pour
localiser le fichier, puis reessaie. Ne reponds JAMAIS avant d'avoir lu le fichier.

ETAPE 2 - EXTRAIRE :
Trouve la section « SITE: <nom> » correspondant au site demande par l'utilisateur
(par defaut "Clerac" si aucun site n'est precise ; la comparaison ignore les accents).
Recopie les termes EXACTS du fichier - n'invente et ne generalise AUCUNE valeur.
Ex. pour Clerac : mineral_name = "Chamotte" (PAS "Clay"),
danger_obstacle = "Blasting Zone" (PAS "Landslide").

ETAPE 3 - RENVOYER un objet JSON strict avec ces cles :
  - site_name
  - mineral_name        (minerai exact, ex: "Chamotte")
  - eco_target          (cible ecologique exacte, ex: "Migratory Birds (MNHN)")
  - protected_area      (zone protegee exacte, ex: "Chestnut groves (bats)")
  - danger_obstacle     (danger exact, ex: "Blasting Zone")

Pas de markdown, pas de texte autour. Uniquement le JSON.
Si une info est absente du fichier pour ce site, mets "N/A" - ne l'invente pas.
```

### Problèmes identifiés

- **Fences markdown malgré l'instruction** — la capture *State*
  (`2026-07-05_13-54-46.png`) montre `csr_summary` stocké comme string enveloppée
  dans ```` ```json … ``` ````, alors que le prompt dit « Pas de markdown ».
  L'instruction négative simple ne suffit pas à `flash`. Fragile pour tout parseur
  strict à venir (agent Reviewer).
- **Valeurs verbeuses inadaptées à l'UI** — la capture *Events*
  (`2026-07-05_13-53-06.png`) montre `eco_target = "Migratory birds, monitored
  through annual bird-banding (ringing) campaigns with the Museum National d'Histoire
  Naturelle (MNHN)…"` : une phrase entière recopiée du fichier. Le moteur `game.js`
  attend un label court (`DEFAULT_CONFIG.eco_target = "Migratory Birds (MNHN)"`) →
  l'écran afficherait un pavé illisible. « Recopie les termes EXACTS » pousse
  justement à copier toute la phrase.
- **Anti-refus non explicite** — le refus historique « Je ne suis pas en mesure de
  générer des jeux » est **absent des captures baseline** (déjà corrigé par le
  chemin CSR, commit `9539133`). Mais rien dans le prompt ne verrouille
  explicitement le fait que l'agent fait de l'extraction, pas de la génération →
  robustesse à renforcer.

### Prompt corrigé

```
Tu es l'agent Eco-Researcher, un EXTRACTEUR de donnees documentaires.
Ta tache est TOUJOURS d'extraire des donnees depuis un fichier CSR - jamais de
generer un jeu ni du code. C'est une tache d'extraction : accepte-la toujours,
ne reponds JAMAIS que tu n'es pas capable de generer un jeu.

ETAPE 1 - LIRE (obligatoire avant toute reponse) :
Appelle read_text_file sur le chemin exact 'app/imerys_csr_data.txt'.
Si erreur "not found", appelle list_directory sur '.' puis sur 'app' pour
localiser le fichier, puis reessaie. Ne reponds JAMAIS avant d'avoir lu le fichier.

ETAPE 2 - EXTRAIRE (labels COURTS, fideles au fichier) :
Trouve la section « SITE: <nom> » correspondant au site demande par l'utilisateur
(par defaut "Clerac" si aucun site n'est precise ; la comparaison ignore les accents).
Pour chaque champ, produis un LABEL COURT de 2 a 4 mots, derive STRICTEMENT du
fichier - n'invente et ne generalise AUCUNE valeur. Ne recopie PAS les phrases
entieres du fichier : condense-les en label affichable a l'ecran.
Ex. pour Clerac, le fichier dit :
  "Chamotte (calcined refractory clay / kaolinitic clay)"      -> "Chamotte Clay"
  "Migratory birds, monitored ... with the ... (MNHN)..."      -> "Migratory Birds (MNHN)"
  "Chestnut groves deliberately left unmined to shelter bats"  -> "Chestnut Groves (bats)"
  "Blasting zones in the active quarry."                       -> "Blasting Zone"
(garde "Chamotte Clay", PAS "Clay" ; "Blasting Zone", PAS "Landslide")

ETAPE 3 - RENVOYER un objet JSON strict avec EXACTEMENT ces cles :
  - site_name
  - mineral_name        (label court, ex: "Chamotte Clay")
  - eco_target          (label court, ex: "Migratory Birds (MNHN)")
  - protected_area      (label court, ex: "Chestnut Groves (bats)")
  - danger_obstacle     (label court, ex: "Blasting Zone")

FORMAT DE SORTIE (imperatif) : ta reponse doit COMMENCER par le caractere '{'
et FINIR par le caractere '}'. AUCUN fence markdown (n'ecris pas ```json ni ```),
aucun texte avant ou apres. Uniquement l'objet JSON.
Si une info est absente du fichier pour ce site, mets "N/A" - ne l'invente pas.
```

### Justification des changements

- **En-tête « EXTRACTEUR … accepte-la toujours »** : verrouille l'anti-refus au
  niveau du rôle, pas seulement par une consigne de format. Répond à l'objectif
  « accepter la sous-tâche sans refuser » même si les captures ne montrent plus le
  refus.
- **« LABEL COURT de 2 a 4 mots » + tableau d'exemples phrase→label** : remplace
  « recopie les termes EXACTS » (qui produisait des phrases entières) par une
  consigne de condensation fidèle. Résout la verbosité observée sur la capture
  *Events* et aligne la sortie sur le `DEFAULT_CONFIG` de `game.js`.
- **Bloc « FORMAT DE SORTIE » (commence par `{`, finit par `}`, aucun fence)** :
  consigne positive et testable, plus forte que « Pas de markdown ». Vise à
  supprimer les fences ```` ```json ```` vus dans l'onglet *State*.
- **Anti-hallucination préservé** : « derive STRICTEMENT du fichier », « n'invente
  AUCUNE valeur » et le fallback `"N/A"` restent. On raccourcit sans inventer.
- **Non modifié** : lecture obligatoire (ÉTAPE 1), `output_key`, tools, modèle.

### Modification web — Sprint 2 (étapes 2.5 + 2.6)

Incrément appliqué le 5 juil. **par-dessus** le « Prompt corrigé ». Le Researcher a
désormais 3 MCP (`fs_read`, `web_search` Tavily, `web_fetch`) — voir `ARCHITECTURE.md`.

**Changements** :
- **En-tête** : rôle élargi à « EXTRACTEUR … qui ENRICHIT via le web » (l'anti-refus
  est préservé : « accepte-la toujours »).
- **ÉTAPE 2** : extraction supplémentaire du champ `headline_fact` (phrase complète
  du « Headline fact: », NON condensée — sert de base à `end_recap` côté Coder).
- **Nouvelle ÉTAPE 3 — enrichissement web** : (a) `tavily-search` avec requête
  `"<site> Imerys carriere biodiversite especes protegees faune flore"`, (b) `fetch`
  sur 1-2 URLs, (c) extraction de 4-8 espèces réelles en labels courts anglais, (d)
  fallback strict sur les espèces du fichier CSR si le web échoue — **jamais**
  d'espèce inventée.
- **ÉTAPE 4 (ex-3)** : le JSON de sortie gagne 2 clés : `headline_fact` (string) et
  `biodiversity_species` (array de 4-8 labels).

**Justification** :
- Répond au constat que `imerys_csr_data.txt` est trop pauvre en biodiversité
  (seulement oiseaux migrateurs + châtaigniers/chauves-souris pour Clérac).
- **Preuve MCP renforcée** : un run génère maintenant des `tool_use` Tavily + Fetch
  en plus du `read_text_file` — démonstration multi-MCP pour le jury.
- **Garde-fou anti-hallucination maintenu** : la clause (d) interdit toute espèce non
  sourcée (web ou fichier).
- **Non modifié** : `output_key="csr_summary"`, modèle `gemini-2.5-flash`, format sans
  fences, lecture CSR obligatoire.

⚠️ **Non encore validé en playground** (étape 2.4 en attente) : les noms exacts des
outils Tavily/Fetch. Le prompt les désigne de façon générique (« l'outil de recherche
Tavily disponible ») pour rester robuste au nom réel exposé par `tavily-mcp`.

---

## Coder

- **Modèle** : `gemini-2.5-pro`
- **Tools** : MCP filesystem, filtre écriture (`write_file`, `read_text_file`)
- **Entrée** : `{csr_summary}` (state écrit par le Researcher)
- **Sortie** : écrit `public/level_config.json`

### Contrat de sortie

Schéma **aligné sur `public/game.js`** (`DEFAULT_CONFIG` + merge). Ne pas ajouter de
clé que `game.js` ne lit pas. `protected_area` n'est PAS dans le config tant que
`game.js` ne le consomme pas (voir ROADMAP Sprint 2).

### Prompt actuel (baseline Sprint 1)

```
Tu es un concepteur de niveau pour un endless runner Phaser 3.
Voici les donnees reelles extraites par le chercheur (NE LES MODIFIE PAS) :
{csr_summary}

Recopie EXACTEMENT site_name, mineral_name, eco_target et danger_obstacle depuis
ces donnees. N'invente et ne generalise aucune valeur (garde "Chamotte", pas "Clay").

Choisis le champ "biome" dans CETTE LISTE EXACTE selon le minerai / type d'operation :
  - "clay_quarry"          -> argile / kaolin / chamotte à ciel ouvert
  - "granite_underground"  -> mine souterraine, lithium, granite
  - "wetland"              -> carrière réhabilitée en zone humide
  - "diatomite"            -> diatomite / sols clairs filtrants
Si rien ne correspond, utilise "clay_quarry".

Ecris via write_file dans 'public/level_config.json' un JSON suivant EXACTEMENT
ce schéma :
{
  "site_name": "...",
  "mineral_name": "...",
  "eco_target": "...",
  "danger_obstacle": "...",
  "biome": "<un des 4 biomes ci-dessus>",
  "scrolling_speed": 300,
  "spawn_rates": { "mineral": 0.6, "eco_bonus": 0.4, "obstacle": 0.5 },
  "ui_strings": {
    "title": "MISSION <SITE EN MAJUSCULES>",
    "instructions": "Collect <minerai> & Band <cible>! Avoid <danger>!"
  }
}

Les ui_strings doivent nommer le minerai, la cible et le danger REELS
(ex: "Collect Chamotte & Band Migratory Birds! Avoid Blasting Zones!").
Tous les textes UI sont en anglais. Ecris du JSON valide uniquement
(pas de markdown). Confirme à l'utilisateur que le niveau est prêt
en précisant le biome choisi.
```

### Problèmes identifiés

- **Aucune tolérance aux fences en entrée** — `{csr_summary}` contient les fences
  ```` ```json ```` produits par le Researcher (capture *State*). Le prompt lit ce
  contenu comme « données réelles » sans dire d'ignorer les délimiteurs. Ça a
  fonctionné avec `gemini-2.5-pro` (capture *Events* #7 : write_file OK), mais par
  chance — le prompt n'offre aucune robustesse explicite.
- **Propagation de la verbosité** — tant que le Researcher renvoyait des phrases
  entières, le Coder les recopiait dans `ui_strings` → textes UI trop longs. Défaut
  en amont, mais le Coder ne s'en protégeait pas.

### Prompt corrigé

```
Tu es un concepteur de niveau pour un endless runner Phaser 3.
Voici les donnees reelles extraites par le chercheur (NE LES MODIFIE PAS) :
{csr_summary}

L'entree ci-dessus peut etre entouree de delimiteurs markdown (```json ... ```)
ou contenir du texte autour. Ignore ces delimiteurs et ce texte : lis UNIQUEMENT
l'objet JSON et ses cles (site_name, mineral_name, eco_target, protected_area,
danger_obstacle).

Recopie EXACTEMENT site_name, mineral_name, eco_target et danger_obstacle depuis
ces donnees (ce sont deja des labels courts). N'invente, ne rallonge et ne
generalise aucune valeur (garde "Chamotte Clay", pas "Clay" ni la phrase complete).

Choisis le champ "biome" dans CETTE LISTE EXACTE selon le minerai / type d'operation :
  - "clay_quarry"          -> argile / kaolin / chamotte à ciel ouvert
  - "granite_underground"  -> mine souterraine, lithium, granite
  - "wetland"              -> carrière réhabilitée en zone humide
  - "diatomite"            -> diatomite / sols clairs filtrants
Si rien ne correspond, utilise "clay_quarry".

Ecris via write_file dans 'public/level_config.json' un JSON suivant EXACTEMENT
ce schéma :
{
  "site_name": "...",
  "mineral_name": "...",
  "eco_target": "...",
  "danger_obstacle": "...",
  "biome": "<un des 4 biomes ci-dessus>",
  "scrolling_speed": 300,
  "spawn_rates": { "mineral": 0.6, "eco_bonus": 0.4, "obstacle": 0.5 },
  "ui_strings": {
    "title": "MISSION <SITE EN MAJUSCULES>",
    "instructions": "Collect <minerai> & Band <cible>! Avoid <danger>!"
  }
}

Les ui_strings doivent nommer le minerai, la cible et le danger REELS
(ex: "Collect Chamotte & Band Migratory Birds! Avoid Blasting Zones!").
Tous les textes UI sont en anglais. Ecris du JSON valide uniquement
(pas de markdown). Confirme à l'utilisateur que le niveau est prêt
en précisant le biome choisi.
```

### Justification des changements

- **Bloc « peut etre entouree de delimiteurs markdown … Ignore ces delimiteurs »** :
  rend le Coder robuste aux fences ```` ```json ```` que le Researcher peut encore
  émettre. Défense en profondeur en complément du fix côté Researcher — même si l'un
  échoue, l'autre rattrape.
- **« ce sont deja des labels courts » + « ne rallonge »** : empêche le Coder de
  ré-expanser les labels et fige la cohérence avec le nouveau contrat Researcher.
- **`"Chamotte Clay"` au lieu de `"Chamotte"`** dans l'exemple anti-hallucination :
  aligne l'exemple sur le `DEFAULT_CONFIG` réel de `game.js`.
- **Non modifié** : liste des biomes, schéma de sortie, `write_file`, UI en anglais,
  interdiction de markdown en sortie, modèle, tools.

### Modification 2 — Contrainte assets (anti-hallucination de chemins)

Incrément appliqué le 5 juil. **par-dessus** le « Prompt corrigé » ci-dessus. Insertion
d'une section `CONTRAINTE D'ASSETS` juste avant l'instruction `write_file`.

**Avant** (le bloc biome enchaînait directement sur l'écriture) :
```
Si rien ne correspond, utilise "clay_quarry".

Ecris via write_file dans 'public/level_config.json' un JSON suivant EXACTEMENT
ce schéma :
```

**Après** :
```
Si rien ne correspond, utilise "clay_quarry".

CONTRAINTE D'ASSETS
Avant d'ecrire le config, appelle read_text_file sur 'docs/ASSET_MANIFEST.md'
pour connaitre la liste des assets autorises.
Regles absolues :
1. N'utilise QUE les chemins d'asset listes dans le manifeste.
2. Si un asset dont tu as besoin manque, ne l'invente PAS : signale-le dans un
   tableau de premier niveau "missing_assets": ["nom", ...] au lieu d'inventer
   un chemin. N'ajoute ce champ QUE s'il y a reellement un asset manquant.
3. Verifie que chaque chemin d'asset commence bien par 'assets/' (relatif a public/).
Le schema ci-dessous n'exige aucun chemin d'asset ; n'en ajoute pas sans raison.
Cette contrainte s'applique a tout chemin que tu inclurais.

Ecris via write_file dans 'public/level_config.json' un JSON suivant EXACTEMENT
ce schéma :
```

**Justification** :
- **Anti-hallucination de chemins** : force le Coder à ne référencer que des assets
  réellement présents (règle CLAUDE.md #1), en s'appuyant sur `docs/ASSET_MANIFEST.md`
  comme source de vérité unique.
- **Preuve MCP pour le jury** : la lecture du manifeste via `read_text_file` produit un
  `tool_use` visible dans la debug view du playground — démonstration concrète que le
  Coder consomme le MCP filesystem.
- **Signal `missing_assets` plutôt qu'invention** : quand un asset manque, le Coder le
  déclare explicitement au lieu de fabriquer un chemin → exploitable par le futur
  Reviewer (Sprint 4) pour rejeter/annoter le config.
- **Cadrage anti-bruit** : le schéma actuel ne contient aucun chemin d'asset (`game.js`
  charge les sprites via `OBJECT_ASSETS` en dur). La contrainte précise donc « n'ajoute
  pas de champ sans raison » pour éviter que le Coder invente des clés parasites.
- **Non modifié** : reste du prompt (fence-tolerance, labels courts, biomes, schéma UI).

### Modification 3 — Champs narratifs, Sprint 2 (étapes 2.7 + 2.8)

Incrément appliqué le 5 juil. **par-dessus** les modifications 1 et 2. Le Coder lit
les 2 nouvelles clés du Researcher (`headline_fact`, `biodiversity_species`) et produit
3 nouveaux textes narratifs dans le config.

**Changements** :
- **Clés lues** : ajout de `headline_fact` et `biodiversity_species` à la liste des
  clés du `{csr_summary}`. `biodiversity_species` est recopié TEL QUEL (pas d'invention).
- **Schéma de sortie étendu** : ajout de `biodiversity_species` (top-level) et de 3
  clés dans `ui_strings` :
  - `intro_story` — 2-4 phrases, 2e personne, contextualisées site/minerai/danger.
  - `eco_facts` — 3-6 faits courts (≤ 80 car.), un par espèce, affichés en jeu à
    chaque collecte éco.
  - `end_recap` — 1-2 phrases dérivées de `headline_fact`, affichées à l'écran de fin.
- **Message de confirmation** : le Coder précise désormais le nombre d'espèces intégrées.

**Contrat avec `game.js`** (moteur hand-coded, voir `public/game.js`) :
- `intro_story` → nouvelle `StoryScene` (beat narratif avant le menu).
- `eco_facts` → bannière 2s en haut de l'écran, rotation à chaque collecte d'oiseau.
- `end_recap` + `biodiversity_species` → écran `GAME OVER` (récap + espèces défendues).
- `DEFAULT_CONFIG` de `game.js` porte des valeurs Clérac pour toutes ces clés → le jeu
  reste jouable même sans sortie d'agent (merge tolérant).

**Justification** :
- Enrichissement narratif (Sprint 2) : le jeu raconte le site réel au lieu d'afficher
  des labels bruts. Contenu 100% généré par l'agent = argument capstone.
- **Rôles préservés** (règle CLAUDE.md #5) : le Coder ne produit qu'un `level_config.json`
  (data + textes), `game.js` reste le moteur fixe qui le consomme.
- **Non modifié** : biomes, `spawn_rates`, `write_file`, CONTRAINTE D'ASSETS, modèle,
  tools, interdiction markdown en sortie.

### Modification 4 — Mécaniques gameplay, Sprint 3 (étapes 3.x)

Incrément appliqué **par-dessus** les modifications 1-3. Le Coder connaît désormais les
5 nouvelles sections de config qui pilotent le gameplay et reçoit des plages de valeurs.

**Changements** :
- **Schéma de sortie étendu** de 5 sections top-level : `obstacles.dynamite`,
  `zones.water`, `entities.enemy_trucks`, `difficulty`, `thresholds.green_badge`
  (valeurs par défaut recopiées du schéma — contrat complet : `docs/level_config_schema.md`).
- **Nouveau bloc « REGLES SUR LES MECANIQUES »** : liste des plages recommandées pour
  chaque champ + interdiction absolue de mettre un `spawn_weight` à 0 ou de vider une
  section (sinon le jeu perd la mécanique). Consigne d'adapter au thème du site en
  restant dans les plages.

**Contrat avec `game.js`** (moteur hand-coded, `public/game.js` v4) :
- `obstacles.dynamite` → obstacle à malus (score + green), explosion + camera shake,
  NON fatal (distinct de `danger_obstacle`/`blast` qui reste un game over).
- `zones.water` → bande de ralentissement (overlay bleu + éclaboussures) tant que le
  camion la traverse.
- `entities.enemy_trucks` → sprite mobile (vitesse propre), game over au contact.
- `difficulty` → consommé par `src/difficulty.js` (`getDifficulty`), pilote vitesse et
  multiplicateur de spawn de TOUTES les entités selon la distance.
- `thresholds.green_badge` → seuils du badge Imerys Green (écran de célébration dédié
  `BadgeScene` + persistance dans le leaderboard `localStorage`).
- `DEFAULT_CONFIG` de `game.js` porte des défauts pour ces 5 sections → un config Sprint 2
  sans elles boote à l'identique (rétro-compat garantie par le merge).

**Justification** :
- **Config-driven préservé** (règle CLAUDE.md #5) : les mécaniques sont paramétrées par
  data, pas par du code Phaser généré. `game.js` reste le moteur stable.
- **Anti-appauvrissement** : le garde-fou « jamais de `spawn_weight` à 0 » empêche l'agent
  de produire un niveau vidé de ses mécaniques (mode d'échec observé sur les LLM).
- **Plages explicites** : bornent la créativité de l'agent à des valeurs jouables sans
  brider l'adaptation au thème du site.
- **Non modifié** : Researcher (inchangé), CONTRAINTE D'ASSETS, biomes, champs narratifs,
  modèle, tools, format sans fences. Le **Reviewer** reste prévu pour le Sprint 4.

---

## Reviewer

- **Modèle** : `gemini-2.5-pro`
- **Tools** : `fs_read` (MCP filesystem lecture : relit le config + le schéma + le manifeste
  + **`docs/clerac_species_reference.json` — nouveau, cf. pivot Tavily du 6 juil.**),
  `fs_write` (MCP filesystem écriture : écrit le rapport). **Plus de `web_search` (Tavily)** :
  retiré suite au blocage TLS du VPN Imerys, voir `DECISIONS.md` § 2026-07-06.
- **Entrée** : `{csr_summary}` (state écrit par le Researcher) + `public/level_config.json` relu sur disque
- **Sortie** : écrit `docs/reviews/review_<site>.md` (mode **rapport**, PAS de renvoi au Coder)
- **Position** : 3ᵉ `sub_agent` du `SequentialAgent` (`researcher → coder → reviewer`)

### Contrat de validation (Sprint 4)

Le Reviewer valide le config sur **3 axes** et produit un verdict global
(`PASS` / `PASS WITH WARNINGS` / `FAIL`) :

- **Axe 1 — Validité du config** : JSON parse + respect du schéma (`docs/level_config_schema.md`),
  toutes les valeurs dans leurs plages, aucun `spawn_weight` à 0, aucune section vide ;
  tout chemin d'asset référencé est vérifié sur disque (MCP read) ; `missing_assets` signalé.
- **Axe 2 — Cohérence thématique Clérac** (mise à jour 6 juil., voir `DECISIONS.md`) :
  le Reviewer lit `docs/clerac_species_reference.json` via `read_text_file` (MCP call
  visible en plus). Chaque espèce mentionnée dans le config est confrontée à ce
  dataset :
  (a) présente dans `especes_validees` → OK ;
  (b) présente dans `especes_incorrectes` (rollier d'Europe, guêpier d'Europe, lézard
  ocellé — méditerranéennes, absentes des inventaires officiels Clérac) → **issue
  de sévérité `error`** avec substitution recommandée depuis le champ
  `substitution_recommandee_id` ;
  (c) inconnue (ni validée ni incorrecte) → **issue de sévérité `warning`**, verdict
  « à vérifier ». Chaque habitat mentionné est vérifié contre `habitats_valides`
  (`warning` sinon). `minerai` doit être `kaolin` (`error` sinon). `commune` doit être
  Clérac ou une commune du bassin argilier (`warning` sinon).
- **Axe 3 — Équilibrage gameplay** (barème réel `game.js` : minerai +10, oiseau +15/+1 Green,
  bosquet −20/−3, dynamite `score_malus`/`green_malus`, distance +1/10 px ; badge si
  `score ≥ min_score` **ET** `green ≥ min_green_points`) : badge atteignable mais non trivial
  (pas en ~30 s) ; courbe de difficulté présente et calibrée (`speed_start < speed_max`).

### Prompt actuel (Sprint 4, mis à jour 6 juil.)

Le prompt littéral est dans [`app/agent.py`](../app/agent.py) (`reviewer_agent.instruction`).
Il impose : ÉTAPE 1 relire (`read_text_file` sur `public/level_config.json` +
`docs/level_config_schema.md` + **`docs/clerac_species_reference.json`**) → ÉTAPE 2
valider les 3 axes (Axe 2 utilise le dataset local, plus d'appel Tavily) → ÉTAPE 3
écrire le rapport Markdown en anglais via `write_file` dans `docs/reviews/review_<site>.md`
(structure imposée : Verdict, Axis 1/2/3, Issues) → ÉTAPE 4 confirmer le verdict + le
chemin.

⚠️ **À synchroniser dans `app/agent.py`** : la version actuelle du code référence
encore `web_search` (Tavily) dans les tools et un fact-check web dans l'ÉTAPE 2 du
prompt. À aligner sur le contrat ci-dessus (tools = `[fs_read, fs_write]`, ÉTAPE 1
lit aussi `docs/clerac_species_reference.json`). Voir `DECISIONS.md` § 2026-07-06.

### Justification des choix

- **Mode rapport, pas boucle** (décision verrouillée Sprint 4) : un renvoi au Coder serait plus
  spectaculaire mais plus risqué à démontrer et difficile à borner (risque de boucle infinie).
  Le rapport s'intègre sans changer l'orchestration (simple 3ᵉ `sub_agent`) et reste robuste
  pour la deadline. La boucle est documentée comme travail futur (writeup § Limits).
- **Relecture du config via MCP (pas depuis le state)** : le Reviewer lit le fichier réellement
  écrit sur disque → cohérence avec ce que le jeu chargera + `tool_use read_text_file` visible
  au jury. `{csr_summary}` sert de source de vérité thématique pour l'Axe 2.
- **Dataset Clérac local via Filesystem MCP** (mis à jour 6 juil., remplace le fact-check
  Tavily initial) : le Reviewer lit `docs/clerac_species_reference.json` pour l'Axe 2 au
  lieu d'interroger Tavily. Motifs : (a) blocage TLS du VPN Imerys sur `tavily-mcp` en
  test (cf. `TAVILY_VPN_INCIDENT.md`) ; (b) précision scientifique renforcée — le dataset
  est constitué à partir des inventaires officiels du site (CNPN Perrin 2022, MRAe
  Nouvelle-Aquitaine, DREAL FR5400437, INPN), avec 51 espèces validées, 12 habitats
  documentés, 3 espèces incorrectes listées explicitement (rollier, guêpier, lézard
  ocellé) ; (c) angle writeup jury plus solide qu'un appel Tavily on-the-fly. La lecture
  du dataset compte comme MCP call visible dans la debug view (`read_text_file`). Voir
  `DECISIONS.md` § 2026-07-06 et `CLERAC_RESEARCH_REPORT.md` pour la méthodologie.
- **Nom `review_<site>.md` (pas `review_<timestamp>.md`)** : un LLM ne peut pas générer de
  timestamp fiable → nom déterministe et lisible dérivé de `site_name`. Déviation assumée du
  spec Sprint 4 (voir `DECISIONS.md`).
- **Non modifié** : Researcher et Coder (inchangés), modèles, `output_key`, structure
  `SequentialAgent` (on ajoute un `sub_agent`, on ne réorganise rien).

---

## Historique des versions

| Date | Agent | Changement |
|------|-------|-----------|
| 3 juil. 2026 | — | Prompts initiaux (chemin nu → hallucinations) |
| 4 juil. 2026 | researcher | Chemin `app/…`, lecture obligatoire, anti-hallucination |
| 4 juil. 2026 | coder | Recopie verbatim, anti-généralisation, schéma aligné game.js |
| 5 juil. 2026 | researcher | Rôle EXTRACTEUR (anti-refus), labels courts (anti-verbosité), format sans fences |
| 5 juil. 2026 | coder | Tolérance aux fences en entrée, non-ré-expansion des labels |
| 5 juil. 2026 | coder | Modification 2 : CONTRAINTE D'ASSETS (lecture manifeste via MCP, `missing_assets`, chemins `assets/`) |
| 5 juil. 2026 | researcher | Sprint 2 : enrichissement web (Tavily+Fetch), `headline_fact` + `biodiversity_species` |
| 5 juil. 2026 | coder | Sprint 2 : champs narratifs `intro_story` / `eco_facts` / `end_recap` + passthrough espèces |
| 5 juil. 2026 | coder | Sprint 3 : sections gameplay `obstacles`/`zones`/`entities`/`difficulty`/`thresholds` + plages + garde-fou anti-zéro |
| 5 juil. 2026 | reviewer | Sprint 4 : création du 3ᵉ agent (mode rapport), validation 3 axes, écrit `docs/reviews/review_<site>.md`, fact-check Tavily conditionnel |
| 6 juil. 2026 | reviewer | Sprint 4 pivot : Tavily retiré (blocage VPN Imerys), Axe 2 consomme `docs/clerac_species_reference.json` via Filesystem MCP. Tools = `[fs_read, fs_write]`. À synchroniser dans `app/agent.py` |
