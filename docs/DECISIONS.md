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
