# Incident MCP Tavily — Diagnostic et plan d'action

**Date :** 2026-07-06
**Sprint :** 4 (Reviewer, démo, writeup Kaggle)
**Statut :** Bloqué — décision de pivot à prendre sous 60 minutes de debug maximum
**Contexte :** VPN Imerys actif en permanence sur la PC de test (WSL), non désactivable

---

## Résumé exécutif

Le MCP Tavily ne parvient jamais à créer une session dans le pipeline ADK. Les logs
côté ADK montrent `Failed to create MCP session` en boucle et `ValueError: Tool
'tavily_search' not found` — le serveur MCP Tavily ne fournit aucun tool à l'agent
parce qu'il crashe au démarrage.

L'hypothèse principale est l'inspection TLS du VPN Imerys qui casse la chaîne de
certificats vue par Node.js (le runtime du serveur MCP Tavily). La clé Tavily
elle-même est valide (compte payant vérifié).

**Décision à prendre :** débugger l'intégration Tavily via VPN (max 60 min), sinon
pivoter sur une alternative MCP compatible avec les contraintes réseau.

---

## Ce que disent les logs (analyse précise)

### Symptôme côté ADK
- `Failed to create MCP session: unhandled errors in a TaskGroup` répété en boucle
- Retries automatiques via `mcp_session_manager.py:207` — tous échouent
- `ValueError: Tool 'tavily_search' not found. Available tools: read_file,
  read_text_file, list_directory`

### Interprétation
- Le MCP Filesystem démarre correctement (`read_file`, `list_directory` visibles)
- Le MCP Tavily ne démarre **jamais** — pas "marche une fois puis échoue", jamais
- L'agent LLM tente d'appeler `tavily_search` parce que son prompt le demande, mais
  le tool n'est pas dans le toolset actif
- Le vrai message d'erreur du subprocess MCP Tavily n'apparaît pas dans les logs ADK
  visibles — il est en stderr du subprocess, non capturé

---

## Contexte réseau : VPN Imerys toujours actif

- Activation au démarrage de la machine, pas désactivable côté utilisateur
- Contrainte fixe pour tout le Sprint 4 et le tournage de la vidéo
- Les VPN d'entreprise industrielle font généralement de l'inspection TLS
  (déchiffrement + rechiffrement avec CA d'entreprise)
- L'erreur `self signed certificate` observée lors des tests curl initiaux est
  cohérente avec cette hypothèse

---

## Trois hypothèses techniques, par ordre de probabilité

### H1 — Inspection TLS d'entreprise (probable)

Le VPN Imerys intercepte le HTTPS sortant vers `api.tavily.com`, le déchiffre, et
le rechiffre avec un CA racine Imerys. Node.js (runtime du MCP Tavily) refuse
cette chaîne parce que le CA Imerys n'est pas dans son trust store embarqué. Le
serveur MCP crashe silencieusement au démarrage, avant même d'exposer ses tools.

**Test qui tranche :**
```powershell
openssl s_client -connect api.tavily.com:443 -showcerts 2>&1 | Select-String "issuer|CN"
```
Si l'issuer contient "Imerys", "Zscaler", "Netskope", "Bluecoat", "Palo Alto" ou
un nom de solution proxy → SSL inspection confirmée.

**Solution si confirmée :**
1. Localiser le CA Imerys installé sur Windows :
   ```powershell
   Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object {$_.Subject -like "*Imerys*"}
   ```
2. Exporter le CA au format .pem
3. Configurer Node pour l'accepter :
   ```powershell
   $env:NODE_EXTRA_CA_CERTS="C:\chemin\vers\imerys-root-ca.pem"
   ```
4. Relancer `agents-cli playground` dans le même shell

### H2 — Domaine `api.tavily.com` bloqué par catégorisation VPN

Certains VPN d'entreprise ont des listes de domaines autorisés par catégorie.
Tavily peut être classé "AI/uncategorized" et bloqué net.

**Test qui tranche :**
```powershell
Test-NetConnection -ComputerName api.tavily.com -Port 443
```
Si `TcpTestSucceeded: False` → domaine bloqué au niveau réseau.

**Solutions possibles :**
- Demander à l'IT Imerys de whitelist `api.tavily.com` (délai administratif long,
  pas viable pour la deadline Kaggle)
- Pivoter sur un MCP utilisant un domaine autorisé

### H3 — Blocage sur WebSockets ou stdio outbound

Moins probable pour un MCP stdio qui reste local, mais possible si le MCP Tavily
utilise des WebSockets sous le capot. Se manifesterait par des timeouts au bout
de X secondes plutôt que des crashes immédiats.

---

## Plan d'action timeboxé — 60 minutes maximum

Après ce quota, pivot immédiat. Pas 90 minutes, pas 3 heures. La deadline Kaggle
compte plus que Tavily spécifiquement.

### Phase 1 — Diagnostic (15 min)

Exécuter dans l'ordre et noter les résultats :

```powershell
# Test 1 : Tavily est-il joignable au niveau TCP ?
Test-NetConnection -ComputerName api.tavily.com -Port 443

# Test 2 : INPN (alternative pertinente au sujet) passe-t-il ?
Test-NetConnection -ComputerName inpn.mnhn.fr -Port 443

# Test 3 : Y a-t-il un CA Imerys installé (indice de SSL inspection) ?
Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object {$_.Subject -like "*Imerys*"}

# Test 4 : Quel CA voit-on effectivement sur la connexion Tavily ?
openssl s_client -connect api.tavily.com:443 -showcerts 2>&1 | Select-String "issuer|CN"
```

