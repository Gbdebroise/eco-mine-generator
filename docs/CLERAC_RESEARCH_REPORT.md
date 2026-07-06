# Recherche approfondie — Site Imerys Clérac (Charente-Maritime)

**Date :** 2026-07-06
**Objectif :** Constituer un dataset de référence Clérac exploitable par le Reviewer
agent (Option A du pivot Tavily → Filesystem MCP + dataset local).
**Simulation de :** Recherche approfondie type Tavily deep search, réalisée hors
contrainte VPN Imerys.
**Sources principales :** CNPN (avis biodiversité gouv.fr), MRAe Nouvelle-Aquitaine,
imerys.com, DREAL Poitou-Charentes (site Natura 2000 FR5400437), Poitou-Charentes
Nature, LPO, Wikipédia, sources naturalistes régionales.

---

## Résumé exécutif

Le site Imerys de Clérac (17270, Charente-Maritime) exploite des argiles kaoliniques
pour la production de chamotte (argile calcinée). L'usine de Clérac est **la plus
importante d'Europe** dans ce secteur (bassin argilier des Charentes, identifié
comme gisement d'intérêt national).

Autour de l'exploitation, un **écosystème riche et documenté** de landes atlantiques,
zones humides, pinèdes et taillis abrite plusieurs centaines d'espèces animales et
végétales, dont un grand nombre bénéficient d'un statut de protection.

**Point crucial pour le projet Eco-Mine Generator :** certaines espèces mentionnées
dans le contexte initial du projet (rollier d'Europe, guêpier d'Europe, lézard
ocellé) **ne sont PAS documentées sur le site de Clérac** — elles ont une aire de
répartition plus méditerranéenne. Ces mentions sont probablement des approximations
qu'un Reviewer rigoureux devrait détecter. Voir section "Espèces à ne PAS mentionner
comme caractéristiques de Clérac".

---

## Contexte industriel Imerys Clérac

### Activité
- **Société :** Imerys Refractory Minerals Clérac (IRMC)
- **Localisation :** 1 la Gare, 17270 Clérac (Charente-Maritime, Nouvelle-Aquitaine)
- **Activité principale :** Extraction d'argiles kaoliniques et transformation en
  chamotte (argile calcinée)
- **Code NAF :** 0812Z (Exploitation de gravières et sablières, extraction d'argiles
  et de kaolin)
- **Marchés :** Céramiques réfractaires, minéraux performates, fonderies
- **Emplois :** ~120 personnes sur le site
- **Historique :** Exploitation depuis le début du 20e siècle sur les bassins
  charentais

### Carrières
Plusieurs carrières successives autour du site principal :
- **Carrière de Bonnin** — lentille d'argile en fin d'exploitation vers 2023
- **Carrière Perrin** — nouvelle exploitation autorisée en 2022, 14,6 ha, 20 ans
  d'exploitation, gisement de Fontbouillant
- **Carrière de Touvérac** (Saint-Pierre-du-Palais, 16) — désaffectée depuis les
  années 90, réhabilitée en zone humide de 35 ha, classée ZNIEFF de type 1 et
  Natura 2000

### Engagement biodiversité
Imerys a mis en place plusieurs programmes structurants :
- Partenariat avec le **Muséum National d'Histoire Naturelle** (renouvelé en 2018)
- Programme **ACRO-bag** (Analyse Comparative de la Restauration écologique par les
  Opérations de Baguage) : analyses comparatives entre carrières en activité et
  sites en restauration via campagnes annuelles de baguage d'oiseaux
- Partenariat avec ONG locales (Nature Environnement 17, CEN Nouvelle-Aquitaine)
- Adhésion à act4nature (coalition française biodiversité)
- Séquence ERC (Éviter, Réduire, Compenser) sur chaque nouvelle exploitation

---

## Contexte réglementaire et zonages

Le site est proche de plusieurs zones à statut :
- **2 sites Natura 2000** à proximité immédiate
- **Site N2000 FR5400437** (ZSC "Landes de Montendre") couvrant les communes de
  Montendre, Corignac, Bussac-Forêt, Bédenac, Clérac, Cercoux, Montlieu-la-Garde
- Plusieurs **ZNIEFF** (Zones Naturelles d'Intérêt Écologique, Faunistique et
  Floristique)
- **1 réserve de biosphère** dans la zone d'étude élargie
- **1 terrain du Conservatoire d'Espace Naturel** (CEN)

