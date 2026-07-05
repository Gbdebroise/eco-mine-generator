// =============================================================
//  difficulty.js — courbe de difficulté (module unique et pur)
//
//  Toute la logique de montée en difficulté vit ICI. Le reste du
//  code (game.js) ne contient AUCUN magic number de difficulté :
//  il appelle getDifficulty(distance, cfg) et applique le résultat.
//
//  Contrat : voir docs/level_config_schema.md § 2.4 "difficulty".
//  Pur & sans dépendance → directement testable en Node (Sprint 4).
// =============================================================

export const DEFAULT_DIFFICULTY = {
  curve: 'linear',
  speed_start_px_per_s: 220,
  speed_max_px_per_s: 480,
  distance_to_max_px: 15000,
  spawn_rate_multiplier_at_max: 2.2
};

/**
 * Normalise une section `difficulty` partielle en objet complet.
 * Si `raw` est absent, retombe sur les défauts — et cale
 * `speed_start_px_per_s` sur `fallbackSpeed` (le `scrolling_speed`
 * legacy) pour préserver le feel des configs Sprint 2.
 *
 * @param {object|undefined|null} raw
 * @param {number} [fallbackSpeed]
 * @returns {typeof DEFAULT_DIFFICULTY}
 */
export function normalizeDifficulty(raw, fallbackSpeed) {
  const d = Object.assign({}, DEFAULT_DIFFICULTY, raw || {});
  if ((!raw || raw.speed_start_px_per_s == null) && typeof fallbackSpeed === 'number') {
    d.speed_start_px_per_s = fallbackSpeed;
  }
  return d;
}

/**
 * Interpole vitesse et multiplicateur de spawn selon la distance parcourue.
 *
 * @param {number} distancePx  distance parcourue en pixels (>= 0)
 * @param {object} [difficultyCfg]  section `difficulty` (normalisée de préférence)
 * @returns {{ speed: number, spawnRateMultiplier: number }}
 */
export function getDifficulty(distancePx, difficultyCfg) {
  const d = difficultyCfg || DEFAULT_DIFFICULTY;
  const span = Math.max(1, d.distance_to_max_px);
  let t = Math.max(0, Math.min(1, (distancePx || 0) / span));

  // Courbe. "linear" par défaut ; "ease" = smoothstep (démarrage/fin adoucis).
  if (d.curve === 'ease') t = t * t * (3 - 2 * t);

  const speed = d.speed_start_px_per_s +
    (d.speed_max_px_per_s - d.speed_start_px_per_s) * t;
  const spawnRateMultiplier = 1 + (d.spawn_rate_multiplier_at_max - 1) * t;

  return { speed, spawnRateMultiplier };
}
