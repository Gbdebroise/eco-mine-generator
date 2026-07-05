# level_config.json — Schéma (contrat Coder ↔ game.js)

> **Source de vérité du format.** Le Coder (`app/agent.py`) écrit un `public/level_config.json`
> qui DOIT respecter ce schéma. Le moteur `public/game.js` (hand-coded, stable) le lit et
> fusionne chaque champ absent avec un défaut interne (`DEFAULT_CONFIG`). Un config Sprint 2
> qui ne contient AUCUNE des sections Sprint 3 ci-dessous doit encore **booter à l'identique** —
> la rétro-compatibilité est garantie par les défauts du loader.
>
> Exemple canonique complet : [`configs/examples/level_config.sprint3.json`](../public/configs/examples/level_config.sprint3.json).
> Pour tester ce fichier dans le jeu sans lancer d'agent :
> `http://localhost:8000/?config=configs/examples/level_config.sprint3.json`
> (le paramètre `?config=` est optionnel ; sans lui le jeu charge `level_config.json`).

---

## 1. Champs Sprint 1–2 (inchangés)

| Clé | Type | Rôle |
|---|---|---|
| `site_name` | string | Nom du site (ex. `"Clerac"`). |
| `mineral_name` | string | Label court du minerai (ex. `"Chamotte Clay"`). |
| `eco_target` | string | Label court de la cible biodiversité (ex. `"Migratory Birds (MNHN)"`). |
| `danger_obstacle` | string | Label court du danger fatal (ex. `"Blasting Zone"`). |
| `biome` | enum | `"clay_quarry"` \| `"granite_underground"` \| `"wetland"` \| `"diatomite"`. |
| `scrolling_speed` | number | **Legacy.** Vitesse de défilement de base (px/s). Sert de *fallback* pour `difficulty.speed_start_px_per_s` quand la section `difficulty` est absente. |
| `spawn_rates` | object | `{ mineral, eco_bonus, obstacle }` — probabilités par vague de spawn (0–1). |
| `biodiversity_species` | string[] | 4–8 labels courts d'espèces réelles. |
| `ui_strings` | object | `title`, `instructions`, `intro_story`, `eco_facts[]`, `end_recap`. |

---

## 2. Sections Sprint 3 (nouvelles, toutes optionnelles)

Chaque section a un défaut interne dans `game.js`. Le Coder **doit** les remplir avec des
valeurs dans les plages recommandées — **ne jamais mettre un `spawn_weight` à 0 ni vider une
section** (sinon le jeu perd la mécanique correspondante).

### 2.1 `obstacles.dynamite` — obstacle à malus (NON fatal)

```json
"obstacles": {
  "dynamite": {
    "spawn_weight": 0.15,
    "explosion_radius_px": 80,
    "green_malus": 10,
    "score_malus": 200
  }
}
```

| Clé | Type | Plage recommandée | Effet |
|---|---|---|---|
| `spawn_weight` | number | `0.08`–`0.20` | Probabilité de spawn par vague. |
| `explosion_radius_px` | number | `60`–`120` | Rayon visuel de l'explosion (particules + camera shake ~200 ms). |
| `green_malus` | number | `5`–`15` | Points Green retirés au contact. |
| `score_malus` | number | `100`–`300` | Points de score retirés au contact. |

> La dynamite explose au contact et **continue la partie** (contrairement à `danger_obstacle`
> / `blast` qui est un game over immédiat).

### 2.2 `zones.water` — bande de ralentissement

```json
"zones": {
  "water": {
    "spawn_weight": 0.10,
    "min_length_px": 120,
    "max_length_px": 300,
    "effect": "slowdown",
    "slowdown_factor": 0.4
  }
}
```

| Clé | Type | Plage recommandée | Effet |
|---|---|---|---|
| `spawn_weight` | number | `0.06`–`0.15` | Probabilité de spawn d'une bande par vague. |
| `min_length_px` / `max_length_px` | number | `100`–`350` | Longueur (hauteur) de la bande, tirée aléatoirement entre les deux. |
| `effect` | enum | `"slowdown"` | Seul effet supporté à ce jour. |
| `slowdown_factor` | number | `0.3`–`0.6` | Multiplicateur de vitesse tant que le camion est dans la bande. |

