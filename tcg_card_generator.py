"""
Générateur de cartes TCG (style Magic/Pokémon) - script Python autonome
- Utilise Pillow pour composer l'image de la carte
- Génère titre, image centrale, texte d'effet, statistiques, rareté
- Supporte batch generation à partir d'un fichier JSON

Install:
  pip install pillow reportlab

Fichiers attendus (exemples):
  - templates/carte_template.png   # template 750x1050 px (modifiable)
  - assets/illustration1.png
  - fonts/Beleren-Bold.ttf          # ou arial.ttf en fallback

Usage:
  python tcg_card_generator.py --input data/cards.json --out out/

Le script est livré comme base : vous pouvez adapter le template, les tailles, polices
et ajouter génération d'images via une API (Stable Diffusion, DALL·E, etc.).
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import textwrap
import json
import os
import random
import argparse
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.pagesizes import portrait

# ----------------------------- Configuration -----------------------------
TEMPLATE_PATH = "templates/carte_template.png"  # exemple
TEMPLATE_SIZE = (750, 1050)  # px (largeur, hauteur)
OUTPUT_DPI = 300
DEFAULT_FONT_PATHS = [
    "fonts/Beleren-Bold.ttf",
    "fonts/Beleren-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

# Zones (absolutes) à adapter selon votre template
ZONES = {
    "image": (75, 140, 600, 520),   # x, y, width, height
    "title": (60, 40),              # x, y
    "type_line": (60, 680),         # x, y
    "text_box": (60, 720, 630, 260),# x, y, w, h
    "stats": (520, 960),            # x, y
}

# ----------------------------- Utilitaires -----------------------------

def load_font(size=24):
    for p in DEFAULT_FONT_PATHS:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    # Wrap text to fit a given pixel width
    words = text.split()
    lines = []
    current = []
    for w in words:
        test = " ".join(current + [w])
        bbox = draw.textbbox((0, 0), test, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines


# ----------------------------- Effets graphiques -----------------------------
# ----------------------------- Générateur -----------------------------

def compose_card(data: dict, template_path=TEMPLATE_PATH, out_path=None):
    """Compose une carte à partir d'un dict data et sauvegarde en PNG.
    data attendu: {"name":..., "type":..., "text":..., "power":..., "toughness":..., "image":..., "rarity":...}
    """
    # Charger template (ou créer fond neutre si absent)
    if os.path.exists(template_path):
        card = Image.open(template_path).convert("RGBA")
    else:
        card = Image.new("RGBA", TEMPLATE_SIZE, (240, 240, 240, 255))

    draw = ImageDraw.Draw(card)

    # Image centrale
    if data.get("image") and os.path.exists(data["image"]):
        img = Image.open(data["image"]).convert("RGBA")
        ix, iy, iw, ih = ZONES["image"]
        img = ImageOps.fit(img, (iw, ih), Image.LANCZOS)
        card.paste(img, (ix, iy), img)
    else:
        # placeholder rectangle
        ix, iy, iw, ih = ZONES["image"]
        draw.rectangle([ix, iy, ix+iw, iy+ih], fill=(200,200,200))
        draw.text((ix+10, iy+10), "No image", font=load_font(24), fill=(80,80,80))

    # Titre
    title_font = load_font(48)
    tx, ty = ZONES["title"]
    draw.text((tx, ty), data.get("name", "Carte sans nom"), font=title_font, fill=(255,255,255))

    # Type / ligne type
    type_font = load_font(24)
    ttx, tty = ZONES["type_line"]
    draw.text((ttx, tty), data.get("type", "Type inconnu"), font=type_font, fill=(230,230,230))

    # Texte / règles
    tbx, tby, tbw, tbh = ZONES["text_box"]
    text_font = load_font(22)
    # wrap
    lines = wrap_text(data.get("text", ""), text_font, tbw-10, draw)
    bbox = draw.textbbox((0, 0), "A", font=text_font)
    line_height = bbox[3] - bbox[1]
    max_lines = tbh // (line_height+4)
    lines = lines[:max_lines]
    y = tby
    for line in lines:
        draw.text((tbx+5, y), line, font=text_font, fill=(10,10,10))
        y += line_height + 4

    # Stats (power/toughness) - optionnel
    if data.get("power") is not None or data.get("toughness") is not None:
        sx, sy = ZONES["stats"]
        stat_font = load_font(36)
        stats_text = f"{data.get('power','')}/{data.get('toughness','')}"
        draw.text((sx, sy), stats_text, font=stat_font, fill=(255,255,255))

    # Rareté -> appliquer un petit badge
    rarity = data.get("rarity", "common")
    badge_font = load_font(18)
    badge_text = rarity.capitalize()
    bx, by = (TEMPLATE_SIZE[0]-130, 20)
    draw.rectangle([bx, by, bx+110, by+40], fill=(30,30,30,200))
    draw.text((bx+10, by+6), badge_text, font=badge_font, fill=(255,215,0) if rarity in ("rare","ultra") else (255,255,255))

    # Flatten and save
    out_img = card.convert("RGB")
    if out_path is None:
        out_path = f"out/{data.get('name','carte')}.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    out_img.save(out_path, dpi=(OUTPUT_DPI, OUTPUT_DPI))
    return out_path


# ----------------------------- Batch + CLI -----------------------------

def batch_generate(json_path: str, out_dir: str):
    with open(json_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    results = []
    for i, card in enumerate(dataset):
        safe_name = card.get("name", f"carte_{i}").replace("/","_")
        out_path = os.path.join(out_dir, f"{safe_name}.png")
        p = compose_card(card, out_path=out_path)
        results.append(p)
    return results


def make_pdf(image_paths, pdf_path, page_size=(TEMPLATE_SIZE[0], TEMPLATE_SIZE[1])):
    # Convert pixels to points for reportlab (assuming 72 points per inch)
    w_px, h_px = page_size
    w_pt = w_px * 72.0 / OUTPUT_DPI
    h_pt = h_px * 72.0 / OUTPUT_DPI
    c = pdfcanvas.Canvas(pdf_path, pagesize=(w_pt, h_pt))
    for img in image_paths:
        c.drawImage(img, 0, 0, width=w_pt, height=h_pt)
        c.showPage()
    c.save()
    return pdf_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Générateur de cartes TCG en batch")
    parser.add_argument("--input", help="Fichier JSON contenant les cartes", required=False)
    parser.add_argument("--out", help="Dossier de sortie", default="out")
    args = parser.parse_args()

    # Exemple si aucun input fourni : on crée 4 cartes demo
    if not args.input:
        demo = [
            {"name":"Phénix d'Azur","type":"Créature — Phoenix","text":"Vol. À la fin du tour, renvoyez Phénix d'Azur dans la main de son propriétaire.","power":"4","toughness":"2","image":"assets/phoenix.png","rarity":"rare"},
            {"name":"Éclat de Mana","type":"Artefact","text":"T: Ajoutez {U}.","image":"assets/mana.png","rarity":"common"},
            {"name":"Gardien des Bois","type":"Créature — Elfe","text":"Quand Gardien des Bois arrive en jeu, cherchez une carte de forêt.","power":"2","toughness":"3","image":"assets/elf.png","rarity":"common"},
            {"name":"Seigneur Céleste","type":"Créature — Ange","text":"Lévitation, protection contre le rouge.","power":"5","toughness":"5","image":"assets/angel.png","rarity":"ultra"}
        ]
        os.makedirs(args.out, exist_ok=True)
        paths = []
        for c in demo:
            paths.append(compose_card(c, out_path=os.path.join(args.out, f"{c['name']}.png")))
        pdf_p = make_pdf(paths, os.path.join(args.out, "deck_demo.pdf"))
        print("Génération demo terminée. Fichiers:")
        for p in paths:
            print(" -", p)
        print("PDF:", pdf_p)
    else:
        os.makedirs(args.out, exist_ok=True)
        paths = batch_generate(args.input, args.out)
        # créer un PDF avec toutes les cartes
        pdf_path = os.path.join(args.out, "deck.pdf")
        make_pdf(paths, pdf_path)
        print(f"Génération terminée. {len(paths)} cartes -> {args.out}")
