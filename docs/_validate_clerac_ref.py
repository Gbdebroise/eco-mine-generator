"""Validation rapide du JSON de reference Clerac."""
import json
import sys

path = r"C:\Users\bertr\Documents\PROJETS\eco-mine-generator\docs\clerac_species_reference.json"

try:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
except json.JSONDecodeError as exc:
    print(f"[ERROR] JSON invalide: {exc}")
    sys.exit(1)
except FileNotFoundError:
    print(f"[ERROR] Fichier introuvable: {path}")
    sys.exit(1)

print("[OK] JSON valide et parseable")
print()

ev = data["especes_validees"]
totaux = {k: len(v) for k, v in ev.items()}
total_especes = sum(totaux.values())

print(f"Site: {data['site_context']['commune']} ({data['site_context']['code_postal']})")
print(f"Operateur: {data['site_context']['operateur']}")
print(f"Minerai: {data['site_context']['minerai_principal']}")
print()
print(f"Habitats valides:      {len(data['habitats_valides'])}")
print(f"Especes validees:      {total_especes}")
for taxon, n in totaux.items():
    print(f"  - {taxon:15s} {n}")
print(f"Especes incorrectes:   {len(data['especes_incorrectes'])}")
print(f"Regles de validation:  3 axes")
