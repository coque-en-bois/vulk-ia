"""
Module de composition pour assembler forme, motifs et texte.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
from shapely.geometry import Polygon, Point

from shapes import MedalShape, ShapeParams, get_shape, calculate_ribbon_hole_position
from motifs import MotifType, MotifParams, get_motif
from constraints import (
    TrotecConstraints, 
    DEFAULT_CONSTRAINTS,
    validate_medal_shape,
    validate_ribbon_hole,
    validate_engraving_text,
    ValidationResult
)


class TextPosition(Enum):
    """Positions prédéfinies pour le texte."""
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"
    AROUND_TOP = "around_top"
    AROUND_BOTTOM = "around_bottom"


@dataclass
class TextElement:
    """Élément texte à graver."""
    content: str
    position: TextPosition = TextPosition.CENTER
    font_size: float = 8.0
    font_family: str = "Arial"
    bold: bool = False
    offset_y: float = 0.0
    curved: bool = False
    curve_radius: Optional[float] = None


@dataclass
class MotifElement:
    """Élément motif décoratif."""
    motif_type: MotifType
    params: MotifParams = field(default_factory=MotifParams)
    position: Tuple[float, float] = (0, 0)


@dataclass
class MedalComposition:
    """Composition complète d'une médaille."""
    shape_type: MedalShape = MedalShape.CIRCLE
    shape_params: ShapeParams = field(default_factory=ShapeParams)
    ribbon_hole: bool = True
    ribbon_hole_diameter: float = 4.0
    ribbon_hole_position: Optional[Tuple[float, float]] = None
    motifs: List[MotifElement] = field(default_factory=list)
    texts: List[TextElement] = field(default_factory=list)
    name: str = "Medal"
    event_type: str = ""
    shape_polygon: Optional[Polygon] = None
    validation_result: Optional[ValidationResult] = None


@dataclass
class ComposedMedal:
    """Médaille composée prête pour le rendu."""
    outline: Polygon
    ribbon_hole_center: Optional[Point]
    ribbon_hole_radius: float
    motif_lines: List[List[Tuple[float, float]]]
    texts: List[Dict[str, Any]]
    name: str
    bounds: Tuple[float, float, float, float]
    is_valid: bool
    validation_result: ValidationResult


def compose_medal(
    composition: MedalComposition,
    constraints: TrotecConstraints = DEFAULT_CONSTRAINTS
) -> ComposedMedal:
    """Compose une médaille complète à partir d'une composition."""
    
    # 1. Générer la forme de base
    outline = get_shape(composition.shape_type, composition.shape_params)
    bounds = outline.bounds
    
    # 2. Valider la forme
    shape_validation = validate_medal_shape(outline, constraints)
    all_errors = list(shape_validation.errors)
    all_warnings = list(shape_validation.warnings)
    
    # 3. Calculer position du trou ruban
    ribbon_hole_center = None
    ribbon_hole_radius = composition.ribbon_hole_diameter / 2
    
    if composition.ribbon_hole:
        if composition.ribbon_hole_position:
            hole_pos = composition.ribbon_hole_position
        else:
            hole_pos = calculate_ribbon_hole_position(outline, margin=8.0)
        
        ribbon_hole_center = Point(hole_pos[0], hole_pos[1])
        
        hole_validation = validate_ribbon_hole(outline, ribbon_hole_center, constraints)
        all_errors.extend(hole_validation.errors)
        all_warnings.extend(hole_validation.warnings)
    
    # 4. Générer les motifs
    all_motif_lines = []
    for motif_elem in composition.motifs:
        lines = get_motif(motif_elem.motif_type, motif_elem.params)
        ox, oy = motif_elem.position
        positioned_lines = [
            [(x + ox, y + oy) for x, y in line]
            for line in lines
        ]
        all_motif_lines.extend(positioned_lines)
    
    # 5. Positionner les textes
    positioned_texts = []
    center_x = (bounds[0] + bounds[2]) / 2
    center_y = (bounds[1] + bounds[3]) / 2
    medal_width = bounds[2] - bounds[0]
    
    for text_elem in composition.texts:
        text_dict = {
            "content": text_elem.content,
            "font_size": text_elem.font_size,
            "font_family": text_elem.font_family,
            "bold": text_elem.bold,
            "curved": text_elem.curved,
        }
        
        if text_elem.position == TextPosition.TOP:
            text_dict["x"] = center_x
            text_dict["y"] = bounds[3] - 15 + text_elem.offset_y
            text_dict["anchor"] = "middle"
            
        elif text_elem.position == TextPosition.CENTER:
            text_dict["x"] = center_x
            text_dict["y"] = center_y + text_elem.offset_y
            text_dict["anchor"] = "middle"
            
        elif text_elem.position == TextPosition.BOTTOM:
            text_dict["x"] = center_x
            text_dict["y"] = bounds[1] + 10 + text_elem.offset_y
            text_dict["anchor"] = "middle"
            
        elif text_elem.position == TextPosition.AROUND_TOP:
            text_dict["curved"] = True
            text_dict["curve_radius"] = text_elem.curve_radius or (medal_width / 2 - 8)
            text_dict["x"] = center_x
            text_dict["y"] = center_y
            text_dict["start_angle"] = 180
            text_dict["anchor"] = "middle"
            
        elif text_elem.position == TextPosition.AROUND_BOTTOM:
            text_dict["curved"] = True
            text_dict["curve_radius"] = text_elem.curve_radius or (medal_width / 2 - 8)
            text_dict["x"] = center_x
            text_dict["y"] = center_y
            text_dict["start_angle"] = 0
            text_dict["anchor"] = "middle"
        
        text_validation = validate_engraving_text(text_elem.font_size, constraints)
        all_errors.extend(text_validation.errors)
        all_warnings.extend(text_validation.warnings)
        
        positioned_texts.append(text_dict)
    
    is_valid = len(all_errors) == 0
    final_validation = ValidationResult(is_valid, all_errors, all_warnings)
    
    return ComposedMedal(
        outline=outline,
        ribbon_hole_center=ribbon_hole_center,
        ribbon_hole_radius=ribbon_hole_radius,
        motif_lines=all_motif_lines,
        texts=positioned_texts,
        name=composition.name,
        bounds=bounds,
        is_valid=is_valid,
        validation_result=final_validation
    )