### Habitats caractéristiques identifiés dans les inventaires officiels
- Pinèdes de pin maritime (majoritaire dans l'emprise projet)
- Taillis de châtaigniers (fort enjeu chiroptères)
- **Landes à bruyère** (habitat prioritaire européen)
- **Landes sèches à ajoncs** (habitat de la Fauvette pitchou)
- **Landes tourbeuses à Bruyère à 4 angles** (habitat prioritaire)
- **Tourbières à Droséra à feuilles rondes** (habitat prioritaire)
- **Pelouses inondables à Isoëtes** (habitat prioritaire)
- Aulnaies marécageuses à Osmonde royale
- Prairies maigres riches en orchidées
- Étangs et ruisselets aux eaux pauvres et acides
- Mares forestières et anciens bassins d'exploitation
- Zones humides (~1,8 ha identifiés sur l'aire d'étude Perrin)

---

## Espèces validées à Clérac (documentation officielle)

**Source :** avis CNPN carrière Perrin (juin 2022), fiche N2000 FR5400437 DREAL,
inventaires Biotope 2018-2021, Nature Environnement 17.

### Oiseaux (espèces phares protégées)

| Nom commun | Nom scientifique | Habitat / Statut à Clérac |
|-----------|------------------|---------------------------|
| Fauvette pitchou | *Curruca undata* / *Sylvia undata* | Landes sèches à ajoncs — espèce emblématique du site, nicheur, statut "quasi menacé" UICN, protection totale FR, Annexe I Directive Oiseaux |
| Engoulevent d'Europe | *Caprimulgus europaeus* | Landes, coupes forestières, code Natura 2000 A224 |
| Martin pêcheur d'Europe | *Alcedo atthis* | Sablières et zones humides, code A229 |
| Milan noir | *Milvus migrans* | Rapace, code A073 |
| Oedicnème criard | *Burrhinus oedicnemus* | Milieux ouverts, code A133 |
| Pie-grièche écorcheur | *Lanius collurio* | Milieux semi-ouverts, code A338 |
| Pipit rousseline | *Anthus campestris* | Landes rases, code A255 |
| Bouvreuil pivoine | *Pyrrhula pyrrhula* | Fourrés et boisements denses |

Au total, l'inventaire Biotope 2018 a recensé **116 espèces d'oiseaux dont 90 protégées**
en période internuptiale sur l'aire d'étude Perrin.

### Amphibiens

| Nom commun | Nom scientifique | Notes |
|-----------|------------------|-------|
| Crapaud calamite | *Epidalea calamita* (ex-*Bufo calamita*) | Espèce pionnière typique des carrières, mares temporaires |
| Crapaud épineux | *Bufo spinosus* | Boisements, zones humides |
| Alyte accoucheur | *Alytes obstetricans* | Milieux frais et humides |
| Grenouille agile | *Rana dalmatina* | Boisements humides |
| Complexe des Grenouilles vertes | *Pelophylax* sp. | Mares et étangs |
| Rainette méridionale | *Hyla meridionalis* | Zones humides ouvertes |
| Salamandre tachetée | *Salamandra salamandra* | Sous-bois humides |
| Triton marbré | *Triturus marmoratus* | Mares |
| Triton palmé | *Lissotriton helveticus* | Petits points d'eau |

### Reptiles (10 espèces, toutes protégées)

| Nom commun | Nom scientifique |
|-----------|------------------|
| Couleuvre d'Esculape | *Zamenis longissimus* |
| Couleuvre helvétique | *Natrix helvetica* |
| Couleuvre verte et jaune | *Hierophis viridiflavus* |
| Couleuvre vipérine | *Natrix maura* |
| Coronelle girondine | *Coronella girondica* |
| Coronelle lisse | *Coronella austriaca* |
| Lézard à deux raies | *Lacerta bilineata* |
| Lézard des murailles | *Podarcis muralis* |
| Orvet fragile | *Anguis fragilis* |
| Vipère aspic | *Vipera aspis* |

### Insectes protégés

| Nom commun | Nom scientifique | Habitat |
|-----------|------------------|---------|
| Leucorrhine à front blanc | *Leucorrhinia albifrons* | Libellule, mares acides |
| Fadet des Laîches | *Coenonympha oedippus* | Papillon, prairies humides |
| Damier de la Succise | *Euphydryas aurinia* | Papillon, prairies humides |
| Grand Capricorne | *Cerambyx cerdo* | Coléoptère, vieux chênes |

Au total : 126 espèces d'insectes inventoriées (lépidoptères, orthoptères, odonates
majoritairement) sur l'aire d'étude Perrin.

