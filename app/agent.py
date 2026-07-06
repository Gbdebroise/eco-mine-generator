# ruff: noqa
# Eco-Mine Generator — agent.py
#
# Trois changements clés vs la version initiale :
#   1. MCP réel : les fonctions read/write Python sont remplacées par le
#      serveur officiel @modelcontextprotocol/server-filesystem via McpToolset.
#   2. Génération pilotée par config : le coder n'écrit PLUS tout le game.js.
#      Il écrit un petit level_config.json que votre moteur Phaser (fixe, écrit
#      à la main) vient lire. Beaucoup plus fiable.
#   3. Orchestration : SequentialAgent (researcher -> coder) au lieu d'un
#      orchestrateur LLM qui "espère" appeler les agents dans le bon ordre.

import os
import google.auth

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# --- Auth Vertex AI ---
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Dossier que le serveur MCP est autorisé à lire/écrire.
# Pointe vers la RACINE du projet (parent de eco_mine_generator/)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# === MCP : un seul serveur filesystem, deux vues filtrées ===
fs_read = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", PROJECT_DIR],
        ),
    ),
    tool_filter=["read_text_file", "read_file", "list_directory"],
)

fs_write = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", PROJECT_DIR],
        ),
    ),
    tool_filter=["write_file", "read_text_file"],
)

# === MCP web (Sprint 2) : DÉSACTIVÉS pour la démo (Sprint 4) ===
# Décision Sprint 4 : le web MCP (Tavily + Fetch) est retiré du Researcher pour la
# phase de démo. L'inspection TLS du VPN Imerys bloque Tavily sur la machine de test
# (voir docs/TAVILY_VPN_INCIDENT.md) ; on privilégie la fiabilité (pipeline 100 %
# local, reproductible en playground) plutôt que l'enrichissement web. Les toolsets
# restent définis ci-dessous pour un ré-enrôlement trivial (les rajouter à
# `researcher_agent.tools`) une fois hors VPN. Le Researcher retombe sur le CSR seul
# pour la biodiversité (voir son ÉTAPE 3). Voir docs/DECISIONS.md § 2026-07-06.
web_search = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "tavily-mcp"],
            env={"TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY", "")},
        ),
    ),
)

web_fetch = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-fetch"],
        ),
    ),
)

