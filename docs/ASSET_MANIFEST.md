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

## Sprites du cœur — rendus par CODE dans `game.js`

> **Décision 2026-07-06 (sprites)** : les sprites d'objets sont désormais **dessinés par
> `game.js`** (`drawObjectPlaceholder`), pas chargés depuis des fichiers. L'import Kenney
> `25ee8e7` avait posé des PNG génériques et surdimensionnés (voiture orange sur le camion
> jaune, hibou 128px sur l'oiseau, tilesheet 1024px de feuilles sur l'arbre…) qui
> **écrasaient** les sprites vectoriels calibrés d'origine et n'étaient pas redimensionnés
> (`group.create` = taille native → « blocs trop gros »). Les 6 PNG parasites ont été
> supprimés → `game.js` retombe sur ses placeholders code (fallback lignes 234-236). Voir
> `docs/DECISIONS.md § 2026-07-06 (sprites)`.

`game.js` → `OBJECT_ASSETS` déclare ces clés. Chaque sprite est **dessiné par code** tant
qu'aucun fichier de même nom n'existe à la racine `assets/` (le fallback recharge un PNG
s'il réapparaît — pattern conservé pour un futur set IA).

| Clé | Rôle | Rendu actuel (code, calibré) |
|---|---|---|
| `truck` | Camion joueur | camion-benne **jaune** 44×68 |
| `enemy_truck` | Camion adverse (game over) | camion **rouge** 44×68, cabine inversée |
| `mineral` | Minerai collectible | gemme gris clair 34×34 |
| `bird` | Oiseau (biodiversité) | petit oiseau bleu 34×28 (bat des ailes) |
| `blast` | Danger « Blasting Zone » (fatal) | panneau danger triangulaire jaune/noir + picto explosion 46×46 |
| `dynamite` | Dynamite (obstacle malus) | fagot de bâtons rouges + mèche + étincelle 44×40 |
| `grove` | Bosquet / châtaigneraie | petit arbre (tronc + feuillage) 46×46 |
| `spark` | Particule / étincelle | point blanc 12×12 (scalé par le système de particules) |

> **Set IA futur (optionnel)** : pour un rendu au niveau des fonds Imagen 3, générer un set
> cohérent (camion-benne jaune, oiseau migrateur, châtaignier, big-bag de kaolin, dynamite)
> en PNG transparents ~96px et les déposer à la racine `assets/<clé>.png` : le fallback les
> chargera automatiquement à la place du code. Aucune modif de `game.js` nécessaire.

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

- `assets/clay_quarry_far.png` — fond lointain carrière de kaolin Clérac (généré). Vue
  aérienne encadrée : actuellement **masquée** derrière `_near` (opaque), conservée pour
  usage futur. NE PAS tiler telle quelle (bordures → coutures).
- `assets/clay_quarry_near.png` — **tuile de sol raccordable verticalement** (480×322,
  opaque, seamless) dérivée de la photo générée d'origine par crop intérieur + raccord
  par fondu (feather-wrap, System.Drawing). C'est la couche VISIBLE qui défile dans
  `game.js` (`tileSprite`). L'original encadré (bords déchirés) reste dans l'historique
  git. Voir `docs/DECISIONS.md § 2026-07-06 (background)`.

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
