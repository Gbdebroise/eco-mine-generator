// =============================================================
//  leaderboard.js — persistance localStorage du classement
//
//  API : add(entry) · getTop(n) · clear() · sanitizePseudo(raw)
//  Stockage : clé "eco_mine_leaderboard_v1", array trié par score desc,
//  tronqué au Top 10. Encapsulé pour faciliter l'éval au Sprint 4.
//
//  Entrée : { pseudo, score, green_points, badge, date_iso }
// =============================================================

const STORAGE_KEY = 'eco_mine_leaderboard_v1';
const MAX_ENTRIES = 10;
const MAX_PSEUDO = 12;

function _store() {
  // localStorage peut être indisponible (mode privé, Node) → dégradation douce.
  try {
    return (typeof localStorage !== 'undefined') ? localStorage : null;
  } catch (e) {
    return null;
  }
}

function _read() {
  const s = _store();
  if (!s) return [];
  try {
    const raw = s.getItem(STORAGE_KEY);
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr : [];
  } catch (e) {
    return [];
  }
}

function _write(arr) {
  const s = _store();
  if (!s) return;
  try {
    s.setItem(STORAGE_KEY, JSON.stringify(arr));
  } catch (e) {
    /* quota / privacy → on ignore silencieusement */
  }
}

/** Nettoie un pseudo : lettres/chiffres/espace/_/- uniquement, 12 car. max. */
export function sanitizePseudo(raw) {
  const s = (raw == null) ? '' : String(raw);
  const cleaned = s.replace(/[^\p{L}\p{N} _-]/gu, '').trim().slice(0, MAX_PSEUDO);
  return cleaned || 'ANON';
}

/** Ajoute une entrée, re-trie par score desc, tronque au Top 10, persiste. Retourne le Top. */
export function add(entry) {
  const e = {
    pseudo: sanitizePseudo(entry && entry.pseudo),
    score: Math.round((entry && entry.score) || 0),
    green_points: Math.round((entry && entry.green_points) || 0),
    badge: !!(entry && entry.badge),
    date_iso: (entry && entry.date_iso) || ''
  };
  const arr = _read();
  arr.push(e);
  arr.sort((a, b) => b.score - a.score);
  const top = arr.slice(0, MAX_ENTRIES);
  _write(top);
  return top;
}

/** Retourne les n meilleures entrées (défaut : Top 10), triées par score desc. */
export function getTop(n) {
  const arr = _read().sort((a, b) => b.score - a.score);
  const count = (typeof n === 'number' && n > 0) ? n : MAX_ENTRIES;
  return arr.slice(0, count);
}

/** Vide le classement. */
export function clear() {
  _write([]);
}
