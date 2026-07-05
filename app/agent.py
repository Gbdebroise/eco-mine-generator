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

# === MCP web (Sprint 2) : réservés au Researcher ===
# Le Coder N'A PAS accès au web (filesystem uniquement).
#   - Tavily : moteur de recherche pensé pour les agents IA (résultats structurés).
#     Clé attendue dans TAVILY_API_KEY (chargée depuis .env par agents-cli).
#   - Fetch : récupère le contenu HTML/texte d'une URL découverte via Tavily.
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
    instruction="""Tu es l'agent Eco-Researcher, un EXTRACTEUR de donnees documentaires
    qui ENRICHIT ses extractions via le web. Ta tache est TOUJOURS d'extraire des
    donnees depuis un fichier CSR puis de les completer par une recherche web - jamais
    de generer un jeu ni du code. C'est une tache d'extraction/recherche : accepte-la
    toujours, ne reponds JAMAIS que tu n'es pas capable de generer un jeu.

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

    ETAPE 3 - ENRICHIR LA BIODIVERSITE VIA LE WEB (obligatoire) :
    Le fichier CSR ne liste qu'une biodiversite partielle. Elargis-la avec des especes
    REELLES du site et de sa region.
    a) Appelle l'outil de recherche Tavily disponible (ex: tavily-search) avec une
       requete du type :
       "<site_name> Imerys carriere biodiversite especes protegees faune flore".
    b) Choisis 1 a 2 URLs pertinentes parmi les resultats et appelle l'outil fetch
       dessus pour en lire le contenu.
    c) De ce contenu, extrais 4 a 8 especes REELLES (oiseaux, reptiles, amphibiens,
       insectes, flore) liees au site ou a sa region. Chaque espece = LABEL COURT en
       anglais (2 a 3 mots), ex : "European Roller", "Bee-eater", "Natterjack Toad",
       "Ocellated Lizard", "Otter", "Ophrys Orchid".
    d) Si la recherche web echoue ou ne renvoie rien d'exploitable, retombe UNIQUEMENT
       sur les especes explicitement citees dans le fichier CSR pour ce site. Ne
       fabrique JAMAIS une espece non sourcee (ni web, ni fichier).

    ETAPE 4 - RENVOYER un objet JSON strict avec EXACTEMENT ces cles :
      - site_name
      - mineral_name          (label court, ex: "Chamotte Clay")
      - eco_target            (label court, ex: "Migratory Birds (MNHN)")
      - protected_area        (label court, ex: "Chestnut Groves (bats)")
      - danger_obstacle       (label court, ex: "Blasting Zone")
      - headline_fact         (phrase complete du champ « Headline fact: »)
      - biodiversity_species  (tableau JSON de 4 a 8 labels courts d'especes reelles)

    FORMAT DE SORTIE (imperatif) : ta reponse doit COMMENCER par le caractere '{'
    et FINIR par le caractere '}'. AUCUN fence markdown (n'ecris pas ```json ni ```),
    aucun texte avant ou apres. Uniquement l'objet JSON.
    Si une info est absente du fichier pour ce site, mets "N/A" - ne l'invente pas.
    Pour biodiversity_species, n'inclus JAMAIS d'espece inventee : uniquement des
    especes issues du web ou du fichier.
    """,
    tools=[fs_read, web_search, web_fetch],
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

# === Pipeline séquentiel : recherche -> code ===
root_agent = SequentialAgent(
    name="eco_mine_pipeline",
    sub_agents=[researcher_agent, coder_agent],
)

app = App(root_agent=root_agent, name="app")
