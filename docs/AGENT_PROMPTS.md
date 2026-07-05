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

---

## Historique des versions

| Date | Agent | Changement |
|------|-------|-----------|
| 3 juil. 2026 | — | Prompts initiaux (chemin nu → hallucinations) |
| 4 juil. 2026 | researcher | Chemin `app/…`, lecture obligatoire, anti-hallucination |
| 4 juil. 2026 | coder | Recopie verbatim, anti-généralisation, schéma aligné game.js |
| 5 juil. 2026 | researcher | Rôle EXTRACTEUR (anti-refus), labels courts (anti-verbosité), format sans fences |
| 5 juil. 2026 | coder | Tolérance aux fences en entrée, non-ré-expansion des labels |
