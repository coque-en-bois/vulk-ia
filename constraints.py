"""
Contraintes de fabrication pour découpe laser Trotec.
Ces règles garantissent que les designs générés sont produisibles.
"""

from dataclasses import dataclass
from typing import Tuple, List
from shapely.geometry import Polygon, Point
from shapely.validation import explain_validity


@dataclass
class TrotecConstraints:
    """Contraintes machine Trotec pour découpe/gravure laser."""
    
    # Dimensions zone de travail (mm)
    max_width: float = 600.0
    max_height: float = 300.0
    
    # Épaisseurs bois supportées (mm)
    wood_thicknesses: Tuple[float, ...] = (3.0, 4.0, 5.0, 6.0)
    
    # Contraintes de découpe
    min_line_width: float = 0.5          # Épaisseur trait minimum (mm)
    min_detail_size: float = 1.0         # Plus petit détail gravable (mm)
    min_bridge_width: float = 2.0        # Pont minimum entre découpes (mm)
    kerf: float = 0.15                   # Perte matière découpe (mm)
    
    # Contraintes médaille
    min_medal_diameter: float = 40.0     # Diamètre minimum médaille (mm)
    max_medal_diameter: float = 120.0    # Diamètre maximum médaille (mm)
    safe_margin: float = 2.0             # Marge sécurité bord (mm)
    
    # Trou pour ruban
    ribbon_hole_diameter: float = 4.0    # Diamètre trou ruban (mm)
    ribbon_hole_min_margin: float = 5.0  # Distance min du bord (mm)
    
    # Gravure
    min_text_height: float = 3.0         # Hauteur texte minimum (mm)
    min_engraving_width: float = 0.3     # Largeur gravure minimum (mm)


# Instance par défaut
DEFAULT_CONSTRAINTS = TrotecConstraints()


@dataclass
class ValidationResult:
    """Résultat de validation d'un design."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __str__(self) -> str:
        status = "✅ Valide" if self.is_valid else "❌ Invalide"
        msg = [status]
        if self.errors:
            msg.append("Erreurs:")
            msg.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            msg.append("Avertissements:")
            msg.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(msg)


def validate_medal_shape(
    polygon: Polygon,
    constraints: TrotecConstraints = DEFAULT_CONSTRAINTS
) -> ValidationResult:
    """
    Valide qu'une forme de médaille respecte les contraintes Trotec.
    
    Args:
        polygon: Forme de la médaille (Shapely Polygon)
        constraints: Contraintes de fabrication
        
    Returns:
        ValidationResult avec erreurs et avertissements
    """
    errors = []
    warnings = []
    
    # 1. Vérifier que le polygone est valide géométriquement
    if not polygon.is_valid:
        errors.append(f"Géométrie invalide: {explain_validity(polygon)}")
        return ValidationResult(False, errors, warnings)
    
    # 2. Vérifier les dimensions
    bounds = polygon.bounds  # (minx, miny, maxx, maxy)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    
    if width > constraints.max_width:
        errors.append(f"Largeur {width:.1f}mm > max {constraints.max_width}mm")
    if height > constraints.max_height:
        errors.append(f"Hauteur {height:.1f}mm > max {constraints.max_height}mm")
    
    # 3. Vérifier taille médaille (basé sur le plus grand côté)
    max_dim = max(width, height)
    min_dim = min(width, height)
    
    if max_dim < constraints.min_medal_diameter:
        errors.append(f"Médaille trop petite: {max_dim:.1f}mm < min {constraints.min_medal_diameter}mm")
    if max_dim > constraints.max_medal_diameter:
        errors.append(f"Médaille trop grande: {max_dim:.1f}mm > max {constraints.max_medal_diameter}mm")
    
    # 4. Vérifier les détails fins (approximation via buffer négatif)
    min_radius = constraints.min_bridge_width / 2
    eroded = polygon.buffer(-min_radius)
    if eroded.is_empty:
        errors.append(f"Forme trop fine: épaisseur < {constraints.min_bridge_width}mm")
    elif eroded.area < polygon.area * 0.3:
        warnings.append("Certaines zones peuvent être fragiles après découpe")
    
    # 5. Vérifier la surface (pas trop petite)
    if polygon.area < 500:  # mm²
        warnings.append(f"Surface très petite: {polygon.area:.0f}mm²")
    
    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def validate_ribbon_hole(
    medal_polygon: Polygon,
    hole_center: Point,
    constraints: TrotecConstraints = DEFAULT_CONSTRAINTS
) -> ValidationResult:
    """
    Valide le positionnement du trou pour le ruban.
    """
    errors = []
    warnings = []
    
    radius = constraints.ribbon_hole_diameter / 2
    hole = hole_center.buffer(radius)
    
    # Vérifier que le trou est dans la médaille
    if not medal_polygon.contains(hole):
        errors.append("Le trou pour ruban sort de la médaille")
    
    # Vérifier la distance au bord
    distance_to_edge = medal_polygon.exterior.distance(hole_center)
    min_distance = radius + constraints.ribbon_hole_min_margin
    
    if distance_to_edge < min_distance:
        errors.append(
            f"Trou trop près du bord: {distance_to_edge:.1f}mm < min {min_distance:.1f}mm"
        )
    
    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def validate_engraving_text(
    text_height: float,
    constraints: TrotecConstraints = DEFAULT_CONSTRAINTS
) -> ValidationResult:
    """
    Valide que le texte est assez grand pour être gravé lisiblement.
    """
    errors = []
    warnings = []
    
    if text_height < constraints.min_text_height:
        errors.append(
            f"Texte trop petit: {text_height:.1f}mm < min {constraints.min_text_height}mm"
        )
    elif text_height < constraints.min_text_height * 1.5:
        warnings.append(f"Texte petit ({text_height:.1f}mm), lisibilité réduite")
    
    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


if __name__ == "__main__":
    # Test des contraintes
    print("=== Test des contraintes Trotec ===\n")
    
    # Test 1: Médaille ronde valide
    center = Point(0, 0)
    medal = center.buffer(40)  # Rayon 40mm = diamètre 80mm
    result = validate_medal_shape(medal)
    print("Médaille ronde 80mm:")
    print(result)
    print()
    
    # Test 2: Médaille trop petite
    small_medal = center.buffer(15)  # Diamètre 30mm
    result = validate_medal_shape(small_medal)
    print("Médaille ronde 30mm:")
    print(result)
    print()
    
    # Test 3: Validation trou ruban
    medal = center.buffer(40)
    hole_pos = Point(0, 35)  # Près du haut
    result = validate_ribbon_hole(medal, hole_pos)
    print("Trou ruban à 5mm du bord:")
    print(result)
