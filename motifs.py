"""
Bibliothèque de motifs décoratifs pour gravure sur médailles.
"""

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from shapely.geometry import Polygon


class MotifType(Enum):
    """Types de motifs disponibles."""
    MOUNTAINS = "mountains"
    WAVES = "waves"
    LAUREL = "laurel"
    RAYS = "rays"
    CHEVRONS = "chevrons"
    TREES = "trees"
    RUNNING_TRACK = "running_track"
    FINISH_LINE = "finish_line"


@dataclass
class MotifParams:
    """Paramètres pour la génération de motifs."""
    width: float = 60.0
    height: float = 20.0
    detail_level: int = 3
    offset_x: float = 0.0
    offset_y: float = 0.0


def create_mountains(
    width: float = 60.0,
    height: float = 25.0,
    n_peaks: int = 3,
    style: str = "simple"
) -> List[List[Tuple[float, float]]]:
    """Crée un motif de montagnes (idéal pour trails)."""
    lines = []
    
    if style == "simple":
        points = [(-width/2, 0)]
        peak_width = width / n_peaks
        for i in range(n_peaks):
            base_x = -width/2 + i * peak_width
            peak_x = base_x + peak_width / 2
            peak_heights = [0.8, 1.0, 0.6] if n_peaks == 3 else [1.0] * n_peaks
            peak_h = height * peak_heights[i % len(peak_heights)]
            points.append((peak_x, peak_h))
            points.append((base_x + peak_width, 0))
        lines.append(points)
        
    elif style == "detailed":
        peak_width = width / n_peaks
        for i in range(n_peaks):
            base_x = -width/2 + i * peak_width
            peak_x = base_x + peak_width / 2
            peak_heights = [0.7, 1.0, 0.5]
            peak_h = height * peak_heights[i % 3]
            
            mountain = [
                (base_x + peak_width * 0.1, 0),
                (peak_x, peak_h),
                (base_x + peak_width * 0.9, 0)
            ]
            lines.append(mountain)
            
            snow_y = peak_h * 0.7
            snow_width = peak_width * 0.25
            snow = [
                (peak_x - snow_width, snow_y),
                (peak_x, peak_h),
                (peak_x + snow_width, snow_y)
            ]
            lines.append(snow)
    
    return lines


def create_waves(
    width: float = 60.0,
    height: float = 15.0,
    n_waves: int = 3,
    n_rows: int = 2
) -> List[List[Tuple[float, float]]]:
    """Crée un motif de vagues (idéal pour natation, triathlon)."""
    lines = []
    wave_width = width / n_waves
    row_spacing = height * 0.6
    
    for row in range(n_rows):
        points = []
        base_y = -row * row_spacing
        
        for i in range(n_waves * 10 + 1):
            t = i / 10
            x = -width/2 + t * wave_width
            if x > width/2:
                break
            y = base_y + height * 0.5 * math.sin(t * 2 * math.pi)
            points.append((x, y))
        
        lines.append(points)
    
    return lines


def create_laurel(
    width: float = 60.0,
    height: float = 40.0,
    n_leaves: int = 6
) -> List[List[Tuple[float, float]]]:
    """Crée une couronne de laurier (classique pour victoire)."""
    lines = []
    
    for side in [-1, 1]:
        stem = []
        for i in range(20):
            t = i / 19
            x = side * (width/2 - 5) * (1 - t*0.3)
            y = -height/2 + height * t
            stem.append((x, y))
        lines.append(stem)
        
        for i in range(n_leaves):
            t = (i + 1) / (n_leaves + 1)
            base_x = side * (width/2 - 5) * (1 - t*0.3)
            base_y = -height/2 + height * t
            
            leaf = []
            leaf_length = 8
            leaf_width = 3
            
            for j in range(10):
                lt = j / 9
                lx = base_x + side * leaf_length * lt * (1 - t*0.5)
                ly = base_y + leaf_width * math.sin(lt * math.pi) * (1 - t*0.3)
                leaf.append((lx, ly))
            
            lines.append(leaf)
    
    return lines


def create_rays(
    center: Tuple[float, float] = (0, 0),
    inner_radius: float = 15.0,
    outer_radius: float = 30.0,
    n_rays: int = 12
) -> List[List[Tuple[float, float]]]:
    """Crée des rayons partant du centre."""
    lines = []
    cx, cy = center
    
    for i in range(n_rays):
        angle = 2 * math.pi * i / n_rays - math.pi/2
        x1 = cx + inner_radius * math.cos(angle)
        y1 = cy + inner_radius * math.sin(angle)
        x2 = cx + outer_radius * math.cos(angle)
        y2 = cy + outer_radius * math.sin(angle)
        lines.append([(x1, y1), (x2, y2)])
    
    return lines


