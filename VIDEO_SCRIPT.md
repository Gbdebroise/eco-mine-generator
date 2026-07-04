# Eco-Mine Generator — script video 5 minutes

**Objectif :** montrer a l'ecran que (1) c'est un vrai systeme multi-agents ADK, (2) il utilise un serveur MCP, (3) pilote par CLI, (4) deploye en production — et placer le moment "wow" changement de site.

**Conseils d'enregistrement**
- Enregistrez en plan continu si possible.
- Narration cible : ~150 mots/minute. Les lignes ci-dessous tiennent en 5:00.
- Pre-lancez `npx` une fois avant d'enregistrer (le serveur MCP se met en cache).
- Deux onglets terminal + un navigateur prets avant de lancer.

---

## 0:00 - 0:30 — Accroche + probleme

**A l'ecran :** Titre "Eco-Mine Generator", puis scroll rapide d'un PDF RSE dense.

**Dire :**
"Mining companies run real biodiversity programs — bird-banding, quarry rehabilitation, underground mines that protect rivers. But all of it is buried in reports nobody reads. So I built an agent that turns a real mining site's environmental data into a playable awareness game. You give it one thing: a site name."

---

## 0:30 - 1:00 — Architecture

**A l'ecran :** Schema du pipeline (CLI -> ADK SequentialAgent -> researcher [MCP read] -> coder [MCP write] -> Phaser -> GitHub Pages).

**Dire :**
"It's a multi-agent pipeline on Google's ADK. A researcher agent reads the site data, a coder agent designs the level, and they talk to the filesystem through an MCP server. The game engine is fixed — the agent only generates the level config. That's what makes it reliable."

---

## 1:00 - 2:15 — Demo run 1 : Clerac

**A l'ecran :** Terminal, tapez lentement.

    adk run eco_mine_generator
    > Generate a game for Clerac

**Dire (pendant l'execution) :**
"I ask for Clerac. Watch the terminal: the researcher agent calls the MCP filesystem server to read the real CSR data — chamotte clay, bird-banding with France's natural history museum, protected chestnut groves for bats. It hands those facts to the coder agent, which writes the level config — again, through MCP."

**A l'ecran :** Navigateur, rafraichissez, jouez 10 secondes.

**Dire :**
"Here's the generated game: collect chamotte, band migratory birds, avoid blasting zones and protected groves. Every label and rule came from the real site data."

---

## 2:15 - 3:15 — Le moment wow : Beauvoir

**A l'ecran :** Terminal.

    > Generate a game for Beauvoir

**Dire :**
"Now the important part. I change nothing in the code. I just ask for a different site — Beauvoir, Imerys' lithium project in the Allier."

**A l'ecran :** Navigateur rafraichi — biome sombre granite, lithium, riviere Sioule.

**Dire :**
"Same engine, completely different game. Lithium ore instead of clay, an underground mine protecting the Sioule river. That's the generalization — one input, a brand-new game."

---

## 3:15 - 4:00 — Sous le capot (criteres, rapide)

**A l'ecran :** agent.py (SequentialAgent + McpToolset visibles), puis level_config.json.

**Dire :**
"Under the hood: a SequentialAgent orchestrates two specialized Gemini agents. File access is entirely through the official MCP filesystem server, with tool filtering. And the agent's whole job is this small JSON config — not hundreds of lines of fragile game code."

---

## 4:00 - 4:40 — Deploiement

**A l'ecran :** Terminal : bash deploy.sh — puis URL GitHub Pages dans le navigateur.

**Dire :**
"One command deploys it. The script pushes the generated game to GitHub Pages — live on the public web, playable on any device. From a site name to a deployed game in under a minute."

---

## 4:40 - 5:00 — Conclusion

**A l'ecran :** Les quatre sites (Clerac, Beauvoir, Provins, Foufouilloux), puis URL du repo.

**Dire :**
"Four real Imerys sites, grounded in public environmental data. An educational tool any communication team could run themselves — no code, just a site name. The code and writeup are linked below."

---

## Checklist avant enregistrement

- [ ] Terminal montre clairement les appels MCP (read puis write)
- [ ] Jeu Clerac joue a l'ecran
- [ ] Jeu Beauvoir visible et visuellement different
- [ ] agent.py : SequentialAgent + McpToolset a l'ecran
- [ ] deploy.sh s'execute et une URL live s'ouvre
- [ ] Duree totale <= 5:00