### 2.3 `entities.enemy_trucks` — entité mobile fatale

```json
"entities": {
  "enemy_trucks": {
    "spawn_weight": 0.08,
    "speed_px_per_s": 180,
    "behavior": "straight_line",
    "collision_effect": "game_over"
  }
}
```

| Clé | Type | Plage recommandée | Effet |
|---|---|---|---|
| `spawn_weight` | number | `0.05`–`0.12` | Probabilité de spawn par vague. |
| `speed_px_per_s` | number | `120`–`240` | Vitesse **propre** ajoutée à la vitesse de défilement. |
| `behavior` | enum | `"straight_line"` | Seul comportement supporté à ce jour. |
| `collision_effect` | enum | `"game_over"` | Seul effet supporté à ce jour. |

### 2.4 `difficulty` — courbe de difficulté

```json
"difficulty": {
  "curve": "linear",
  "speed_start_px_per_s": 220,
  "speed_max_px_per_s": 480,
  "distance_to_max_px": 15000,
  "spawn_rate_multiplier_at_max": 2.2
}
```

| Clé | Type | Plage recommandée | Effet |
|---|---|---|---|
| `curve` | enum | `"linear"` (ou `"ease"`) | Interpolation utilisée par `getDifficulty`. |
| `speed_start_px_per_s` | number | `180`–`260` | Vitesse au départ (distance = 0). |
| `speed_max_px_per_s` | number | `400`–`560` | Vitesse à `distance_to_max_px`. |
| `distance_to_max_px` | number | `10000`–`20000` | Distance à laquelle la vitesse/spawn atteint le max. |
| `spawn_rate_multiplier_at_max` | number | `1.8`–`2.6` | Multiplicateur appliqué à **tous** les taux de spawn au max. |

> Implémentation unique dans [`public/src/difficulty.js`](../public/src/difficulty.js) :
> `getDifficulty(distancePx, difficultyCfg)` → `{ speed, spawnRateMultiplier }`.
> Interpolation linéaire entre `speed_start` et `speed_max` sur `distance_to_max_px`.
> Le multiplicateur de spawn va de `1` (départ) à `spawn_rate_multiplier_at_max`.
> **Aucun magic number de difficulté ne doit vivre ailleurs que dans cette section.**

### 2.5 `thresholds.green_badge` — seuils du badge Imerys Green

```json
"thresholds": {
  "green_badge": {
    "min_score": 5000,
    "min_green_points": 30
  }
}
```

| Clé | Type | Plage recommandée | Effet |
|---|---|---|---|
| `min_score` | number | `3000`–`8000` | Score total minimum (production + éco + bonus distance). |
| `min_green_points` | number | `20`–`40` | Points Green minimum. |

> Score total = `prodScore + ecoScore + floor(distance_px / 10)`.
> Points Green = `+1` par collecte éco, `−3` par bosquet protégé heurté, `−green_malus` par dynamite.
> Badge obtenu si `score_total ≥ min_score` **ET** `green_points ≥ min_green_points`.

---

## 3. Rétro-compatibilité (défauts du loader)

`game.js` fusionne chaque section manquante avec ces défauts. Un config Sprint 2 boote donc
sans modification :

- `difficulty` absent → synthétisé, `speed_start_px_per_s = scrolling_speed`.
- `obstacles` / `zones` / `entities` / `thresholds` absents → valeurs par défaut ci-dessus.
- Toute sous-clé manquante d'une section présente → complétée par le défaut.

---

## 4. Assets référencés

Le schéma **n'exige aucun chemin d'asset**. Les sprites des nouvelles mécaniques
(`dynamite`, `enemy_truck`, badge) sont chargés en option par `game.js` depuis la racine
`assets/` et **dessinés par code si absents** (404 console = normal). Voir
[`ASSET_MANIFEST.md`](ASSET_MANIFEST.md). Ne jamais inventer un chemin d'asset.