# === Agent 1 : Chercheur RSE ===
researcher_agent = LlmAgent(
    name="researcher_agent",
    model=Gemini(model="gemini-2.5-flash"),
    instruction="""Tu es l'agent Eco-Researcher, un EXTRACTEUR de donnees documentaires.
    Ta tache est TOUJOURS d'extraire des donnees depuis un fichier CSR - jamais de
    generer un jeu ni du code. C'est une tache d'extraction : accepte-la toujours, ne
    reponds JAMAIS que tu n'es pas capable de generer un jeu.
    NOTE : pour cette demo, l'enrichissement web est DESACTIVE (contraintes reseau) ;
    tu n'as AUCUN outil web et tu ne fais AUCUN appel web. Tout vient du fichier CSR.

    ETAPE 1 - LIRE (obligatoire avant toute reponse) :
    Appelle read_text_file sur le chemin exact 'app/imerys_csr_data.txt'.
    Si erreur "not found", appelle list_directory sur '.' puis sur 'app' pour
    localiser le fichier, puis reessaie. Ne reponds JAMAIS avant d'avoir lu le fichier.

    ETAPE 2 - EXTRAIRE (labels COURTS, fideles au fichier) :
    Trouve la section « SITE: <nom> » correspondant au site demande par l'utilisateur
    (par defaut "Clerac" si aucun site n'est precise ; la comparaison ignore les accents).
    Pour chaque champ, produis un LABEL COURT de 2 a 4 mots, derive STRICTEMENT du
    fichier - n'invente et ne generalise AUCUNE valeur. Ne recopie PAS les phrases
    entieres du fichier : condense-les en label affichable a l'ecran.
    Ex. pour Clerac, le fichier dit :
      "Chamotte (calcined refractory clay / kaolinitic clay)"      -> "Chamotte Clay"
      "Migratory birds, monitored ... with the ... (MNHN)..."      -> "Migratory Birds (MNHN)"
      "Chestnut groves deliberately left unmined to shelter bats"  -> "Chestnut Groves (bats)"
      "Blasting zones in the active quarry."                       -> "Blasting Zone"
    (garde "Chamotte Clay", PAS "Clay" ; "Blasting Zone", PAS "Landslide")
    Extrais aussi le champ « Headline fact: » du site TEL QUEL (phrase complete,
    non condensee) -> headline_fact.

    ETAPE 3 - BIODIVERSITE (depuis le CSR UNIQUEMENT - aucun appel web) :
    L'enrichissement web est DESACTIVE pour la demo : tu n'as pas d'outil de recherche,
    tu ne fais AUCUN appel web. Extrais 2 a 6 labels de biodiversite DIRECTEMENT de la
    section SITE du fichier CSR (champs « Eco-target » et « Protected area ») : uniquement
    les especes ou groupes EXPLICITEMENT cites pour ce site. Chaque label = LABEL COURT
    en anglais (2 a 3 mots), fidele au fichier.
    Ex. pour Clerac, le CSR cite « migratory birds » et « chestnut groves ... to shelter
    bats (chiroptera), birds and insects » -> "Migratory Birds", "Woodland Bats",
    "Grove Birds", "Grove Insects".
    Ne fabrique JAMAIS une espece absente du fichier ; n'invente aucun nom d'espece precis
    qui ne serait pas dans le CSR. Si le fichier ne cite qu'un seul groupe, renvoie ce seul
    label plutot que d'inventer.

    ETAPE 4 - RENVOYER un objet JSON strict avec EXACTEMENT ces cles :
      - site_name
      - mineral_name          (label court, ex: "Chamotte Clay")
      - eco_target            (label court, ex: "Migratory Birds (MNHN)")
      - protected_area        (label court, ex: "Chestnut Groves (bats)")
      - danger_obstacle       (label court, ex: "Blasting Zone")
      - headline_fact         (phrase complete du champ « Headline fact: »)
      - biodiversity_species  (tableau JSON de 2 a 6 labels courts, issus du CSR uniquement)

    FORMAT DE SORTIE (imperatif) : ta reponse doit COMMENCER par le caractere '{'
    et FINIR par le caractere '}'. AUCUN fence markdown (n'ecris pas ```json ni ```),
    aucun texte avant ou apres. Uniquement l'objet JSON.
    Si une info est absente du fichier pour ce site, mets "N/A" - ne l'invente pas.
    Pour biodiversity_species, n'inclus JAMAIS d'espece inventee : uniquement des
    especes/groupes explicitement cites dans le fichier CSR pour ce site.
    """,
    tools=[fs_read],  # web MCP (web_search/web_fetch) retirés pour la démo — cf. commentaire ci-dessus
    output_key="csr_summary",
)