Matrice de décision selon les résultats :

| Tavily TCP | CA Imerys visible | Diagnostic          | Action                        |
|------------|-------------------|---------------------|-------------------------------|
| OK         | Oui               | SSL inspection      | Phase 2 (fix CA)              |
| OK         | Non               | Autre problème local| Phase 2 (isoler MCP)          |
| Bloqué     | -                 | Domaine filtré      | Pivot immédiat (Phase 3)      |

### Phase 2 — Résolution (30 min si SSL inspection)

1. Exporter le CA Imerys en `.pem`
2. `$env:NODE_EXTRA_CA_CERTS="chemin\imerys-ca.pem"`
3. Relancer MCP Inspector en isolation :
   ```powershell
   npx @modelcontextprotocol/inspector npx -y tavily-mcp
   ```
4. Vérifier que `tools/list` retourne bien `tavily_search`
5. Si OK → relancer le pipeline ADK complet
6. Vérifier que les MCP calls Tavily apparaissent dans le playground debug view

### Phase 3 — Pivot si échec (15 min de bascule)

Voir section suivante.

---

## Plan B — Pivot vers alternative MCP

Deux options selon les résultats des tests réseau.

### Option A (recommandée) — Filesystem MCP + dataset Clérac local

**Principe :** Constituer un dataset de référence des espèces Clérac en JSON local,
consulté par le Reviewer via le Filesystem MCP (déjà fonctionnel, passe le VPN).

**Avantages :**
- Zéro dépendance réseau, zéro fragilité en démo
- Filesystem MCP déjà en place, aucun changement d'architecture
- Angle jury solide : "dataset curé à partir des sources officielles INPN"
- Plus scientifiquement rigoureux qu'un appel Tavily aléatoire

**Inconvénient :** Un MCP externe visible en moins pour le compteur du jury.

**Implémentation (30 min) :**
1. Constituer `docs/clerac_species_reference.json` avec :
   - Liste des espèces validées (rollier d'Europe, guêpier, engoulevent, crapaud
     calamite, lézard ocellé, orchidées)
   - Statut de protection (source INPN)
   - Habitat associé au type de milieu (kaolinière, mare temporaire, lande)
2. Modifier le Reviewer pour utiliser `read_file` sur ce JSON
3. Le prompt Reviewer inclut la référence : "compare les espèces mentionnées dans
   le config avec `docs/clerac_species_reference.json`"

**À faire hors VPN si possible :** compiler le dataset depuis inpn.mnhn.fr en une
seule session, puis le committer dans le repo (transféré via git bundle habituel).

### Option B — Fetch MCP officiel Anthropic + INPN

**Principe :** Remplacer Tavily par le MCP Fetch officiel qui fait des GET HTTP
simples vers `inpn.mnhn.fr`.

**Conditions :** INPN doit passer le VPN (Test 2 de la Phase 1).

**Avantages :**
- MCP externe conservé (compteur jury intact)
- Source de données ultra-pertinente au sujet biodiversité française
- MCP officiel Anthropic = très stable

**Inconvénients :**
- Dépend de la disponibilité INPN via VPN
- Moins de flexibilité qu'un moteur de recherche

### Option C (déconseillée dans le contexte) — Brave Search MCP

Alternative directe à Tavily. Utile uniquement si aucune des deux options
ci-dessus n'est possible. Même risque de blocage VPN que Tavily.

---

## Ce qu'il ne faut PAS faire

- **Ne pas écrire de MCP custom INPN maintenant.** Bonne idée dans un monde
  détendu, mauvaise idée en gestion de crise Sprint 4.
- **Ne pas s'acharner au-delà de 60 minutes sur Tavily.** La deadline gagne.
- **Ne pas désactiver la vérification TLS avec `NODE_TLS_REJECT_UNAUTHORIZED=0`
  en production.** Uniquement pour un test ponctuel de diagnostic, jamais dans la
  démo ou le writeup — signal d'alerte pour tout jury sécurité.
- **Ne pas tourner la vidéo tant que le pipeline n'est pas stable trois fois
  d'affilée.** Un crash MCP en démo coûte la note narrative.

---

## Impact sur le writeup Kaggle

Le writeup mentionne actuellement (Sprint 4 étape 1) l'utilisation de Tavily MCP
dans le Reviewer. À adapter selon l'issue :

- **Si Tavily fonctionne (Phase 2 réussie) :** aucun changement, mentionner
  éventuellement la robustesse à l'inspection TLS d'entreprise comme point
  d'ingénierie
- **Si pivot Option A :** reformuler autour du "dataset Clérac curé + Filesystem
  MCP", angle "rigueur scientifique et reproductibilité"
- **Si pivot Option B :** mentionner INPN et le choix d'une source officielle
  française pertinente au sujet

Dans tous les cas, ne pas cacher le problème rencontré dans la section "Limites
et apprentissages" — le jury Kaggle valorise l'honnêteté sur les contraintes
réelles.

---

## Suivi

- [ ] Phase 1 exécutée, résultats notés
- [ ] Décision prise : fix Tavily / pivot Option A / pivot Option B
- [ ] Pipeline stable trois fois consécutives sans crash MCP
- [ ] Mise à jour du prompt Reviewer selon la décision
- [ ] Ajout entrée `docs/DECISIONS.md` (ADR-lite) documentant le choix final
- [ ] Mise à jour `CLAUDE.md` / `GEMINI.md` avec la config MCP finale
- [ ] Section writeup Kaggle ajustée