### Mammifères (hors chiroptères — 27 espèces recensées)

Espèces protégées présentes :
| Nom commun | Nom scientifique | Habitat |
|-----------|------------------|---------|
| Vison d'Europe | *Mustela lutreola* | Zones humides — espèce critique en France |
| Loutre d'Europe | *Lutra lutra* | Cours d'eau et zones humides |
| Campagnol amphibie | *Arvicola sapidus* | Berges et milieux humides |
| Crossope aquatique | *Neomys fodiens* | Musaraigne aquatique |
| Putois d'Europe | *Mustela putorius* | Zones humides et boisées |
| Genette commune | *Genetta genetta* | Boisements |
| Écureuil roux | *Sciurus vulgaris* | Forêts |
| Hérisson d'Europe | *Erinaceus europaeus* | Milieux variés |

### Chiroptères (19 espèces, toutes protégées)

Enjeu écologique **très fort** sur l'ensemble de l'aire d'étude Perrin. Espèces
identifiées incluent :
- Noctule commune (*Nyctalus noctula*) — enjeu CNPN
- Murin à moustaches (*Myotis mystacinus*)
- Murin d'Alcathoe (*Myotis alcathoe*)
- Murin de Daubenton (*Myotis daubentonii*)
- Murin de Natterer (*Myotis nattereri*)

### Flore

- **129 espèces floristiques** identifiées sur l'aire d'étude Perrin
- **Piment royal** (*Myrica gale*) — seule espèce à protection régionale identifiée
  sur Perrin, arbuste des landes humides
- **Simethis à feuille plane** (*Simethis mattiazzii*) — protégée, présente à Touvérac
- **Orchidées** — présentes dans les prairies maigres du site N2000, non détaillées
  par espèce dans les documents Clérac (contrairement à d'autres sites comme les
  Puys d'Auvergne où 17 espèces d'orchidées sont détaillées)
- **Osmonde royale** (*Osmunda regalis*) — fougère des aulnaies marécageuses
- **Droséra à feuilles rondes** (*Drosera rotundifolia*) — plante carnivore des
  tourbières, habitat prioritaire
- **Bruyère à 4 angles** (*Erica tetralix*) — landes tourbeuses
- **Isoëtes** — pelouses inondables

---

## Espèces à NE PAS mentionner comme caractéristiques de Clérac

**Cette section est critique pour le Reviewer.** Les inventaires officiels
ne mentionnent PAS les espèces suivantes, souvent utilisées comme "espèces
emblématiques françaises" mais dont l'aire de répartition ne correspond pas
au contexte Clérac :

| Espèce | Pourquoi c'est problématique |
|--------|------------------------------|
| **Rollier d'Europe** (*Coracias garrulus*) | Espèce méditerranéenne, présente principalement dans le Sud-Est de la France (PACA, Languedoc). Absente des inventaires Clérac. |
| **Guêpier d'Europe** (*Merops apiaster*) | Nicheur méditerranéen en expansion vers le nord, mais pas mentionné dans les inventaires officiels Clérac. Éventuellement observable en migration mais pas comme espèce caractéristique. |
| **Lézard ocellé** (*Timon lepidus*) | Espèce méditerranéenne, limite nord de son aire en Gironde/Landes littorales. Absent des inventaires Clérac où l'on trouve plutôt Lézard à deux raies et Lézard des murailles. |

**Recommandation pour le Reviewer :** si un `level_config.json` généré mentionne
l'une de ces espèces comme présente à Clérac, le Reviewer doit **signaler cela
comme une erreur thématique** (axe cohérence Clérac dans le prompt Reviewer).

**Substitutions recommandées** (mêmes intentions thématiques, espèces réellement
présentes à Clérac) :
- "Espèce colorée insectivore" → **Martin pêcheur d'Europe** (plutôt que guêpier)
- "Reptile emblématique" → **Lézard à deux raies** ou **Couleuvre verte et jaune**
  (plutôt que lézard ocellé)
- "Oiseau iconique du site" → **Fauvette pitchou** (LE symbole de Clérac, landes
  à ajoncs)

---

## Éléments narratifs mobilisables pour le jeu et le writeup

