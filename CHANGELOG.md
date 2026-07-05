# Changelog — Eco-Mine Generator / Mission Clérac

Format inspiré de [Keep a Changelog](https://keepachangelog.com/). Dates en ISO.
Le projet se synchronise entre deux machines par `git bundle` (voir `CLAUDE.md`).

---

## [Sprint 4] — 2026-07-05 — Reviewer, démo & writeup Kaggle

Boucler le système multi-agent (Researcher → Coder → **Reviewer**) et livrer le package
jury : writeup, script vidéo, checklist. Le Reviewer valide le config généré — il ne
remplace pas le Coder, il le **contrôle**. Architecture **config-driven** préservée.

> ⚠️ **Non testé sur cette machine** (édition Windows). À valider sur le PC WSL — voir la
> section « Validation » plus bas et `docs/HANDOFF.md`.

### Décisions verrouillées (avec l'utilisateur)
- **Reviewer = mode RAPPORT** (pas de boucle de renvoi au Coder) : plus sûr à démontrer,
  aucun changement d'orchestration. Boucle documentée comme travail futur.
- **Langue jury = EN** (writeup + vidéo).
- **Docs racine migrés vers `docs/`** (anti-drift).
- **Deadline serrée** → chemin le plus robuste privilégié.

### Added
- `app/agent.py` : 3ᵉ agent `reviewer_agent` (`gemini-2.5-pro`, tools `fs_read` +
  `web_search` Tavily + `fs_write`) ajouté aux `sub_agents` du `SequentialAgent`.
- `docs/kaggle_writeup.md` — writeup Kaggle (EN, squelette + intentions ; Results à remplir
  après tests).
- `docs/video_script.md` (4 min, EN, 3 agents + compteur MCP) + `docs/video_checklist.md`.
- `docs/reviews/` (`.gitkeep`) — cible du rapport Reviewer `review_<site>.md`.
- `public/configs/examples/level_config.broken.json` — fixture volontairement cassée
  (espèces hors-site, valeurs hors-plage, `spawn_weight` 0, `speed_max < speed_start`,
  `missing_assets`) pour tester la détection du Reviewer.
- `tests/manual/run_reviewer.py` — runner standalone du Reviewer sur un config donné
  (seed `csr_summary`, swap non destructif de `level_config.json`).

### Changed
- `SequentialAgent` : `sub_agents=[researcher, coder, reviewer]` (ajout, pas de refonte).
- Docs : `AGENT_PROMPTS.md` (section Reviewer + historique), `DECISIONS.md` (ADR-lite
  Reviewer mode rapport), `ARCHITECTURE.md` (3ᵉ agent dans le pipeline),
  `HANDOFF.md`/`CLAUDE.md`/`GEMINI.md` (Sprint 4, pipeline à 3 agents).
- Root `WRITEUP.md` / `VIDEO_SCRIPT.md` → **stubs pointeurs** vers `docs/` (contenu migré
  et actualisé 3-agents ; anciennes versions 2-agents en historique git).

### Not changed (volontairement)
- **Researcher** et **Coder** : prompts, modèles, tools, `output_key` inchangés.
- Structure de state (`{csr_summary}`) — le Reviewer la **consomme**, ne la modifie pas.
- Modèles (`gemini-2.5-flash` / `gemini-2.5-pro`), moteur `game.js`.

### Déviation assumée
- Rapport nommé `review_<site>.md` (pas `review_<timestamp>.md`) : un LLM ne produit pas de
  timestamp fiable. Voir `docs/DECISIONS.md`.

### Validation (à lancer sur le PC de test WSL)
1. **Reviewer sur config cassé** (doit produire un verdict FAIL détectant tous les problèmes) :
   `uv run python tests/manual/run_reviewer.py`
   puis lire `docs/reviews/review_clerac.md`.
2. **Pipeline complet** : `agents-cli playground` → `Generate a game for Clerac` → vérifier
   dans la debug view les 3 agents + le `write_file` du rapport (verdict PASS).
3. **Atteignabilité badge** : rendu manuel (`cd public && python -m http.server 8000`),
   jouer un run et vérifier que le badge Green tombe avec `score ≥ 5000` ET `green ≥ 30`
   (barème : oiseau +15/+1 Green, minerai +10, distance +1/10 px).

---

## [Sprint 3] — 2026-07-05 — Gameplay & Meta

Rendre le jeu défendable devant le jury : mécaniques variées, difficulté progressive,
feedback de fin de partie, badge Imerys Green. Architecture **config-driven** préservée
(les agents remplissent `level_config.json`, `game.js` reste le moteur hand-coded).

> ⚠️ **Non testé sur cette machine** (édition Windows uniquement). À valider sur le PC
> WSL après transfert `git bundle` — voir la section « Validation » plus bas.

### Les 6 changements du sprint

1. **Schéma de config étendu** — `docs/level_config_schema.md` (nouveau contrat) +
   exemple canonique `public/configs/examples/level_config.sprint3.json`. Cinq nouvelles
   sections : `obstacles.dynamite`, `zones.water`, `entities.enemy_trucks`, `difficulty`,
   `thresholds.green_badge`. **Rétro-compatible** : un config Sprint 2 boote à l'identique
   (défauts dans le loader `mergeConfig`).

2. **Dynamite** (`feat(game)`) — obstacle qui explose au contact (particules + camera
   shake ~200 ms), applique `score_malus` + `green_malus`, **ne termine pas la partie**.

3. **Zones d'eau** (`feat(game)`) — bande de terrain (longueur tirée entre
   `min_length_px` et `max_length_px`) qui ralentit le camion (`slowdown_factor`) tant
   qu'il la traverse. Overlay bleu + éclaboussures.