def create_geometric_border(
    polygon: Polygon,
    offset: float = 3.0,
    style: str = "line"
) -> List[List[Tuple[float, float]]]:
    """Crée une bordure géométrique suivant le contour."""
    lines = []
    inner = polygon.buffer(-offset)
    
    if inner.is_empty:
        return lines
    
    if style == "line":
        coords = list(inner.exterior.coords)
        lines.append(coords)
    
    return lines


def create_chevrons(
    width: float = 40.0,
    height: float = 20.0,
    n_chevrons: int = 3
) -> List[List[Tuple[float, float]]]:
    """Crée un motif de chevrons (dynamique, sportif)."""
    lines = []
    spacing = height / (n_chevrons + 1)
    
    for i in range(n_chevrons):
        y_base = height/2 - (i + 1) * spacing
        chevron = [
            (-width/2, y_base + spacing * 0.3),
            (0, y_base),
            (width/2, y_base + spacing * 0.3)
        ]
        lines.append(chevron)
    
    return lines


def create_trees(
    width: float = 50.0,
    height: float = 25.0,
    n_trees: int = 3
) -> List[List[Tuple[float, float]]]:
    """Crée des silhouettes de sapins (trail, nature)."""
    lines = []
    tree_spacing = width / n_trees
    heights = [0.7, 1.0, 0.8] if n_trees == 3 else [1.0] * n_trees
    
    for i in range(n_trees):
        tree_height = height * heights[i % len(heights)]
        center_x = -width/2 + tree_spacing * (i + 0.5)
        tree_width = tree_spacing * 0.6
        
        tree = [
            (center_x - tree_width/2, 0),
            (center_x, tree_height),
            (center_x + tree_width/2, 0),
            (center_x - tree_width/2, 0)
        ]
        lines.append(tree)
        
        trunk_width = tree_width * 0.15
        trunk = [
            (center_x - trunk_width, 0),
            (center_x - trunk_width, -height * 0.1),
            (center_x + trunk_width, -height * 0.1),
            (center_x + trunk_width, 0)
        ]
        lines.append(trunk)
    
    return lines


def create_running_track(
    width: float = 50.0,
    n_lanes: int = 3
) -> List[List[Tuple[float, float]]]:
    """Crée des lignes de piste d'athlétisme."""
    lines = []
    lane_spacing = 4.0
    
    for i in range(n_lanes):
        y = (i - n_lanes/2 + 0.5) * lane_spacing
        line = [(-width/2, y), (width/2, y)]
        lines.append(line)
    
    return lines


def create_finish_line(
    width: float = 30.0,
    height: float = 20.0,
    n_squares: int = 6
) -> List[List[Tuple[float, float]]]:
    """Crée un motif damier de ligne d'arrivée."""
    lines = []
    square_size = width / n_squares
    n_rows = int(height / square_size)
    
    for row in range(n_rows):
        for col in range(n_squares):
            if (row + col) % 2 == 0:
                x = -width/2 + col * square_size
                y = -height/2 + row * square_size
                square = [
                    (x, y),
                    (x + square_size, y),
                    (x + square_size, y + square_size),
                    (x, y + square_size),
                    (x, y)
                ]
                lines.append(square)
    
    return lines


def get_motif(
    motif_type: MotifType,
    params: Optional[MotifParams] = None,
    **kwargs
) -> List[List[Tuple[float, float]]]:
    """Factory function pour créer un motif."""
    if params is None:
        params = MotifParams()
    
    motif_creators = {
        MotifType.MOUNTAINS: lambda: create_mountains(params.width, params.height),
        MotifType.WAVES: lambda: create_waves(params.width, params.height),
        MotifType.LAUREL: lambda: create_laurel(params.width, params.height),
        MotifType.RAYS: lambda: create_rays(**kwargs) if kwargs else create_rays(),
        MotifType.CHEVRONS: lambda: create_chevrons(params.width, params.height),
        MotifType.TREES: lambda: create_trees(params.width, params.height),
        MotifType.RUNNING_TRACK: lambda: create_running_track(params.width),
        MotifType.FINISH_LINE: lambda: create_finish_line(params.width, params.height),
    }
    
    lines = motif_creators.get(motif_type, lambda: [])()
    
    if params.offset_x != 0 or params.offset_y != 0:
        lines = [
            [(x + params.offset_x, y + params.offset_y) for x, y in line]
            for line in lines
        ]
    
    return lines


if __name__ == "__main__":
    print("=== Motifs disponibles ===\n")
    
    for motif_type in MotifType:
        params = MotifParams(width=50, height=25)
        lines = get_motif(motif_type, params)
        n_lines = len(lines)
        n_points = sum(len(line) for line in lines)
        print(f"{motif_type.value:20} | {n_lines:2} lignes | {n_points:3} points")
