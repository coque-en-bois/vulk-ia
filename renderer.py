"""
Module de rendu pour générer les fichiers SVG et PNG.
"""

from pathlib import Path
from typing import Optional
import svgwrite
from svgwrite import Drawing
from svgwrite.container import Group

from composer import ComposedMedal


# Couleurs pour le rendu
COLORS = {
    "cut_line": "#FF0000",
    "engrave_line": "#0000FF",
}

WOOD_COLORS = {
    "hetre": ("#D4A574", "#4A3728"),
    "chene": ("#C19A6B", "#3D2914"),
    "noyer": ("#5C4033", "#2C1810"),
    "erable": ("#E8DCC4", "#5A4A3A"),
    "bouleau": ("#F5DEB3", "#6B4423"),
}


def create_svg_medal(
    medal: ComposedMedal,
    wood_type: str = "hetre",
    margin: float = 10.0,
    show_cut_lines: bool = False
) -> Drawing:
    """Crée un fichier SVG de la médaille."""
    bounds = medal.bounds
    width = bounds[2] - bounds[0] + 2 * margin
    height = bounds[3] - bounds[1] + 2 * margin
    
    dwg = svgwrite.Drawing(
        size=(f"{width}mm", f"{height}mm"),
        viewBox=f"{bounds[0] - margin} {-(bounds[3] + margin)} {width} {height}"
    )
    
    wood_bg, engrave_color = WOOD_COLORS.get(wood_type, WOOD_COLORS["hetre"])
    
    main_group = dwg.g(transform="scale(1, -1)")
    
    # Fond de la médaille
    outline_coords = list(medal.outline.exterior.coords)
    medal_shape = dwg.polygon(
        points=outline_coords,
        fill=wood_bg,
        stroke=engrave_color if not show_cut_lines else COLORS["cut_line"],
        stroke_width=0.5
    )
    main_group.add(medal_shape)
    
    # Trou pour ruban
    if medal.ribbon_hole_center:
        hole = dwg.circle(
            center=(medal.ribbon_hole_center.x, medal.ribbon_hole_center.y),
            r=medal.ribbon_hole_radius,
            fill="white",
            stroke=engrave_color if not show_cut_lines else COLORS["cut_line"],
            stroke_width=0.3
        )
        main_group.add(hole)
    
    # Motifs (gravure)
    motifs_group = dwg.g(
        stroke=engrave_color,
        stroke_width=0.4,
        fill="none",
        stroke_linecap="round",
        stroke_linejoin="round"
    )
    
    for line in medal.motif_lines:
        if len(line) >= 2:
            points = [(x, y) for x, y in line]
            polyline = dwg.polyline(points)
            motifs_group.add(polyline)
    
    main_group.add(motifs_group)
    dwg.add(main_group)
    
    # Textes
    texts_group = dwg.g()
    
    for text_data in medal.texts:
        x = text_data["x"]
        y = -(text_data["y"])
        
        font_size = text_data["font_size"]
        font_weight = "bold" if text_data.get("bold", False) else "normal"
        
        if text_data.get("curved", False):
            _add_curved_text(dwg, texts_group, text_data, engrave_color)
        else:
            text_elem = dwg.text(
                text_data["content"],
                insert=(x, y),
                text_anchor=text_data.get("anchor", "middle"),
                font_size=f"{font_size}mm",
                font_family=text_data.get("font_family", "Arial"),
                font_weight=font_weight,
                fill=engrave_color
            )
            texts_group.add(text_elem)
    
    dwg.add(texts_group)
    
    return dwg


def _add_curved_text(
    dwg: Drawing,
    group: Group,
    text_data: dict,
    color: str
):
    """Ajoute un texte courbé au SVG."""
    content = text_data["content"]
    cx = text_data["x"]
    cy = -text_data["y"]
    radius = text_data.get("curve_radius", 30)
    start_angle = text_data.get("start_angle", 180)
    font_size = text_data["font_size"]
    
    path_id = f"textpath_{id(text_data)}"
    
    if start_angle == 180:
        path_d = f"M {cx - radius},{cy} A {radius},{radius} 0 0,1 {cx + radius},{cy}"
    else:
        path_d = f"M {cx + radius},{cy} A {radius},{radius} 0 0,1 {cx - radius},{cy}"
    
    path = dwg.path(d=path_d, id=path_id, fill="none", stroke="none")
    dwg.defs.add(path)
    
    text = dwg.text(
        "",
        font_size=f"{font_size}mm",
        font_family=text_data.get("font_family", "Arial"),
        font_weight="bold" if text_data.get("bold") else "normal",
        fill=color
    )
    
    text_path = dwg.textPath(
        dwg.defs.elements[-1],
        content,
        startOffset="50%"
    )
    text_path["text-anchor"] = "middle"
    text.add(text_path)
    
    group.add(text)