4. **Camions ennemis** (`feat(game)`) — entités mobiles (`speed_px_per_s` propre),
   sprite rouge distinct du joueur, **game over** au contact.

5. **Difficulté progressive** (`feat(game)`) — module unique `public/src/difficulty.js`
   (`getDifficulty(distance, cfg)` → `{ speed, spawnRateMultiplier }`), interpolation
   linéaire `speed_start`→`speed_max` sur `distance_to_max_px`. Le multiplicateur
   s'applique au taux de spawn de **toutes** les entités. Zéro magic number ailleurs.

6. **Couche méta** — `public/src/leaderboard.js` (API `add`/`getTop`/`clear`/
   `sanitizePseudo`, stockage `localStorage` clé `eco_mine_leaderboard_v1`, Top 10 trié
   par score) + pseudo en fin de partie (max 12, sanitize) + **badge Imerys Green**
   (`BadgeScene` de célébration si `score ≥ min_score` ET `green_points ≥
   min_green_points`) + écran `LeaderboardScene` accessible du menu et de la fin.

### Added
- `docs/level_config_schema.md`, `public/configs/examples/level_config.sprint3.json`
- `public/src/difficulty.js`, `public/src/leaderboard.js`
- `game.js` : scènes `BadgeScene`, `GameOverScene`, `LeaderboardScene` ; groupes
  `dynamites` / `enemyTrucks` ; bandes d'eau ; HUD points Green.
- Override d'URL `?config=<chemin>` dans `BootScene` (test d'un config sans agent).
- Placeholders code + entrées manifeste pour `dynamite`, `enemy_truck`, `ui/badge_green.png`.

### Changed
- `public/index.html` : `game.js` chargé en `<script type="module">` (ES modules).
- `game.js` v3 → v4 : rampe de vitesse en dur remplacée par la courbe `difficulty` ;
  `gameOver` inline → scènes dédiées.
- `app/agent.py` : prompt du Coder étendu (5 sections + plages + garde-fou anti-zéro).
- Docs : `AGENT_PROMPTS.md` (Modification 4), `DECISIONS.md` (3 ADR-lite),
  `ASSET_MANIFEST.md` (nouveaux placeholders).

### Not changed (volontairement)
- **Reviewer** : prévu pour le Sprint 4, non touché.
- **Researcher** : inchangé.
- Modèles (`gemini-2.5-flash` / `gemini-2.5-pro`), tools MCP, `output_key`, structure
  `SequentialAgent`.

### Validation (à lancer sur le PC de test WSL)
1. **Rendu manuel** (sans agent) :
   `cd public && python -m http.server 8000` →
   `http://localhost:8000/?config=configs/examples/level_config.sprint3.json`
2. **Pipeline agents** : `agents-cli playground` → run complet → vérifier dans la debug
   view que le Coder écrit les 5 sections dans `public/level_config.json`.
3. **Diff schéma** : comparer le config généré à `docs/level_config_schema.md` (sections
   présentes, valeurs dans les plages, aucun `spawn_weight` à 0).
