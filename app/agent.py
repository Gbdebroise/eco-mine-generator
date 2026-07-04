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
    instruction="""Tu es l'agent Eco-Researcher.
    Utilise l'outil read_text_file pour lire le fichier 'imerys_csr_data.txt'.
    Trouve la section correspondant au site demandé par l'utilisateur.
    Extrais et renvoie UNIQUEMENT un objet JSON avec ces clés :
      - site_name
      - mineral_name        (ex: "Chamotte Clay")
      - eco_target          (ex: "Migratory Birds (MNHN)")
      - protected_area      (ex: "Chestnut groves / bats")
      - danger_obstacle     (ex: "Blasting Zone")
    Pas de markdown, pas de texte autour. Juste le JSON.
    """,
    tools=[fs_read],
    output_key="csr_summary",
)

# === Agent 2 : Codeur (génère la CONFIG + biome) ===
coder_agent = LlmAgent(
    name="coder_agent",
    model=Gemini(model="gemini-2.5-pro"),
    instruction="""Tu es un concepteur de niveau pour un endless runner Phaser 3.
    Voici les données environnementales réelles extraites par le chercheur :
    {csr_summary}

    À partir de ces données, génère le contenu d'un fichier de configuration de
    niveau, puis écris-le avec l'outil write_file dans 'public/level_config.json'.

    Choisis le champ "biome" dans CETTE LISTE EXACTE selon le site :
      - "clay_quarry"          -> carrière argile / kaolin / chamotte à ciel ouvert
      - "granite_underground"  -> mine souterraine, lithium, granite
      - "wetland"              -> carrière réhabilitée en zone humide
      - "diatomite"            -> diatomite / sols clairs filtrants
    Si rien ne correspond, utilise "clay_quarry".

    Le JSON doit suivre EXACTEMENT ce schéma :
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
        "instructions": "Collect <minerai> & Band <cible>! Avoid <obstacle>!"
      }
    }

    Tous les textes UI sont en anglais. Écris du JSON valide uniquement
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