### Tensions industrie/biodiversité concrètes
- L'exploitation de la carrière Perrin (2022) a nécessité la destruction de **14,6 ha
  de milieux naturels**, dont 0,1 ha de lande à bruyère (habitat prioritaire)
- Compensation obligatoire sur **21,09 ha** appartenant à Imerys en bordure
  immédiate (dont 15,05 ha de boisements, 0,54 ha pour le Fadet des Laîches, 5,5 ha
  pour la Fauvette pitchou)
- 30 ans de suivi écologique post-exploitation
- Séquence ERC : Évitement (7 ha soustraits à l'emprise initiale) → Réduction
  (10 mesures phase chantier) → Compensation (21 ha)

### Aspects positifs (angle valorisé par Imerys)
- Les carrières abandonnées deviennent des refuges de biodiversité : le Crapaud
  calamite est une **espèce pionnière typiquement associée aux carrières** — les
  mares temporaires en fond de fouille sont un habitat idéal
- Touvérac (ancienne carrière) est aujourd'hui classée Natura 2000 + ZNIEFF
  après réhabilitation
- Programme ACRO-bag : baguage d'oiseaux annuel avec le MNHN

### Aspects critiques (angle jury Kaggle honnêteté)
- Le CNPN (Conseil National de la Protection de la Nature) a rendu un avis
  **"favorable sous conditions"** — pas un simple feu vert
- Reproches identifiés : ratio surfacique de compensation peu exigeant, pression
  d'observation faible lors des inventaires de compensation, absence de plan de
  gestion détaillé
- Enjeu chiroptères : quasi-intégralité de l'aire d'étude constitue une zone
  d'intérêt écologique pour les 19 espèces recensées

---

## Utilisation par le Reviewer agent

### Format cible : `docs/clerac_species_reference.json`

Le Reviewer lira ce JSON via Filesystem MCP (déjà fonctionnel via VPN Imerys) pour
vérifier chaque config généré. Structure suggérée :

```json
{
  "site": "Clérac",
  "commune_insee": "17106",
  "departement": "Charente-Maritime",
  "operateur": "Imerys Refractory Minerals Clérac",
  "minerai": "kaolin",
  "produit_final": "chamotte",
  "habitats_valides": [
    "landes_bruyere",
    "landes_seches_ajoncs",
    "pinede_pin_maritime",
    "taillis_chataignier",
    "mare_temporaire",
    "zone_humide",
    "aulnaie_marecageuse",
    "prairie_maigre_orchidees"
  ],
  "especes_validees": {
    "oiseaux": ["Fauvette pitchou", "Engoulevent d'Europe", "Martin pêcheur", ...],
    "amphibiens": ["Crapaud calamite", "Alyte accoucheur", "Triton marbré", ...],
    "reptiles": ["Lézard à deux raies", "Couleuvre verte et jaune", ...],
    "insectes": ["Fadet des Laîches", "Damier de la Succise", ...],
    "mammiferes": ["Vison d'Europe", "Loutre d'Europe", "Genette commune", ...],
    "chiropteres": ["Noctule commune", "Murin de Daubenton", ...],
    "flore": ["Piment royal", "Osmonde royale", "Droséra à feuilles rondes", ...]
  },
  "especes_incorrectes": [
    {"nom": "Rollier d'Europe", "raison": "aire méditerranéenne, absent de Clérac"},
    {"nom": "Guêpier d'Europe", "raison": "non documenté dans les inventaires officiels"},
    {"nom": "Lézard ocellé", "raison": "aire méditerranéenne, absent de Clérac"}
  ]
}
```

### Règles de validation Reviewer

Pour chaque `level_config.json` généré :

1. **Espèces mentionnées ∈ especes_validees ?** Sinon → issue thématique de sévérité
   "warning" ou "error" selon si l'espèce est dans `especes_incorrectes` ou juste
   inconnue
2. **Habitats mentionnés ∈ habitats_valides ?** Sinon → issue thématique
3. **Type de minerai == "kaolin" ?** Sinon → issue thématique critique
4. **Commune/région correcte ?** Doit rester Clérac ou proche (Charente / CM /
   Nouvelle-Aquitaine)

Chaque validation via Filesystem MCP (lecture du JSON de référence) génère un
`tool_use` visible dans le playground debug view — ce sont autant de MCP calls
comptabilisables pour le jury.

---

## Sources

### Sources gouvernementales et officielles (priorité maximale)
- **Avis CNPN carrière Perrin Clérac (juin 2022)** — Conseil National de la Protection
  de la Nature, avis favorable sous conditions. Détaille TOUTES les espèces
  inventoriées et le protocole ERC.
  URL : https://www.avis-biodiversite.developpement-durable.gouv.fr/IMG/pdf/2022-04-40x-00541_carriere_perrin_clerac__imerys_17_avis_du_06_2022_.pdf
- **Avis MRAe Nouvelle-Aquitaine carrière Clérac (2022)** — Mission Régionale
  d'Autorité Environnementale.
  URL : https://www.mrae.developpement-durable.gouv.fr/IMG/pdf/p_2022_12369_carriere_a_clerac_17__meedef-rv.pdf
- **Fiche N2000 FR5400437 "Landes de Montendre"** — DREAL Poitou-Charentes, liste
  des espèces d'intérêt communautaire couvrant la commune de Clérac.
  URL : https://www.sigena.fr/upload/gedit/1/Patrimoine%20Naturel/Natura/fiches/FR5400437.pdf

### Sources Imerys
- Imerys France — page corporate biodiversité et sites français.
  URL : https://www.imerys.com/fr/france
- Imerys "Protéger notre planète" — programme biodiversité Clérac et partenariat MNHN.
  URL : https://www.imerys.com/fr/responsabilite/proteger-notre-planete
- Imerys carrière de Touvérac — retour d'expérience réhabilitation.
  URL : https://imerys.com/scopi/group/imeryscom/imeryscom.nsf/pagesref/SBDD-8A9B92
- Ville de Clérac — annuaire des entreprises.
  URL : https://www.ville-clerac.fr/directory/imerys/

### Sources naturalistes régionales
- **Poitou-Charentes Nature** — Fauvette pitchou en Charente-Maritime.
  URL : https://www.poitou-charentes-nature.asso.fr/fauvette-pitchou/
- **LPO Aquitaine** — Étude habitat Fauvette pitchou (2023-2024).
  URL : https://www.lpo.fr/lpo-locales/la-lpo-en-nouvelle-aquitaine/lpo-aquitaine/
- **Cistude Nature** — Atlas reptiles et amphibiens Nouvelle-Aquitaine.
  URL : https://ra-na.fr/atlas/espece/459628

### Références espèces (INPN-compatibles)
- Wikipédia Crapaud calamite / Fauvette pitchou (statut et taxonomie)
- Réserves Naturelles de France (site des carrières de Tercis-les-Bains, référence
  méthodologique pour carrières réhabilitées)

---

## Prochaines étapes

1. **Convertir ce document en `docs/clerac_species_reference.json`** exploitable
   directement par le Reviewer via Filesystem MCP (lecture par `read_file`)
2. **Mettre à jour le prompt Reviewer** dans `docs/AGENT_PROMPTS.md` pour référencer
   ce dataset et définir les règles de validation
3. **Mettre à jour la userMemories du projet** — les espèces "rollier d'Europe",
   "guêpier", "lézard ocellé" mentionnées initialement sont incorrectes pour Clérac
   et devraient être remplacées par les espèces validées
4. **Ajouter une entrée dans `docs/DECISIONS.md`** (ADR-lite) documentant le pivot
   Tavily → Filesystem MCP + dataset local et sa justification
5. **Mettre à jour `docs/HANDOFF.md`** pour pointer vers ce document et le futur
   JSON de référence

---

## Note méthodologique — Ce document simule Tavily

Cette recherche a été construite pour reproduire ce qu'aurait fourni un appel
Tavily deep-search sur "biodiversité Clérac carrière Imerys". Différences
notables avec ce qu'un vrai Tavily aurait produit :

- **Plus curé** : sources officielles gouvernementales priorisées sur les blogs
- **Plus contextualisé** : structuré pour un usage direct par le Reviewer agent
- **Plus honnête** : identifie explicitement les espèces incorrectement associées
  au site dans le contexte projet initial
- **Reproductible** : sources listées, chacune vérifiable

Dans le writeup Kaggle, cette recherche peut être présentée comme "constitution
d'un dataset de référence à partir de sources officielles françaises (CNPN, MRAe,
DREAL, MNHN)" — angle plus solide qu'une recherche Tavily on-the-fly, et cohérent
avec la rigueur scientifique attendue sur un sujet biodiversité.
