# Reviewer report — Clerac
**Verdict: PASS**

## Axis 1 — Config validity
The provided `level_config.json` is valid and well-formed. All required keys are present, and their values fall within the recommended ranges specified in `docs/level_config_schema.md`.

- **`obstacles.dynamite`**: All parameters (`spawn_weight`, `explosion_radius_px`, `green_malus`, `score_malus`) are within their recommended ranges.
- **`zones.water`**: All parameters (`spawn_weight`, `min_length_px`, `max_length_px`, `slowdown_factor`) are within their recommended ranges.
- **`entities.enemy_trucks`**: All parameters (`spawn_weight`, `speed_px_per_s`) are within their recommended ranges.
- **`difficulty`**: The difficulty curve is well-defined with all parameters (`speed_start_px_per_s`, `speed_max_px_per_s`, `distance_to_max_px`, `spawn_rate_multiplier_at_max`) within their recommended ranges.
- **`thresholds.green_badge`**: The badge thresholds (`min_score`, `min_green_points`) are within their recommended ranges.
- **Asset Check**: No direct asset paths are referenced in the config, which complies with the project's asset handling strategy (relying on code-drawn placeholders).

No sections are empty, and no `spawn_weight` values are set to zero, ensuring all game mechanics are active.

## Axis 2 — Clerac thematic coherence
The configuration is thematically consistent with the ground-truth data provided in `docs/clerac_species_reference.json`.

- **`site_name`**: "Clerac" correctly matches the reference data.
- **`mineral_name`**: "Chamotte Clay" is a correct representation of the final product derived from the "kaolin" extracted at the site.
- **`protected_area`**: The concept of protected Chestnut Groves (`taillis_chataignier`) is correctly implemented as a game mechanic and is validated by the reference data, which highlights its importance for bats (`chiropteres`).
- **`biodiversity_species`**: The species listed ("Migratory Birds", "Woodland Bats", "Grove Birds", "Grove Insects") are high-level categories that are well-supported by the specific, validated species and habitats listed in the reference JSON (e.g., numerous migratory bird species, multiple bat species, birds associated with groves). No incorrect or out-of-place species (like the Mediterranean examples in `especes_incorrectes`) were used.

## Axis 3 — Gameplay balance
The game settings appear to be well-balanced.

- **Difficulty Curve**: The difficulty scales progressively, with both speed and spawn rates increasing over a reasonable distance (`15000px`). The starting speed (220px/s) and max speed (480px/s) provide a clear sense of acceleration.
- **Badge Attainability**: The Imerys Green badge is deemed achievable but not trivial. The thresholds (`min_score: 5000`, `min_green_points: 30`) require the player to perform consistently well, collecting a significant number of both minerals and eco-bonuses while avoiding obstacles. The balance of spawn rates appears sufficient to allow a skilled player to meet both conditions during a run.

## Issues
None.