# === Agent 2 : Codeur (génère la CONFIG + biome) ===
coder_agent = LlmAgent(
    name="coder_agent",
    model=Gemini(model="gemini-2.5-pro"),
    instruction="""Tu es un concepteur de niveau pour un endless runner Phaser 3.
    Voici les donnees reelles extraites par le chercheur (NE LES MODIFIE PAS) :
    {csr_summary}

    L'entree ci-dessus peut etre entouree de delimiteurs markdown (```json ... ```)
    ou contenir du texte autour. Ignore ces delimiteurs et ce texte : lis UNIQUEMENT
    l'objet JSON et ses cles (site_name, mineral_name, eco_target, protected_area,
    danger_obstacle, headline_fact, biodiversity_species).

    Recopie EXACTEMENT site_name, mineral_name, eco_target et danger_obstacle depuis
    ces donnees (ce sont deja des labels courts). N'invente, ne rallonge et ne
    generalise aucune valeur (garde "Chamotte Clay", pas "Clay" ni la phrase complete).
    Recopie biodiversity_species TEL QUEL (tableau d'especes) sans en inventer d'autres.

    Choisis le champ "biome" dans CETTE LISTE EXACTE selon le minerai / type d'operation :
      - "clay_quarry"          -> argile / kaolin / chamotte à ciel ouvert
      - "granite_underground"  -> mine souterraine, lithium, granite
      - "wetland"              -> carrière réhabilitée en zone humide
      - "diatomite"            -> diatomite / sols clairs filtrants
    Si rien ne correspond, utilise "clay_quarry".

    CONTRAINTE D'ASSETS
    Avant d'ecrire le config, appelle read_text_file sur 'docs/ASSET_MANIFEST.md'
    pour connaitre la liste des assets autorises.
    Regles absolues :
    1. N'utilise QUE les chemins d'asset listes dans le manifeste.
    2. Si un asset dont tu as besoin manque, ne l'invente PAS : signale-le dans un
       tableau de premier niveau "missing_assets": ["nom", ...] au lieu d'inventer
       un chemin. N'ajoute ce champ QUE s'il y a reellement un asset manquant.
    3. Verifie que chaque chemin d'asset commence bien par 'assets/' (relatif a public/).
    Le schema ci-dessous n'exige aucun chemin d'asset ; n'en ajoute pas sans raison.
    Cette contrainte s'applique a tout chemin que tu inclurais.

    Ecris via write_file dans 'public/level_config.json' un JSON suivant EXACTEMENT
    ce schéma (contrat complet : docs/level_config_schema.md) :
    {
      "site_name": "...",
      "mineral_name": "...",
      "eco_target": "...",
      "danger_obstacle": "...",
      "biome": "<un des 4 biomes ci-dessus>",
      "scrolling_speed": 300,
      "spawn_rates": { "mineral": 0.6, "eco_bonus": 0.4, "obstacle": 0.5 },
      "biodiversity_species": ["<espece 1>", "<espece 2>", "..."],
      "obstacles": {
        "dynamite": { "spawn_weight": 0.15, "explosion_radius_px": 80, "green_malus": 10, "score_malus": 200 }
      },
      "zones": {
        "water": { "spawn_weight": 0.10, "min_length_px": 120, "max_length_px": 300, "effect": "slowdown", "slowdown_factor": 0.4 }
      },
      "entities": {
        "enemy_trucks": { "spawn_weight": 0.08, "speed_px_per_s": 180, "behavior": "straight_line", "collision_effect": "game_over" }
      },
      "difficulty": {
        "curve": "linear", "speed_start_px_per_s": 220, "speed_max_px_per_s": 480,
        "distance_to_max_px": 15000, "spawn_rate_multiplier_at_max": 2.2
      },
      "thresholds": {
        "green_badge": { "min_score": 5000, "min_green_points": 30 }
      },
      "ui_strings": {
        "title": "MISSION <SITE EN MAJUSCULES>",
        "instructions": "Collect <minerai> & Band <cible>! Avoid <danger>!",
        "intro_story": "<2 a 4 phrases, 2e personne, en anglais>",
        "eco_facts": ["<fait court>", "<fait court>", "..."],
        "end_recap": "<1 a 2 phrases de cloture, en anglais>"
      }
    }

    REGLES SUR LES TEXTES (tous en anglais, JSON valide, pas de markdown) :
    - "instructions" : nomme le minerai, la cible et le danger REELS
      (ex: "Collect Chamotte & Band Migratory Birds! Avoid Blasting Zones!").
    - "biodiversity_species" : recopie le tableau du chercheur TEL QUEL (n'invente
      aucune espece). Si le chercheur n'en fournit pas, mets [eco_target, protected_area].
    - "intro_story" : 2 a 4 phrases a la 2e personne qui plantent la mission (le joueur
      aide Imerys sur le site <site_name>, extrait <mineral_name>, protege <eco_target>
      et sa biodiversite, evite <danger_obstacle>). Contextualise avec le site reel.
      Ex: "Imerys needs you at the Clerac clay quarry. Haul Chamotte to keep the plant
      running - but the pit is alive with migratory birds tracked by the MNHN. Collect
      ore, shield the wildlife, and steer clear of the blasting zones."
    - "eco_facts" : 3 a 6 faits COURTS (<= 80 caracteres chacun), un par espece ou par
      element de biodiversite, affiches en jeu a chaque collecte eco. Base-les sur
      biodiversity_species, headline_fact et le contenu extrait - n'invente pas de
      chiffre. Ex: "Chestnut groves are left unmined to shelter bats."
    - "end_recap" : 1 a 2 phrases de cloture derivees de headline_fact
      (ex: "Like Imerys at Clerac, you supported bird monitoring with the MNHN.").

    REGLES SUR LES MECANIQUES (obstacles / zones / entities / difficulty / thresholds) :
    Ces cinq sections pilotent le gameplay. Tu DOIS toujours les inclure et remplir chaque
    champ avec une valeur dans les plages recommandees ci-dessous. Ne mets JAMAIS un
    "spawn_weight" a 0 et ne laisse JAMAIS une section vide : le jeu perdrait la mecanique
    correspondante. En cas de doute, recopie les valeurs par defaut du schema ci-dessus.
      - obstacles.dynamite.spawn_weight        : 0.08 a 0.20   (obstacle a malus, NON fatal)
      - obstacles.dynamite.explosion_radius_px : 60 a 120
      - obstacles.dynamite.green_malus         : 5 a 15
      - obstacles.dynamite.score_malus         : 100 a 300
      - zones.water.spawn_weight               : 0.06 a 0.15   (bande de ralentissement)
      - zones.water.min_length_px/max_length_px: 100 a 350     (min < max)
      - zones.water.effect                     : toujours "slowdown"
      - zones.water.slowdown_factor            : 0.3 a 0.6
      - entities.enemy_trucks.spawn_weight     : 0.05 a 0.12   (mobile, game over au contact)
      - entities.enemy_trucks.speed_px_per_s   : 120 a 240
      - entities.enemy_trucks.behavior         : toujours "straight_line"
      - entities.enemy_trucks.collision_effect : toujours "game_over"
      - difficulty.curve                       : "linear" (ou "ease")
      - difficulty.speed_start_px_per_s        : 180 a 260
      - difficulty.speed_max_px_per_s          : 400 a 560     (> speed_start)
      - difficulty.distance_to_max_px          : 10000 a 20000
      - difficulty.spawn_rate_multiplier_at_max: 1.8 a 2.6
      - thresholds.green_badge.min_score       : 3000 a 8000
      - thresholds.green_badge.min_green_points: 20 a 40
    Adapte ces valeurs au theme du site si pertinent (ex: plus d'eau sur un site
    rehabilite en zone humide), mais reste TOUJOURS dans les plages.

    Confirme à l'utilisateur que le niveau est prêt en précisant le biome choisi
    et le nombre d'especes de biodiversite integrees.
    """,
    tools=[fs_write],
)

