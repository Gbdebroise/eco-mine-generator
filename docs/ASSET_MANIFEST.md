# ASSET_MANIFEST — sources d'assets autorisées

## Règle absolue

Le Coder ne doit JAMAIS référencer un chemin d'asset qui n'est pas listé dans
ce document. Toute référence à un asset absent de ce manifeste sera considérée
comme une hallucination et le `level_config.json` généré sera rejeté par le Reviewer.

> **Provenance & vérification** : tous les assets Kenney proviennent du bundle
> *Game Assets All-in-1 3.5.0* (catégorie `2D assets`). La provenance faisant foi
> est le fichier `License.txt` **livré dans chaque pack source** (`~/Downloads/Kenney
> Game Assets All-in-1 3.5.0/2D assets/<Pack>/License.txt`). Les URLs ci-dessous
> suivent la convention de slug Kenney (`kenney.nl/assets/<slug>`) ; confirmer le slug
> exact sur kenney.nl en cas de doute. Licence uniforme : **CC0** (domaine public,
> usage personnel/éducatif/commercial libre, crédit non obligatoire).
>
> **Sélection** : seule une sélection curatée (variantes « Default size », sans
> retina/vector/spritesheets) est versionnée — **1133 fichiers, ~11 MB**. Les 16 packs
> complets restent hors-repo dans `~/Downloads/…` comme bibliothèque de référence.

---

## Sprites du cœur (chargés directement par `game.js`)

