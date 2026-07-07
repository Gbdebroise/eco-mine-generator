# Reviewer report — Beauvoir
**Verdict: FAIL**

## Axis 1 — Config validity
- **JSON Structure**: PASS. The file is valid JSON and respects the overall schema structure. All required sections from the Sprint 3 schema are present.
- **Value Ranges**: PASS. All numeric values for `obstacles.dynamite`, `zones.water`, `entities.enemy_trucks`, `difficulty`, and `thresholds.green_badge` are within their recommended ranges as per `docs/level_config_schema.md`.
- **Empty/Zeroed Sections**: PASS. No mechanics-related sections are empty and no `spawn_weight` values are set to zero.
- **Asset Check**: FAIL. The configuration file explicitly declares missing assets: `assets/granite_underground_far.png` and `assets/granite_underground_near.png`. The absence of biome background textures is a blocking issue.

## Axis 2 — Clerac thematic coherence
This validation was performed by comparing the `level_config.json` against the reference dataset `docs/clerac_species_reference.json`.

- **`site_name`**: WARNING. The config is for "Beauvoir", but the reference dataset is for "Clerac". This is a thematic mismatch.
- **`mineral_name`**: FAIL. The config specifies `"Lithium Ore"`. The reference dataset's `site_context.minerai_principal` is `"kaolin"`. This is a critical thematic error.
- **`biodiversity_species`**: FAIL. The config lists `["Biodiversity Plots (ONF/CEN)", "Sioule River"]`. This field is meant for 4-8 real species names (e.g., "Fauvette pitchou"), not thematic concepts. Neither of these entries are found in the `especes_validees` of the reference dataset.
- **`biome`**: WARNING. The biome `"granite_underground"` is not listed in the `habitats_valides` of the reference dataset.
- **`protected_area`**: WARNING. The protected area "Sioule River" is not found in the `habitats_valides` of the reference dataset.

## Axis 3 — Gameplay balance
- **Difficulty Curve**: PASS. The difficulty progression is well-defined and calibrated. `speed_start_px_per_s` (220) is less than `speed_max_px_per_s` (480), `distance_to_max_px` (15000) is reasonable, and `spawn_rate_multiplier_at_max` (2.2) provides a ramp-up in intensity.
- **Badge Attainability**: PASS. The thresholds (`min_score`: 5000, `min_green_points`: 30) are challenging but appear reachable for an average player. Achieving the green points target and surviving long enough to accrue the necessary distance score (approx. 41,000 pixels) is not trivial and should take around two minutes, which is acceptable.

## Issues
- **[FAIL] Axis 1 (Config validity)**: The `missing_assets` field explicitly lists `["assets/granite_underground_far.png", "assets/granite_underground_near.png"]`. The game cannot run without its background assets.
- **[FAIL] Axis 2 (Thematic coherence)**: The `mineral_name` is `"Lithium Ore"`, which directly contradicts the reference dataset's required mineral, `"kaolin"`.
- **[FAIL] Axis 2 (Thematic coherence)**: The `biodiversity_species` field is used incorrectly, containing concepts instead of the required biological species from the reference dataset.
- **[WARNING] Axis 2 (Thematic coherence)**: The `site_name`, `biome`, and `protected_area` do not align with the provided `clerac_species_reference.json` dataset.
