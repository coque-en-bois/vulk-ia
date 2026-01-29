"""
Bibliothèque de formes de base pour médailles.
Toutes les formes sont générées en tant que Shapely Polygons.
"""

import math
from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from shapely.geometry import Polygon, Point, box
from shapely.affinity import rotate


class MedalShape(Enum):
    """Types de formes de médailles disponibles."""
    CIRCLE = "circle"
    HEXAGON = "hexagon"
    OCTAGON = "octagon"
    SHIELD = "shield"
    STAR = "star"
    DROP = "drop"
    RECTANGLE = "rectangle"
    ROUNDED_RECTANGLE = "rounded_rectangle"
    GEAR = "gear"
    LEAF = "leaf"


@dataclass
class ShapeParams:
    """Paramètres communs pour la génération de formes."""
    width: float = 70.0           # Largeur en mm
    height: Optional[float] = None  # Hauteur (si None, = width)
    rotation: float = 0.0         # Rotation en degrés
    corner_radius: float = 0.0    # Rayon des coins arrondis
    
    def __post_init__(self):
        if self.height is None:
            self.height = self.width


def create_circle(diameter: float = 70.0) -> Polygon:
    """Crée une médaille ronde."""
    center = Point(0, 0)
    return center.buffer(diameter / 2, resolution=64)


def create_regular_polygon(n_sides: int, diameter: float = 70.0, rotation: float = 0.0) -> Polygon:
    """Crée un polygone régulier (hexagone, octogone, etc.)."""
    radius = diameter / 2
    angles = [2 * math.pi * i / n_sides for i in range(n_sides)]
    points = [(radius * math.cos(a), radius * math.sin(a)) for a in angles]
    polygon = Polygon(points)
    
    if rotation != 0:
        polygon = rotate(polygon, rotation, origin=(0, 0))
    
    return polygon


def create_hexagon(diameter: float = 70.0, flat_top: bool = True) -> Polygon:
    """Crée une médaille hexagonale."""
    rotation = 0 if flat_top else 30
    return create_regular_polygon(6, diameter, rotation)


def create_octagon(diameter: float = 70.0) -> Polygon:
    """Crée une médaille octogonale."""
    return create_regular_polygon(8, diameter, rotation=22.5)


def create_star(
    n_points: int = 5,
    outer_diameter: float = 70.0,
    inner_ratio: float = 0.4
) -> Polygon:
    """Crée une médaille en forme d'étoile."""
    outer_radius = outer_diameter / 2
    inner_radius = outer_radius * inner_ratio
    
    points = []
    for i in range(n_points * 2):
        angle = math.pi / 2 + (math.pi * i / n_points)
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y))
    
    return Polygon(points)


def create_shield(width: float = 60.0, height: float = 80.0) -> Polygon:
    """Crée une médaille en forme d'écusson/bouclier."""
    top_height = height * 0.35
    curve_height = height * 0.65
    
    points = []
    points.append((-width/2, height/2))
    points.append((width/2, height/2))
    points.append((width/2, height/2 - top_height))
    
    n_curve_points = 16
    for i in range(1, n_curve_points):
        t = i / n_curve_points
        x = width/2 * (1 - t) * (1 - t*0.3)
        y = (height/2 - top_height) - curve_height * t
        points.append((x, y))
    
    points.append((0, -height/2))
    
    for i in range(n_curve_points - 1, 0, -1):
        t = i / n_curve_points
        x = -width/2 * (1 - t) * (1 - t*0.3)
        y = (height/2 - top_height) - curve_height * t
        points.append((x, y))
    
    points.append((-width/2, height/2 - top_height))
    
    return Polygon(points)