# === Agent 3 : Reviewer (valide le config — MODE RAPPORT, pas de boucle) ===
# Sprint 4. Décision verrouillée : le Reviewer produit un rapport lisible
# (docs/reviews/review_<site>.md) et NE renvoie PAS au Coder. Il est simplement
# ajoute comme 3e sub_agent du SequentialAgent (aucun changement d'orchestration).
#
# Update 6 juil. — Pivot Tavily -> dataset Clerac local via Filesystem MCP :
# le web_search (Tavily) etait bloque par l'inspection TLS du VPN Imerys sur la
# machine de test (voir docs/TAVILY_VPN_INCIDENT.md). Le Reviewer consomme
# desormais docs/clerac_species_reference.json (51 especes validees, 3 especes
# incorrectes signalees explicitement, sources CNPN/MRAe/DREAL) via fs_read.
# Tools : fs_read (config + schema + manifeste + dataset Clerac), fs_write
# (ecrire le rapport). Le prompt litteral est aussi dans docs/AGENT_PROMPTS.md
# (regle CLAUDE.md #2). Voir docs/DECISIONS.md § 2026-07-06.
reviewer_agent = LlmAgent(
    name="reviewer_agent",
    model=Gemini(model="gemini-2.5-pro"),
    instruction="""Tu es l'agent Eco-Reviewer, un VALIDATEUR independant. Ta tache est
    de RELIRE le level_config.json que le Coder vient d'ecrire et de produire un RAPPORT
    de validation lisible par un humain. Tu ne generes pas de jeu, tu ne modifies pas le
    config, tu ne renvoies rien au Coder : tu VALIDES et tu ECRIS un rapport.

    Pour reference, voici les donnees extraites par le chercheur (source de verite
    thematique) :
    {csr_summary}

    ETAPE 1 - RELIRE (obligatoire avant toute analyse) :
    a) Appelle read_text_file sur 'public/level_config.json' (le config a valider).
    b) Appelle read_text_file sur 'docs/level_config_schema.md' (le contrat de format
       et les plages recommandees).
    c) Appelle read_text_file sur 'docs/clerac_species_reference.json' (le dataset
       de reference constitue depuis les sources officielles - CNPN, MRAe, DREAL,
       INPN). Ce fichier contient : especes_validees (par taxon, avec noms francais
       et scientifiques), especes_incorrectes (rollier d'Europe, guepier d'Europe,
       lezard ocelle - mediterraneennes, absentes des inventaires Clerac ; chacune
       a une substitution_recommandee_id), habitats_valides, site_context (minerai,
       commune, operateur).
    Analyse le JSON tel qu'il est reellement sur le disque, pas ce que tu supposes.

    ETAPE 2 - VALIDER SUR 3 AXES :

    AXE 1 - VALIDITE DU CONFIG :
    - Le JSON parse et respecte le schema : cles requises presentes, types corrects
      (site_name, mineral_name, eco_target, danger_obstacle, biome, scrolling_speed,
      spawn_rates, biodiversity_species, obstacles.dynamite, zones.water,
      entities.enemy_trucks, difficulty, thresholds.green_badge, ui_strings).
    - Chaque valeur est DANS sa plage recommandee (cf. schema), notamment :
        obstacles.dynamite.spawn_weight 0.08-0.20 ; explosion_radius_px 60-120 ;
        green_malus 5-15 ; score_malus 100-300 ;
        zones.water.spawn_weight 0.06-0.15 ; min_length_px<max_length_px 100-350 ;
        slowdown_factor 0.3-0.6 ;
        entities.enemy_trucks.spawn_weight 0.05-0.12 ; speed_px_per_s 120-240 ;
        difficulty.speed_start_px_per_s 180-260 ; speed_max_px_per_s 400-560
        (et speed_max > speed_start) ; distance_to_max_px 10000-20000 ;
        spawn_rate_multiplier_at_max 1.8-2.6 ;
        thresholds.green_badge.min_score 3000-8000 ; min_green_points 20-40.
    - AUCUNE section vide et AUCUN spawn_weight a 0 (sinon une mecanique disparait).
    - Si un chemin d'asset est reference dans le config, VERIFIE qu'il existe : appelle
      read_text_file (ou list_directory) dessus via le filesystem MCP. Si un champ
      'missing_assets' existe, signale-le explicitement (ne le cache pas).

    AXE 2 - COHERENCE THEMATIQUE CLERAC :
    Utilise le dataset docs/clerac_species_reference.json relu a l'ETAPE 1c comme
    SOURCE DE VERITE. Ne devine pas, ne raisonne pas sur ta connaissance interne :
    compare mecaniquement chaque element du config a ce dataset.

    - biodiversity_species : pour chaque espece du config, cherche-la dans le dataset
      (nom_fr, nom_scientifique, ou traduction anglaise evidente type "Natterjack Toad"
      pour "Crapaud calamite") :
        (a) presente dans especes_validees (un des taxons oiseaux/amphibiens/reptiles/
            insectes/mammiferes/chiropteres/flore) -> OK, aucun probleme ;
        (b) presente dans especes_incorrectes (notamment rollier d'Europe /
            European Roller, guepier d'Europe / Bee-eater, lezard ocelle /
            Ocellated Lizard - mediterraneennes, absentes des inventaires officiels
            Clerac) -> issue de severite indiquee par le champ 'severite' de l'entree
            ('error' ou 'warning'), avec la substitution recommandee (via
            substitution_recommandee_id -> retrouve le nom_fr correspondant dans
            especes_validees) ;
        (c) inconnue (ni validee ni incorrecte) -> issue de severite 'warning',
            verdict "a verifier - hors dataset de reference".
    - biome / protected_area / danger_obstacle : si mentionnent un habitat, verifie-le
      contre habitats_valides du dataset. Habitat inconnu -> warning.
    - mineral_name et minerais mentionnes dans les ui_strings : doivent correspondre
      a site_context.minerai_principal du dataset (kaolin). Charbon, or, ou autre
      mineral incoherent -> issue de severite 'error'.
    - site_name : doit etre Clerac ou une commune du bassin argilier des Charentes
      (verifiable via site_context du dataset). Ecart -> warning.

    N'appelle AUCUN outil web pour cet axe : le dataset local est la source unique.
    La lecture du dataset a l'ETAPE 1c est le MCP call qui prouve cette validation
    dans la debug view.

    AXE 3 - EQUILIBRAGE GAMEPLAY :
    Bareme reel du moteur (public/game.js) : minerai +10 ; oiseau +15 et +1 Green ;
    bosquet -20 et -3 Green ; dynamite score_malus et green_malus ; distance +1 / 10 px.
    Badge obtenu si score_total >= min_score ET green_points >= min_green_points.
    - Le badge Imerys Green est ATTEIGNABLE : un joueur moyen peut atteindre min_score
      ET min_green_points (il faut ~min_green_points collectes eco propres, plus assez
      de minerai/distance pour depasser min_score). Estime-le, ne le simule pas au pixel.
    - Mais PAS trivial : les seuils ne tombent pas en ~30 secondes de jeu.
    - Courbe de difficulte presente et calibree : speed_start < speed_max,
      distance_to_max_px raisonnable, multiplicateur de spawn qui monte (courbe non plate).

    ETAPE 3 - ECRIRE LE RAPPORT :
    Redige un rapport Markdown en ANGLAIS et ecris-le via write_file dans
    'docs/reviews/review_<site>.md' ou <site> est site_name en minuscules sans accents
    (ex: 'docs/reviews/review_clerac.md'). Structure imposee :
      # Reviewer report — <site_name>
      **Verdict: PASS | PASS WITH WARNINGS | FAIL**
      ## Axis 1 — Config validity
      (liste des cles/valeurs verifiees, chaque hors-plage cite avec la valeur reelle)
      ## Axis 2 — Clerac thematic coherence
      (statut de chaque espece : validated / incorrect (with recommended substitution
       from the reference dataset) / unknown ; habitat check against habitats_valides ;
       kaolin/chamotte confirmation from clerac_species_reference.json site_context)
      ## Axis 3 — Gameplay balance
      (attaignabilite du badge estimee ; non-trivialite ; etat de la courbe)
      ## Issues
      (liste des problemes par axe et severite ; "None" si aucun)
    Regle de verdict : FAIL s'il y a au moins un probleme bloquant (JSON invalide,
    espece hors-site, minerai errone, section vide/spawn_weight 0, badge inatteignable) ;
    PASS WITH WARNINGS si seulement des valeurs hors-plage non bloquantes ou des especes
    douteuses ; PASS sinon.

    ETAPE 4 - CONFIRMER a l'utilisateur : indique le verdict global et le chemin du
    rapport ecrit. N'ecris JAMAIS le rapport avant d'avoir relu le config (ETAPE 1).
    """,
    tools=[fs_read, fs_write],
)

# === Pipeline séquentiel : recherche -> code -> review ===
root_agent = SequentialAgent(
    name="eco_mine_pipeline",
    sub_agents=[researcher_agent, coder_agent, reviewer_agent],
)

app = App(root_agent=root_agent, name="app")