def create_trail_medal(
    event_name: str = "Trail des Montagnes",
    year: str = "2026",
    distance: str = "42K",
    diameter: float = 70.0
) -> MedalComposition:
    """Crée une composition prédéfinie pour un trail."""
    return MedalComposition(
        name=f"{event_name} {year}",
        shape_type=MedalShape.CIRCLE,
        shape_params=ShapeParams(width=diameter),
        ribbon_hole=True,
        motifs=[
            MotifElement(
                motif_type=MotifType.MOUNTAINS,
                params=MotifParams(width=diameter * 0.7, height=diameter * 0.3),
                position=(0, -5)
            ),
            MotifElement(
                motif_type=MotifType.TREES,
                params=MotifParams(width=diameter * 0.5, height=diameter * 0.2),
                position=(0, -diameter * 0.25)
            )
        ],
        texts=[
            TextElement(
                content=event_name.upper(),
                position=TextPosition.AROUND_TOP,
                font_size=5.0,
                bold=True
            ),
            TextElement(
                content=distance,
                position=TextPosition.CENTER,
                font_size=14.0,
                bold=True,
                offset_y=5
            ),
            TextElement(
                content=year,
                position=TextPosition.AROUND_BOTTOM,
                font_size=5.0
            )
        ],
        event_type="trail"
    )


def create_running_medal(
    event_name: str = "Marathon de Paris",
    year: str = "2026",
    diameter: float = 70.0
) -> MedalComposition:
    """Crée une composition prédéfinie pour une course sur route."""
    return MedalComposition(
        name=f"{event_name} {year}",
        shape_type=MedalShape.HEXAGON,
        shape_params=ShapeParams(width=diameter),
        ribbon_hole=True,
        motifs=[
            MotifElement(
                motif_type=MotifType.RUNNING_TRACK,
                params=MotifParams(width=diameter * 0.6),
                position=(0, -10)
            ),
            MotifElement(
                motif_type=MotifType.CHEVRONS,
                params=MotifParams(width=diameter * 0.4, height=12),
                position=(0, 5)
            )
        ],
        texts=[
            TextElement(
                content=event_name.upper(),
                position=TextPosition.TOP,
                font_size=5.0,
                bold=True,
                offset_y=-5
            ),
            TextElement(
                content="FINISHER",
                position=TextPosition.CENTER,
                font_size=8.0,
                bold=True
            ),
            TextElement(
                content=year,
                position=TextPosition.BOTTOM,
                font_size=6.0,
                offset_y=5
            )
        ],
        event_type="running"
    )


def create_swimming_medal(
    event_name: str = "Traversée du Lac",
    year: str = "2026",
    diameter: float = 65.0
) -> MedalComposition:
    """Crée une composition prédéfinie pour la natation."""
    return MedalComposition(
        name=f"{event_name} {year}",
        shape_type=MedalShape.DROP,
        shape_params=ShapeParams(width=diameter * 0.8, height=diameter),
        ribbon_hole=True,
        motifs=[
            MotifElement(
                motif_type=MotifType.WAVES,
                params=MotifParams(width=diameter * 0.6, height=15),
                position=(0, -15)
            )
        ],
        texts=[
            TextElement(
                content=event_name.upper(),
                position=TextPosition.TOP,
                font_size=4.5,
                bold=True,
                offset_y=-10
            ),
            TextElement(
                content=year,
                position=TextPosition.BOTTOM,
                font_size=6.0,
                offset_y=10
            )
        ],
        event_type="swimming"
    )


