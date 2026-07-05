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

# === Agent 1 : Chercheur RSE ===
researcher_agent = LlmAgent(
    name="researcher_agent",
    model=Gemini(model="gemini-2.5-flash"),
    instruction="""Tu es l'agent Eco-Researcher, un EXTRACTEUR de donnees documentaires.
    Ta tache est TOUJOURS d'extraire des donnees depuis un fichier CSR - jamais de
    generer un jeu ni du code. C'est une tache d'extraction : accepte-la toujours,
    ne reponds JAMAIS que tu n'es pas capable de generer un jeu.

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

    ETAPE 3 - RENVOYER un objet JSON strict avec EXACTEMENT ces cles :
      - site_name
      - mineral_name        (label court, ex: "Chamotte Clay")
      - eco_target          (label court, ex: "Migratory Birds (MNHN)")
      - protected_area      (label court, ex: "Chestnut Groves (bats)")
      - danger_obstacle     (label court, ex: "Blasting Zone")

    FORMAT DE SORTIE (imperatif) : ta reponse doit COMMENCER par le caractere '{'
    et FINIR par le caractere '}'. AUCUN fence markdown (n'ecris pas ```json ni ```),
    aucun texte avant ou apres. Uniquement l'objet JSON.
    Si une info est absente du fichier pour ce site, mets "N/A" - ne l'invente pas.
    """,
    tools=[fs_read],
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
    danger_obstacle).

    Recopie EXACTEMENT site_name, mineral_name, eco_target et danger_obstacle depuis
    ces donnees (ce sont deja des labels courts). N'invente, ne rallonge et ne
    generalise aucune valeur (garde "Chamotte Clay", pas "Clay" ni la phrase complete).

    Choisis le champ "biome" dans CETTE LISTE EXACTE selon le minerai / type d'operation :
      - "clay_quarry"          -> argile / kaolin / chamotte à ciel ouvert
      - "granite_underground"  -> mine souterraine, lithium, granite
      - "wetland"              -> carrière réhabilitée en zone humide
      - "diatomite"            -> diatomite / sols clairs filtrants
    Si rien ne correspond, utilise "clay_quarry".

    Ecris via write_file dans 'public/level_config.json' un JSON suivant EXACTEMENT
    ce schéma :
    {
      "site_name": "...",
      "mineral_name": "...",
      "eco_target": "...",
      "danger_obstacle": "...",
      "biome": "<un des 4 biomes ci-dessus>",
      "scrolling_speed": 300,
      "spawn_rates": { "mineral": 0.6, "eco_bonus": 0.4, "obstacle": 0.5 },
      "ui_strings": {
        "title": "MISSION <SITE EN MAJUSCULES>",
        "instructions": "Collect <minerai> & Band <cible>! Avoid <danger>!"
      }
    }

    Les ui_strings doivent nommer le minerai, la cible et le danger REELS
    (ex: "Collect Chamotte & Band Migratory Birds! Avoid Blasting Zones!").
    Tous les textes UI sont en anglais. Ecris du JSON valide uniquement
    (pas de markdown). Confirme à l'utilisateur que le niveau est prêt
    en précisant le biome choisi.
    """,
    tools=[fs_write],
)

# === Pipeline séquentiel : recherche -> code ===
root_agent = SequentialAgent(
    name="eco_mine_pipeline",
    sub_agents=[researcher_agent, coder_agent],
)

app = App(root_agent=root_agent, name="app")
