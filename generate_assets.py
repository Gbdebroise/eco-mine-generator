#!/usr/bin/env python3
"""
generate_assets.py — Génère tous les fonds et écrans-titre avec Imagen.

Usage :
    python generate_assets.py                  # tous les biomes + sites
    python generate_assets.py --biome clay_quarry
    python generate_assets.py --site Clerac

Pré-requis :
    pip install google-genai pillow
    gcloud auth application-default login
"""

import argparse
import io
import os

import google.auth
from google import genai
from google.genai import types
from PIL import Image

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

client = genai.Client()
MODEL = "imagen-3.0-generate-002"
OUT_DIR = "public/assets"
os.makedirs(OUT_DIR, exist_ok=True)

BIOME_FAR = {
    "clay_quarry": (
        "Top-down view of an open-pit clay quarry road. "
        "Sandy beige and ochre ground with white clay patches, "
        "tire tracks, small rocks scattered around. "
        "Flat 2D game background, seamless tile, pixel art style, "
        "no sky, no horizon, pure top-down overhead view, muted earthy tones."
    ),
    "granite_underground": (
        "Top-down view of an underground mine tunnel floor. "
        "Dark grey granite rock, mining cart rail tracks running vertically, "
        "patches of wet stone, faint pickaxe marks. "
        "Flat 2D game background, seamless tile, pixel art style, "
        "no sky, dark charcoal palette with blue-grey highlights."
    ),
    "wetland": (
        "Top-down view of a rehabilitated quarry wetland. "
        "Lush green grass with patches of shallow water, "
        "small reeds and marsh plants, muddy banks, lily pads. "
        "Flat 2D game background, seamless tile, pixel art style, "
        "no sky, vivid greens and teal blues."
    ),
    "diatomite": (
        "Top-down view of a diatomite quarry floor. "
        "Pale white and light grey chalky ground, fine dust texture, "
        "shallow excavation marks, subtle mineral sparkle. "
        "Flat 2D game background, seamless tile, pixel art style, "
        "no sky, very light off-white palette."
    ),
}

BIOME_NEAR = {
    "clay_quarry": (
        "Scattered rocks and small boulders on transparent background, "
        "top-down view, clay quarry ground details, "
        "no background fill, PNG with alpha, pixel art style, "
        "sparse layout with lots of empty space, earthy tones."
    ),
    "granite_underground": (
        "Stalactite tips and small granite fragments on transparent background, "
        "top-down view, underground mine details, "
        "no background fill, PNG with alpha, pixel art style, "
        "sparse layout, dark grey tones."
    ),
    "wetland": (
        "Reed stems and small lily pads on transparent background, "
        "top-down view, wetland details, "
        "no background fill, PNG with alpha, pixel art style, "
        "sparse layout, green tones."
    ),
    "diatomite": (
        "Fine dust puffs and chalk fragments on transparent background, "
        "top-down view, diatomite quarry details, "
        "no background fill, PNG with alpha, pixel art style, "
        "sparse layout, very pale tones."
    ),
}

SITE_START = {
    "Clerac": (
        "Dramatic pixel art title screen for a mining video game set at Clerac, France. "
        "A bright yellow mining dumper truck in a white clay quarry at golden hour. "
        "Migratory birds flying in the background. Chestnut grove on the right side. "
        "Text space at the top for the title. "
        "Vibrant colors, retro arcade game aesthetic, portrait 480x640."
    ),
    "Beauvoir": (
        "Dramatic pixel art title screen for a mining video game set at Beauvoir, France. "
        "An underground lithium mine gallery lit by headlamps. "
        "Shiny grey granite walls, glinting lithium ore veins, "
        "a yellow dumper truck in silhouette. River visible in background. "
        "Text space at the top for the title. "
        "Dark moody atmosphere, retro arcade game aesthetic, portrait 480x640."
    ),
    "Provins": (
        "Dramatic pixel art title screen for a mining video game set at Provins, France. "
        "A rehabilitated quarry now a lush wetland. "
        "Ducks and herons on a blue lake, green meadows, a yellow dumper on a berm. "
        "Text space at the top for the title. "
        "Bright cheerful colors, retro arcade game aesthetic, portrait 480x640."
    ),
    "Foufouilloux": (
        "Dramatic pixel art title screen for a mining video game set at Foufouilloux, France. "
        "A diatomite quarry with bright white chalky cliffs. "
        "A yellow dumper truck on pale ground, clear blue sky. "
        "Text space at the top for the title. "
        "High contrast, sunny atmosphere, retro arcade game aesthetic, portrait 480x640."
    ),
}


def generate_image(prompt, size):
    response = client.models.generate_images(
        model=MODEL,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",
            output_mime_type="image/png",
        ),
    )
    img_bytes = response.generated_images[0].image.image_bytes
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    return img.resize(size, Image.LANCZOS)

def save(img, path):
    img.save(path)
    print(f"  ok  {path}")

def make_transparent(img, threshold=230):
    data = img.getdata()
    new = []
    for r, g, b, a in data:
        if r > threshold and g > threshold and b > threshold:
            new.append((r, g, b, 0))
        else:
            new.append((r, g, b, a))
    result = img.copy()
    result.putdata(new)
    return result

def generate_biome(biome):
    print(f"\n> Biome : {biome}")
    print("  Fond (far)...")
    save(generate_image(BIOME_FAR[biome], (480, 256)), f"{OUT_DIR}/{biome}_far.png")
    print("  1er plan (near)...")
    img_near = make_transparent(generate_image(BIOME_NEAR[biome], (480, 384)))
    save(img_near, f"{OUT_DIR}/{biome}_near.png")

def generate_site_start(site):
    print(f"\n> Ecran-titre : {site}")
    save(generate_image(SITE_START[site], (480, 640)), f"{OUT_DIR}/{site.lower()}_start_screen.png")
    print(f"  Copiez en start_screen.png pour l'activer.")

def main():
    parser = argparse.ArgumentParser(description="Genere les assets Eco-Mine Runner avec Imagen.")
    parser.add_argument("--biome", choices=list(BIOME_FAR.keys()))
    parser.add_argument("--site", choices=list(SITE_START.keys()))
    args = parser.parse_args()
    if args.biome:
        generate_biome(args.biome)
    elif args.site:
        generate_site_start(args.site)
    else:
        print("=== Eco-Mine Generator — generation des assets ===")
        for b in BIOME_FAR:
            generate_biome(b)
        for s in SITE_START:
            generate_site_start(s)
        print("\n=== Termine. Assets dans public/assets/ ===")

if __name__ == "__main__":
    main()