def create_drop(width: float = 50.0, height: float = 70.0) -> Polygon:
    """Crée une médaille en forme de goutte d'eau."""
    points = []
    n_points = 32
    
    circle_radius = width / 2
    circle_center_y = -height/2 + circle_radius
    
    for i in range(n_points // 2 + 1):
        angle = math.pi + (math.pi * i / (n_points // 2))
        x = circle_radius * math.cos(angle)
        y = circle_center_y + circle_radius * math.sin(angle)
        points.append((x, y))
    
    tip_y = height / 2
    for i in range(1, n_points // 4):
        t = i / (n_points // 4)
        x = circle_radius * (1 - t**1.5)
        y = circle_center_y + circle_radius + (tip_y - circle_center_y - circle_radius) * t
        points.append((x, y))
    
    points.append((0, tip_y))
    
    for i in range(n_points // 4 - 1, 0, -1):
        t = i / (n_points // 4)
        x = -circle_radius * (1 - t**1.5)
        y = circle_center_y + circle_radius + (tip_y - circle_center_y - circle_radius) * t
        points.append((x, y))
    
    return Polygon(points)


def create_rounded_rectangle(
    width: float = 70.0,
    height: float = 50.0,
    corner_radius: float = 8.0
) -> Polygon:
    """Crée un rectangle aux coins arrondis."""
    rect = box(-width/2 + corner_radius, -height/2 + corner_radius,
               width/2 - corner_radius, height/2 - corner_radius)
    return rect.buffer(corner_radius, join_style=1)


def create_gear(
    outer_diameter: float = 70.0,
    n_teeth: int = 12,
    tooth_depth: float = 5.0
) -> Polygon:
    """Crée une médaille en forme d'engrenage."""
    outer_radius = outer_diameter / 2
    inner_radius = outer_radius - tooth_depth
    
    points = []
    tooth_angle = 2 * math.pi / n_teeth
    
    for i in range(n_teeth):
        base_angle = i * tooth_angle - math.pi / 2
        
        a1 = base_angle
        points.append((inner_radius * math.cos(a1), inner_radius * math.sin(a1)))
        
        a2 = base_angle + tooth_angle * 0.2
        points.append((inner_radius * math.cos(a2), inner_radius * math.sin(a2)))
        
        a3 = base_angle + tooth_angle * 0.25
        points.append((outer_radius * math.cos(a3), outer_radius * math.sin(a3)))
        
        a4 = base_angle + tooth_angle * 0.75
        points.append((outer_radius * math.cos(a4), outer_radius * math.sin(a4)))
        
        a5 = base_angle + tooth_angle * 0.8
        points.append((inner_radius * math.cos(a5), inner_radius * math.sin(a5)))
    
    return Polygon(points)


def create_leaf(width: float = 50.0, height: float = 80.0) -> Polygon:
    """Crée une médaille en forme de feuille."""
    points = []
    n_points = 24
    
    points.append((0, -height/2))
    
    for i in range(1, n_points):
        t = i / n_points
        x = -width/2 * math.sin(t * math.pi) * (1 - t*0.3)
        y = -height/2 + height * t
        points.append((x, y))
    
    points.append((0, height/2))
    
    for i in range(n_points - 1, 0, -1):
        t = i / n_points
        x = width/2 * math.sin(t * math.pi) * (1 - t*0.3)
        y = -height/2 + height * t
        points.append((x, y))
    
    return Polygon(points)


def get_shape(
    shape_type: MedalShape,
    params: Optional[ShapeParams] = None
) -> Polygon:
    """Factory function pour créer une forme de médaille."""
    if params is None:
        params = ShapeParams()
    
    shape_creators = {
        MedalShape.CIRCLE: lambda: create_circle(params.width),
        MedalShape.HEXAGON: lambda: create_hexagon(params.width),
        MedalShape.OCTAGON: lambda: create_octagon(params.width),
        MedalShape.STAR: lambda: create_star(outer_diameter=params.width),
        MedalShape.SHIELD: lambda: create_shield(params.width, params.height),
        MedalShape.DROP: lambda: create_drop(params.width, params.height),
        MedalShape.RECTANGLE: lambda: create_rounded_rectangle(
            params.width, params.height, params.corner_radius or 5.0
        ),
        MedalShape.ROUNDED_RECTANGLE: lambda: create_rounded_rectangle(
            params.width, params.height, params.corner_radius or 8.0
        ),
        MedalShape.GEAR: lambda: create_gear(params.width),
        MedalShape.LEAF: lambda: create_leaf(params.width, params.height),
    }
    
    polygon = shape_creators[shape_type]()
    
    if params.rotation != 0:
        polygon = rotate(polygon, params.rotation, origin=(0, 0))
    
    return polygon


def calculate_ribbon_hole_position(
    polygon: Polygon,
    margin: float = 6.0
) -> Tuple[float, float]:
    """Calcule la position optimale du trou pour le ruban."""
    bounds = polygon.bounds
    top_y = bounds[3]
    center_x = (bounds[0] + bounds[2]) / 2
    hole_y = top_y - margin
    
    return (center_x, hole_y)


if __name__ == "__main__":
    print("=== Formes de médailles disponibles ===\n")
    
    for shape_type in MedalShape:
        params = ShapeParams(width=70, height=80)
        polygon = get_shape(shape_type, params)
        bounds = polygon.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        print(f"{shape_type.value:20} | {width:.1f} x {height:.1f} mm | Aire: {polygon.area:.0f} mm²")