def render_medal_svg(
    medal: ComposedMedal,
    output_path: str,
    wood_type: str = "hetre",
    show_cut_lines: bool = False
) -> Path:
    """Génère et sauvegarde le SVG de la médaille."""
    dwg = create_svg_medal(medal, wood_type, show_cut_lines=show_cut_lines)
    
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    dwg.saveas(str(output), pretty=True)
    
    return output


def render_medal_png(
    medal: ComposedMedal,
    output_path: str,
    wood_type: str = "hetre",
    scale: float = 5.0
) -> Optional[Path]:
    """Génère un PNG de la médaille (pour prévisualisation)."""
    try:
        import cairosvg
    except (ImportError, OSError):
        print("⚠️  cairosvg non disponible - PNG non généré (installer cairo: brew install cairo)")
        return None
    
    svg_path = output_path.replace(".png", "_temp.svg")
    dwg = create_svg_medal(medal, wood_type)
    dwg.saveas(svg_path, pretty=True)
    
    bounds = medal.bounds
    width_mm = bounds[2] - bounds[0] + 20
    height_mm = bounds[3] - bounds[1] + 20
    
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    cairosvg.svg2png(
        url=svg_path,
        write_to=str(output),
        output_width=int(width_mm * scale),
        output_height=int(height_mm * scale)
    )
    
    Path(svg_path).unlink()
    
    return output


def render_production_svg(
    medal: ComposedMedal,
    output_path: str
) -> Path:
    """Génère un SVG optimisé pour la production (Trotec)."""
    bounds = medal.bounds
    margin = 5.0
    width = bounds[2] - bounds[0] + 2 * margin
    height = bounds[3] - bounds[1] + 2 * margin
    
    dwg = svgwrite.Drawing(
        size=(f"{width}mm", f"{height}mm"),
        viewBox=f"{bounds[0] - margin} {-(bounds[3] + margin)} {width} {height}"
    )
    
    main_group = dwg.g(transform="scale(1, -1)")
    
    # Lignes de découpe
    cut_group = dwg.g(
        stroke=COLORS["cut_line"],
        stroke_width=0.1,
        fill="none"
    )
    
    outline_coords = list(medal.outline.exterior.coords)
    cut_group.add(dwg.polygon(points=outline_coords))
    
    if medal.ribbon_hole_center:
        cut_group.add(dwg.circle(
            center=(medal.ribbon_hole_center.x, medal.ribbon_hole_center.y),
            r=medal.ribbon_hole_radius
        ))
    
    main_group.add(cut_group)
    
    # Lignes de gravure
    engrave_group = dwg.g(
        stroke=COLORS["engrave_line"],
        stroke_width=0.1,
        fill="none"
    )
    
    for line in medal.motif_lines:
        if len(line) >= 2:
            engrave_group.add(dwg.polyline(points=line))
    
    main_group.add(engrave_group)
    dwg.add(main_group)
    
    # Textes en bleu
    for text_data in medal.texts:
        x = text_data["x"]
        y = -(text_data["y"])
        
        if not text_data.get("curved", False):
            text_elem = dwg.text(
                text_data["content"],
                insert=(x, y),
                text_anchor=text_data.get("anchor", "middle"),
                font_size=f"{text_data['font_size']}mm",
                font_family=text_data.get("font_family", "Arial"),
                font_weight="bold" if text_data.get("bold") else "normal",
                fill=COLORS["engrave_line"]
            )
            dwg.add(text_elem)
    
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    dwg.saveas(str(output), pretty=True)
    
    return output


if __name__ == "__main__":
    from composer import create_trail_medal, compose_medal
    
    print("=== Test du rendu ===\n")
    
    composition = create_trail_medal(
        event_name="Test Trail",
        year="2026",
        distance="50K",
        diameter=75
    )
    
    medal = compose_medal(composition)
    
    svg_path = render_medal_svg(medal, "output/test_medal.svg", wood_type="hetre")
    print(f"✅ SVG créé: {svg_path}")
    
    prod_path = render_production_svg(medal, "output/test_medal_production.svg")
    print(f"✅ SVG production créé: {prod_path}")
    
    png_path = render_medal_png(medal, "output/test_medal.png", wood_type="hetre")
    if png_path:
        print(f"✅ PNG créé: {png_path}")
