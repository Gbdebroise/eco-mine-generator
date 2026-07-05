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
