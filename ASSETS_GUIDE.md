# Assets — guide complet

Tous les assets vont dans `public/assets/`. Le moteur charge chaque fichier
par cle ; si le fichier est absent, il dessine le placeholder procedural.
Vous pouvez livrer les assets un par un, dans n'importe quel ordre.

---

## 1. Fonds de decor — generer avec Imagen

```bash
pip install google-genai pillow
python generate_assets.py                        # tous les biomes + ecrans-titre
python generate_assets.py --biome clay_quarry    # un seul biome
python generate_assets.py --site Beauvoir        # un seul ecran-titre
```

| Fichier                        | Taille   | Role                        |
|-------------------------------|----------|------------------------------|
| clay_quarry_far.png            | 480x256  | Fond lent (Clerac)           |
| clay_quarry_near.png           | 480x384  | 1er plan transparent         |
| granite_underground_far.png    | 480x256  | Fond (Beauvoir EMILI)        |
| granite_underground_near.png   | 480x384  | 1er plan transparent         |
| wetland_far.png                | 480x256  | Fond (Provins)               |
| wetland_near.png               | 480x384  | 1er plan transparent         |
| diatomite_far.png              | 480x256  | Fond (Foufouilloux)          |
| diatomite_near.png             | 480x384  | 1er plan transparent         |

Regle _near.png : fond transparent PNG RGBA avec elements epars.
Si le fond blanc Imagen reste visible, ouvrez dans GIMP et effacez
avec la baguette magique (seuil 30).

---

## 2. Sprites — Kenney.nl (CC0, aucun credit requis)

truck.png — 44x68 px
  Pack : https://kenney.nl/assets/top-down-vehicles
  Fichier : PNG/vehicle_truck.png — rogner, redimensionner a 44x68

ore.png — 34x34 px
  Pack : https://kenney.nl/assets/topdown-shooter
  Fichier : PNG/crate_wood.png

bird.png — 34x28 px
  Pack : https://kenney.nl/assets/animal-pack-redux
  Fichier : PNG/duck.png ou PNG/parrot.png

blast.png — 46x46 px
  Pack : https://kenney.nl/assets/particle-pack
  Fichier : PNG/explosionGreen2.png

grove.png — 46x46 px
  Pack : https://kenney.nl/assets/topdown-shooter
  Fichier : PNG/tree_large.png

spark.png — 12x12 px
  Pack : https://kenney.nl/assets/particle-pack
  Fichier : PNG/star_06.png

---

## 3. Ecrans-titre — un par site

Generes par le script en <site>_start_screen.png (480x640).
Pour activer sur le site courant :
  copy public\assets\clerac_start_screen.png public\assets\start_screen.png

---

## 4. Audio (optionnel)

Pack : https://kenney.nl/assets/interface-sounds (CC0)
  Audio/click_002.ogg -> renommer sfx_collect.mp3
  Audio/error_006.ogg -> renommer sfx_crash.mp3

---

## 5. Structure finale public/assets/

clay_quarry_far.png           <- Imagen
clay_quarry_near.png          <- Imagen
granite_underground_far.png   <- Imagen
granite_underground_near.png  <- Imagen
wetland_far.png               <- Imagen
wetland_near.png              <- Imagen
diatomite_far.png             <- Imagen
diatomite_near.png            <- Imagen
start_screen.png              <- Imagen (site courant)
truck.png                     <- Kenney
ore.png                       <- Kenney
bird.png                      <- Kenney
blast.png                     <- Kenney
grove.png                     <- Kenney
spark.png                     <- Kenney
sfx_collect.mp3               <- Kenney
sfx_crash.mp3                 <- Kenney

Ordre de priorite pour la demo :
1. clay_quarry_far + granite_underground_far  (difference de biome visible)
2. truck.png  (vrai dumper)
3. start_screen.png  (impact visuel immediat)
4. sfx_collect + sfx_crash  (sensation de jeu x2)
5. Reste des sprites et 1ers plans