`game.js` → `OBJECT_ASSETS` attend ces noms **à la racine** `assets/`. Chaque fichier
est une copie renommée d'un asset Kenney. ⚠️ **À valider visuellement** sur la machine
de test (rendu non vérifiable sur la machine d'édition).

| Chemin (relatif `public/`) | Rôle | Source Kenney | À valider |
|---|---|---|---|
| `assets/truck.png` | Camion joueur | racing-pack → `PNG/Cars/car_red_1.png` | ⚠️ voiture rouge top-down (placeholder) |
| `assets/ore.png` | Minerai collectible | physics-assets → `PNG/Debris/debrisStone_1.png` | ⚠️ caillou gris |
| `assets/bird.png` | Oiseau (biodiversité) | animal-pack-remastered → `PNG/Square/owl.png` | ⚠️ hibou stylisé |
| `assets/blast.png` | Danger « Blasting Zone » | explosion-pack → `PNG/Ground explosion/groundExplosion05.png` | ⚠️ frame unique |
| `assets/grove.png` | Bosquet / châtaigneraie | foliage-pack → `Tilesheet/treeLeaves_default.png` | ⚠️ feuillage |
| `assets/spark.png` | Particule / étincelle | explosion-pack → `PNG/Particles/burst.png` | ⚠️ éclat |
| `assets/dynamite.png` | Dynamite (obstacle malus, Sprint 3) | physics-assets → `PNG/Explosive elements/elementExplosive*.png` | ⚠️ **placeholder code** (fichier non copié) |
| `assets/enemy_truck.png` | Camion adverse (game over, Sprint 3) | racing-pack → `PNG/Cars/car_red_1.png` | ⚠️ **placeholder code** (fichier non copié) |

> **Sprint 3** : `dynamite`, `enemy_truck` (et le badge, plus bas) suivent le pattern
> établi de `game.js` : le sprite est chargé s'il existe à la racine `assets/`, sinon
> `game.js` **dessine un placeholder par code** (404 console = normal). Les sources
> Kenney ci-dessus sont dans la bibliothèque `public/assets/kenney/` mais **pas encore
> copiées/renommées** à la racine — à faire sur la machine de test pour un rendu final.

---

## Assets Kenney (locaux)

Chemin racine : `public/assets/kenney/`

### Pack : Racing Pack (1.0)
- **URL source** : https://kenney.nl/assets/racing-pack
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/racing-pack/PNG/Cars/` — 50 voitures (`car_red_1.png`, `car_blue_1.png`… 5 couleurs × variantes) → camion joueur + camions adverses colorés
  - `assets/kenney/racing-pack/PNG/Objects/` — 39 objets de piste (cônes, tonneaux, barrières) → obstacles
- **Contenu NON utilisé** : `PNG/Characters`, `PNG/Motorcycles`, `PNG/Tiles`, `Spritesheets/`, `Vector/`

### Pack : Animal Pack Remastered
- **URL source** : https://kenney.nl/assets/animal-pack-redux
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/animal-pack-remastered/PNG/Square/` — 30 animaux (`owl.png`, `duck.png`, `parrot.png`, `penguin.png`, `frog.png`, `rabbit.png`…) → sauvetages biodiversité + transformation Green
- **Contenu NON utilisé** : styles `Round`, `Round (outline)`, `Round without details`, `Square (outline)`, `Spritesheet/`, `Vector/`

### Pack : Foliage Pack (1.0)
- **URL source** : https://kenney.nl/assets/foliage-pack
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/foliage-pack/PNG/Default size/` — 62 éléments végétaux (`foliagePack_001.png`…) → arbres, buissons, plantes (décor biodiversité)
  - *(note : `grove.png` racine vient de `Tilesheet/treeLeaves_default.png`, non re-copié ici — dispo dans le pack source)*
- **Contenu NON utilisé** : `PNG/Retina`, `Spritesheet/`, `Tilesheet/`, `Vector/`

### Pack : Explosion Pack (1.0)
- **URL source** : https://kenney.nl/assets/explosion-pack
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/explosion-pack/PNG/Ground explosion/` — 9 frames (`groundExplosion00-08.png`) → explosion dynamite au sol
  - `assets/kenney/explosion-pack/PNG/Regular explosion/` — 9 frames → explosion aérienne
  - `assets/kenney/explosion-pack/PNG/Particles/` — 17 particules (`burst.png`, `greyCloud1.png`…) → étincelles / poussière
- **Contenu NON utilisé** : `PNG/Pixel explosion`, `PNG/Simple explosion`, `PNG/Sonic explosion`

### Pack : Generic Items
- **URL source** : https://kenney.nl/assets/generic-items
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/generic-items/PNG/Colored/` — 163 objets (`genericItem_color_001.png`…) → sacs, caisses, big bags de kaolin (collectibles miniers)
- **Contenu NON utilisé** : `PNG/White`, `Spritesheet/`, `Vector/`

### Pack : Physics Assets (1.0)
- **URL source** : https://kenney.nl/assets/physics-assets
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/physics-assets/PNG/Debris/` — 9 débris de pierre (`debrisStone_1-3.png`…) → rochers / minerai
  - `assets/kenney/physics-assets/PNG/Explosive elements/` — 58 éléments (`elementExplosive000.png`…) → dynamite / obstacles explosifs
- **Contenu NON utilisé** : `PNG/Aliens`, `PNG/Backgrounds`, `PNG/Glass elements`, `PNG/Metal elements`, et autres matériaux

### Pack : Particle Pack (1.1)
- **URL source** : https://kenney.nl/assets/particle-pack
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/particle-pack/PNG (Transparent)/` — 80 particules (`dirt_01.png`, `smoke_01.png`, `circle_01.png`…) → nuages de poussière derrière le camion (Sprint 3)
- **Contenu NON utilisé** : `PNG (Black background)`, `.../Rotated`, `Unity samples/`

### Pack : Smoke Particles (1.0)
- **URL source** : https://kenney.nl/assets/smoke-particles
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/smoke-particles/PNG/Black smoke/` — 25 frames (`blackSmoke00.png`…) → fumée / poussière
  - `assets/kenney/smoke-particles/PNG/Gas/` — 9 frames → gaz / vapeur
- **Contenu NON utilisé** : `PNG/Explosion`, `PNG/Flash`, `PNG/White smoke`, `Spritesheets/`

### Pack : Platformer Pack Industrial (1.0)
- **URL source** : https://kenney.nl/assets/platformer-pack-industrial
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/platformer-pack-industrial/PNG/Default size/` — 112 tuiles (`platformIndustrial_001.png`…) → décor de carrière / mine (machines, tapis)
- **Contenu NON utilisé** : `PNG/Retina`, `Spritesheet/`, `Tilesheet/`

### Pack : Pixel Platformer: Industrial Expansion (1.0)
- **URL source** : https://kenney.nl/assets/pixel-platformer-industrial-expansion
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/pixel-platformer-industrial-expansion/PNG/` — 116 tuiles pixel → décor industriel style pixel
- **Contenu NON utilisé** : variantes retina / spritesheet

### Pack : Road Textures
- **URL source** : https://kenney.nl/assets/road-textures
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/road-textures/PNG/Default/` — 96 textures (`roadTexture_01.png`…) → sol défilant de la piste (carrière)
- **Contenu NON utilisé** : `PNG/Retina`, `Tilesheet/`, `Vector/`

### Pack : Road Textures Classic (1.0)
- **URL source** : https://kenney.nl/assets/road-textures
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/road-textures-classic/PNG/` — 80 textures de sol (style classique)
- **Contenu NON utilisé** : variantes retina / tilesheet / vector

### Pack : Medals (1.1)
- **URL source** : https://kenney.nl/assets/medals
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/medals/PNG/` — 27 médailles (`flatshadow_medal1.png`…) → base pour le badge Imerys Green / UI scoring
- **Contenu NON utilisé** : `Spritesheet/`, `Vector/`

### Pack : Background Elements Remastered (1.0)
- **URL source** : https://kenney.nl/assets/background-elements-redux
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/background-elements-remastered/Backgrounds/` — 8 fonds (`backgroundColorForest.png`, `backgroundColorGrass.png`, `backgroundDesert.png`…) → fonds parallax par biome
- **Contenu NON utilisé** : `PNG/Default` (Elements), `PNG/Retina`, `Spritesheet/`

### Pack : Fish Pack
- **URL source** : https://kenney.nl/assets/fish-pack
- **Licence** : CC0
- **Contenu utilisable** :
  - `assets/kenney/fish-pack/PNG/Default/` — 126 éléments (`background_seaweed_a.png`, `background_rock_a.png`, poissons…) → décor du biome `wetland`
- **Contenu NON utilisé** : `PNG/Double`, `Spritesheet/`, `Vector/`

---

## Assets générés (Imagen 3)

> ⚠️ **Déviation assumée du template** : ces fonds sont à la **racine** `public/assets/`
> (et non `public/assets/generated/`) car `game.js` les charge à `assets/<biome>_far.png`
> / `assets/<biome>_near.png`. Ne pas déplacer sans modifier `game.js`.

- `assets/clay_quarry_far.png` — fond lointain carrière de kaolin Clérac (généré)
- `assets/clay_quarry_near.png` — fond proche carrière de kaolin Clérac (généré)

---

## Assets à générer plus tard (placeholder)

Planifiés, non encore produits (`game.js` dessine un placeholder en leur absence — 404
console = normal) :

- `assets/granite_underground_far.png` / `_near.png` — biome mine souterraine (Beauvoir)
- `assets/wetland_far.png` / `_near.png` — biome zone humide (Provins) — piocher dans `kenney/fish-pack/`
- `assets/diatomite_far.png` / `_near.png` — biome diatomite (Foufouilloux)
- `assets/ui/badge_green.png` — badge arbre doré (Sprint 3 ; chargé par `BadgeScene`, placeholder code si absent). Base : `kenney/medals/PNG/`. Fournir l'asset final ici.
- `assets/dynamite.png` — dynamite Sprint 3 (placeholder code en attendant la copie depuis `kenney/physics-assets/`)
- `assets/enemy_truck.png` — camion adverse Sprint 3 (placeholder code en attendant la copie depuis `kenney/racing-pack/`)
- `assets/generated/background_clerac_tile.png` — tuile de fond à découper via Pillow (Sprint 3)

---

## Convention de nommage

Tous les chemins référencés dans `level_config.json` doivent être **RELATIFS depuis la
racine `public/`** :
- Sprites cœur : `assets/truck.png`, `assets/ore.png`, `assets/bird.png`, `assets/blast.png`, `assets/grove.png`, `assets/spark.png`
- Fonds de biome : `assets/<biome>_far.png`, `assets/<biome>_near.png`
- Bibliothèque Kenney : `assets/kenney/<slug>/PNG/<sous-dossier>/<fichier>.png`
  (ex. `assets/kenney/racing-pack/PNG/Cars/car_blue_1.png`)

**Ne jamais compléter un fichier « manquant » par intuition.** Avant de référencer un
asset, vérifier qu'il existe sur le disque ET qu'il est listé ci-dessus. Pour ajouter un
asset de la bibliothèque source, le copier d'abord dans `public/assets/kenney/<slug>/`
puis l'inscrire dans ce manifeste.

---

## Historique

| Date | Action |
|------|--------|
| 5 juil. 2026 | Création. Import curaté Kenney All-in-1 3.5.0 (16 packs, sélection Default-size, 1133 fichiers). Layout par pack `kenney/<slug>/`. Mapping des 6 sprites cœur. |
