# ASSET_MANIFEST — assets réels sur disque

> **Règle CLAUDE.md #1** : le Coder ne doit JAMAIS référencer un asset absent de ce
> manifeste. Toute référence d'asset dans le code ou un prompt doit exister ici ET
> sur le disque (`public/assets/`).
>
> **Provenance** : Kenney *Game Assets All-in-1 3.5.0* (catégorie `2D assets`),
> licence **CC0** (domaine public, réutilisation libre y compris commerciale, sans
> attribution obligatoire). Source hors-repo : `~/Downloads/Kenney Game Assets
> All-in-1 3.5.0/` = bibliothèque de référence pour piocher davantage plus tard.
> Seule une sélection curatée (variantes « Default size », sans retina/vector/
> spritesheets) est versionnée dans `public/assets/` — 1133 fichiers, ~11 MB.

---

## 1. Sprites du cœur (chargés directement par `game.js`)

`game.js` → `OBJECT_ASSETS` attend ces noms **à plat** dans `assets/`. Chaque fichier
est une copie renommée d'un asset Kenney. ⚠️ **À valider visuellement** sur la machine
de test (rendu non vérifiable sur la machine d'édition) — swap trivial si un sprite ne
convient pas, la source est dans la bibliothèque.

| Fichier (`public/assets/`) | Rôle in-game | Source Kenney | À valider |
|---|---|---|---|
| `truck.png` | Camion joueur | Racing Pack → `Cars/car_red_1.png` | ⚠️ voiture rouge vue de dessus (pas un camion minier — placeholder) |
| `ore.png` | Minerai collectible | Physics Assets → `Debris/debrisStone_1.png` | ⚠️ caillou gris |
| `bird.png` | Oiseau (biodiversité / MNHN) | Animal Pack Remastered → `Square/owl.png` | ⚠️ hibou stylisé |
| `blast.png` | Danger « Blasting Zone » | Explosion Pack → `Ground explosion/groundExplosion05.png` | ⚠️ frame unique d'explosion |
| `grove.png` | Bosquet / châtaigneraie | Foliage Pack → `Tilesheet/treeLeaves_default.png` | ⚠️ feuillage d'arbre |
| `spark.png` | Particule / étincelle | Explosion Pack → `Particles/burst.png` | ⚠️ éclat |

## 2. Fonds de biome (`<biome>_far.png` / `<biome>_near.png`)

`game.js` charge un décor optionnel par biome ; en son absence il dessine un
placeholder (404 console = normal).

| Biome | `_far` | `_near` | État |
|---|---|---|---|
| `clay_quarry` | ✅ `clay_quarry_far.png` | ✅ `clay_quarry_near.png` | **Pré-existant** (généré, hors Kenney) |
| `granite_underground` | ❌ | ❌ | Placeholder dessiné (à produire) |
| `wetland` | ❌ | ❌ | Placeholder dessiné (voir dossier `wetland/`) |
| `diatomite` | ❌ | ❌ | Placeholder dessiné (à produire) |

## 3. Bibliothèque curatée par usage (`public/assets/<dossier>/`)

Sélection versionnée, disponible pour Sprint 3+ (obstacles, collectibles, décors).
Tous CC0.

| Dossier | Nb | Usage prévu | Source Kenney |
|---|---|---|---|
| `vehicles/` | 50 | Camion joueur + camions adverses (couleurs multiples) | Racing Pack → Cars |
| `vehicles/objects/` | 39 | Cônes, tonneaux, obstacles de piste | Racing Pack → Objects |
| `animals/` | 30 | Sauvetages bio : `owl`, `duck`, `parrot`, `frog`, `rabbit`… | Animal Pack Remastered → Square |
| `foliage/` | 62 | Arbres, buissons, plantes (décor biodiversité) | Foliage Pack → Default size |
| `obstacles/` | 67 | Rochers (`debrisStone_*`) + éléments explosifs (dynamite) | Physics Assets → Debris + Explosive elements |
| `collectibles/` | 163 | Sacs, caisses, objets miniers (sacs/big bags kaolin) | Generic Items → Colored |
| `fx/ground_explosion/` | 9 | Séquence explosion au sol (dynamite) | Explosion Pack |
| `fx/regular_explosion/` | 9 | Séquence explosion aérienne | Explosion Pack |
| `fx/particles/` | 17 | Débris/étincelles d'explosion | Explosion Pack → Particles |
| `particles/` | 80 | Poussière (`dirt_*`), fumée derrière le camion (Sprint 3) | Particle Pack → Transparent |
| `particles/smoke/` | 25 | Fumée noire (séquence) | Smoke Particles → Black smoke |
| `particles/gas/` | 9 | Gaz/vapeur | Smoke Particles → Gas |
| `ground/` | 96 | Textures de sol défilant (piste carrière) | Road Textures → Default |
| `ground/classic/` | 80 | Variantes de sol (style classique) | Road Textures (Classic) |
| `background/` | 8 | Fonds parallax (forêt, prairie, désert…) | Background Elements Remastered |
| `industrial/` | 112 | Décor de carrière/mine (machines, tapis) | Platformer Pack Industrial → Default size |
| `industrial/pixel/` | 116 | Décor industriel style pixel | Pixel Platformer Industrial Expansion |
| `ui/medals/` | 27 | Badges scoring (base pour le badge Imerys Green) | Medals |
| `wetland/` | 126 | Décor zone humide (biome `wetland`) : algues, rochers, poissons | Fish Pack → Default |

**Total versionné** : 1133 fichiers, ~11 MB.

## 4. Non retenu (dans la bibliothèque `~/Downloads`, pas dans le repo)

Disponible pour piocher plus tard sans re-télécharger : **Ranks Pack** (642 assets de
rangs), et pour chaque pack ci-dessus les variantes **Retina / Vector / Spritesheet**
non copiées. Ajouter au repo seulement si un usage précis se présente, puis
**documenter ici avant de référencer dans le code**.

---

## Historique

| Date | Action |
|------|--------|
| 5 juil. 2026 | Création. Import curaté Kenney All-in-1 3.5.0 (16 packs, sélection Default-size) + mapping des 6 sprites cœur. |