def create_corporate_medal(
    company_name: str = "OOOVATION",
    event_name: str = "Team Building",
    year: str = "2026",
    diameter: float = 70.0
) -> MedalComposition:
    """Crée une composition pour un événement d'entreprise."""
    return MedalComposition(
        name=f"{company_name} - {event_name} {year}",
        shape_type=MedalShape.SHIELD,
        shape_params=ShapeParams(width=diameter * 0.85, height=diameter),
        ribbon_hole=True,
        motifs=[
            MotifElement(
                motif_type=MotifType.LAUREL,
                params=MotifParams(width=diameter * 0.7, height=diameter * 0.5),
                position=(0, -5)
            )
        ],
        texts=[
            TextElement(
                content=company_name,
                position=TextPosition.TOP,
                font_size=6.0,
                bold=True,
                offset_y=-8
            ),
            TextElement(
                content=event_name.upper(),
                position=TextPosition.CENTER,
                font_size=5.0,
                offset_y=5
            ),
            TextElement(
                content=year,
                position=TextPosition.BOTTOM,
                font_size=5.0,
                offset_y=8
            )
        ],
        event_type="corporate"
    )


def create_custom_medal(
    shape: MedalShape = MedalShape.CIRCLE,
    primary_motif: MotifType = MotifType.MOUNTAINS,
    secondary_motif: Optional[MotifType] = None,
    text_main: str = "ÉVÉNEMENT",
    text_secondary: str = "FINISHER",
    text_year: str = "2026",
    diameter: float = 70.0,
    concept_name: str = "Custom Medal",
    wood_type: str = "hetre"
) -> MedalComposition:
    """
    Crée une composition personnalisée (utilisée par l'IA).
    
    Args:
        shape: Forme de la médaille
        primary_motif: Motif principal
        secondary_motif: Motif secondaire optionnel
        text_main: Texte principal
        text_secondary: Texte secondaire
        text_year: Année
        diameter: Diamètre en mm
        concept_name: Nom du concept
        wood_type: Type de bois
        
    Returns:
        MedalComposition configurée
    """
    # Déterminer les dimensions selon la forme
    if shape in [MedalShape.SHIELD, MedalShape.DROP, MedalShape.LEAF]:
        shape_params = ShapeParams(width=diameter * 0.85, height=diameter)
    else:
        shape_params = ShapeParams(width=diameter)
    
    # Construire les motifs
    motifs = [
        MotifElement(
            motif_type=primary_motif,
            params=MotifParams(width=diameter * 0.6, height=diameter * 0.25),
            position=(0, -5)
        )
    ]
    
    if secondary_motif:
        motifs.append(
            MotifElement(
                motif_type=secondary_motif,
                params=MotifParams(width=diameter * 0.4, height=diameter * 0.15),
                position=(0, -diameter * 0.22)
            )
        )
    
    # Construire les textes selon la forme
    if shape == MedalShape.CIRCLE:
        texts = [
            TextElement(
                content=text_main,
                position=TextPosition.AROUND_TOP,
                font_size=5.0,
                bold=True
            ),
            TextElement(
                content=text_secondary,
                position=TextPosition.CENTER,
                font_size=8.0,
                bold=True,
                offset_y=8
            ),
            TextElement(
                content=text_year,
                position=TextPosition.AROUND_BOTTOM,
                font_size=5.0
            )
        ]
    else:
        texts = [
            TextElement(
                content=text_main,
                position=TextPosition.TOP,
                font_size=5.0,
                bold=True,
                offset_y=-5
            ),
            TextElement(
                content=text_secondary,
                position=TextPosition.CENTER,
                font_size=7.0,
                bold=True
            ),
            TextElement(
                content=text_year,
                position=TextPosition.BOTTOM,
                font_size=5.0,
                offset_y=5
            )
        ]
    
    return MedalComposition(
        name=concept_name,
        shape_type=shape,
        shape_params=shape_params,
        ribbon_hole=True,
        motifs=motifs,
        texts=texts,
        event_type="custom"
    )


if __name__ == "__main__":
    print("=== Test de composition de médailles ===\n")
    
    trail_composition = create_trail_medal(
        event_name="Ultra Trail du Mont Blanc",
        year="2026",
        distance="170K",
        diameter=80
    )
    
    composed = compose_medal(trail_composition)
    
    print(f"Médaille: {composed.name}")
    print(f"Forme: {trail_composition.shape_type.value}")
    print(f"Dimensions: {composed.bounds[2]-composed.bounds[0]:.1f} x {composed.bounds[3]-composed.bounds[1]:.1f} mm")
    print(f"Trou ruban: {composed.ribbon_hole_center is not None}")
    print(f"Nombre de motifs: {len(composed.motif_lines)} lignes")
    print(f"Nombre de textes: {len(composed.texts)}")
    print()
    print("Validation:")
    print(composed.validation_result)
