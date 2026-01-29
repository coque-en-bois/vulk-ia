#!/usr/bin/env python3
"""
Générateur de Médailles OOOVATION
=================================

Outil de génération de médailles personnalisées pour découpe laser Trotec.

Usage:
    python main.py --type trail --name "Ultra Trail 2026" --distance 100K
    python main.py --type running --name "Marathon Paris" --year 2026
    python main.py --interactive
    python main.py --ai --name "Trail des Volcans" --distance 80K
"""

import argparse
from pathlib import Path
from datetime import datetime

from shapes import MedalShape, ShapeParams
from motifs import MotifType, MotifParams
from composer import (
    MedalComposition, 
    TextElement, 
    MotifElement,
    TextPosition,
    compose_medal,
    create_trail_medal,
    create_running_medal,
    create_swimming_medal,
    create_corporate_medal,
    create_custom_medal
)
from renderer import render_medal_svg, render_medal_png, render_production_svg


def generate_medal(
    event_type: str,
    event_name: str,
    year: str = None,
    distance: str = None,
    shape: str = None,
    diameter: float = 70.0,
    wood_type: str = "hetre",
    output_dir: str = "output"
) -> dict:
    """Génère une médaille complète."""
    if year is None:
        year = str(datetime.now().year)
    
    # Créer la composition selon le type
    if event_type == "trail":
        composition = create_trail_medal(
            event_name=event_name,
            year=year,
            distance=distance or "42K",
            diameter=diameter
        )
    elif event_type == "running":
        composition = create_running_medal(
            event_name=event_name,
            year=year,
            diameter=diameter
        )
    elif event_type == "swimming":
        composition = create_swimming_medal(
            event_name=event_name,
            year=year,
            diameter=diameter
        )
    elif event_type == "corporate":
        composition = create_corporate_medal(
            company_name=event_name.split()[0] if event_name else "COMPANY",
            event_name=" ".join(event_name.split()[1:]) if len(event_name.split()) > 1 else "Event",
            year=year,
            diameter=diameter
        )
    else:
        composition = MedalComposition(
            name=f"{event_name} {year}",
            shape_type=MedalShape.CIRCLE,
            shape_params=ShapeParams(width=diameter),
            ribbon_hole=True,
            texts=[
                TextElement(content=event_name.upper(), position=TextPosition.CENTER, font_size=6.0, bold=True),
                TextElement(content=year, position=TextPosition.BOTTOM, font_size=5.0)
            ]
        )
    
    # Forcer une forme si spécifiée
    if shape:
        try:
            composition.shape_type = MedalShape(shape.lower())
        except ValueError:
            print(f"⚠️  Forme '{shape}' inconnue, utilisation de la forme par défaut")
    
    # Composer la médaille
    medal = compose_medal(composition)
    
    # Créer le dossier de sortie
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Nom de fichier
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "" for c in event_name)
    safe_name = safe_name.replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{safe_name}_{year}_{timestamp}"
    
    # Générer les fichiers
    results = {
        "name": medal.name,
        "is_valid": medal.is_valid,
        "validation": str(medal.validation_result),
        "dimensions": {
            "width": round(medal.bounds[2] - medal.bounds[0], 1),
            "height": round(medal.bounds[3] - medal.bounds[1], 1)
        },
        "files": {}
    }
    
    # SVG prévisualisation
    svg_path = render_medal_svg(
        medal, 
        str(output_path / f"{base_name}_preview.svg"),
        wood_type=wood_type
    )
    results["files"]["preview_svg"] = str(svg_path)
    
    # SVG production
    prod_path = render_production_svg(
        medal,
        str(output_path / f"{base_name}_production.svg")
    )
    results["files"]["production_svg"] = str(prod_path)
    
    # PNG
    png_path = render_medal_png(
        medal,
        str(output_path / f"{base_name}_preview.png"),
        wood_type=wood_type,
        scale=10
    )
    if png_path:
        results["files"]["preview_png"] = str(png_path)
    
    return results


def interactive_mode():
    """Mode interactif pour créer une médaille."""
    print("\n" + "="*60)
    print("   🏅 GÉNÉRATEUR DE MÉDAILLES OOOVATION 🏅")
    print("="*60 + "\n")
    
    print("Types d'événements disponibles:")
    print("  1. trail     - Course nature/montagne")
    print("  2. running   - Course sur route")
    print("  3. swimming  - Natation")
    print("  4. corporate - Événement entreprise")
    print("  5. custom    - Personnalisé")
    print()
    
    event_type = input("Type d'événement [trail]: ").strip().lower() or "trail"
    
    default_names = {
        "trail": "Trail des Montagnes",
        "running": "Marathon de Paris",
        "swimming": "Traversée du Lac",
        "corporate": "OOOVATION Team Building"
    }
    default_name = default_names.get(event_type, "Mon Événement")
    event_name = input(f"Nom de l'événement [{default_name}]: ").strip() or default_name
    
    current_year = str(datetime.now().year)
    year = input(f"Année [{current_year}]: ").strip() or current_year
    
    distance = None
    if event_type in ["trail", "running"]:
        distance = input("Distance [42K]: ").strip() or "42K"
    
    diameter_str = input("Diamètre en mm [70]: ").strip()
    diameter = float(diameter_str) if diameter_str else 70.0
    
    print("\nFormes disponibles:")
    for shape in MedalShape:
        print(f"  - {shape.value}")
    shape = input("Forme (laisser vide pour défaut): ").strip() or None
    
    print("\nTypes de bois:")
    print("  - hetre (clair)")
    print("  - chene (moyen)")
    print("  - noyer (foncé)")
    print("  - bouleau (très clair)")
    wood_type = input("Type de bois [hetre]: ").strip() or "hetre"
    
    print("\n⏳ Génération en cours...\n")
    
    results = generate_medal(
        event_type=event_type,
        event_name=event_name,
        year=year,
        distance=distance,
        shape=shape,
        diameter=diameter,
        wood_type=wood_type
    )
    
    print("="*60)
    print(f"✅ Médaille générée: {results['name']}")
    print("="*60)
    print()
    print(f"Dimensions: {results['dimensions']['width']} x {results['dimensions']['height']} mm")
    print()
    print("Validation:")
    print(results['validation'])
    print()
    print("Fichiers générés:")
    for file_type, path in results['files'].items():
        print(f"  📄 {file_type}: {path}")
    print()
    
    return results


def ai_mode(
    event_name: str,
    event_type: str = "trail",
    year: str = None,
    distance: str = None,
    location: str = None,
    additional_info: str = None,
    output_dir: str = "output"
):
    """
    Mode IA : génère des suggestions créatives puis les médailles correspondantes.
    """
    from ai_suggester import get_ai_suggestions, print_suggestions, suggestion_to_composition_params, HAS_ANTHROPIC
    
    if not HAS_ANTHROPIC:
        print("❌ Le package 'anthropic' n'est pas installé.")
        print("   Installez-le avec: pip install anthropic")
        return None
    
    if year is None:
        year = str(datetime.now().year)
    
    print("\n" + "="*70)
    print("   🤖 MODE IA - SUGGESTIONS CRÉATIVES 🤖")
    print("="*70)
    print(f"\n📋 Événement: {event_name}")
    print(f"   Type: {event_type}")
    if distance:
        print(f"   Distance: {distance}")
    if location:
        print(f"   Lieu: {location}")
    
    print("\n⏳ Consultation de l'IA en cours...\n")
    
    # Obtenir les suggestions
    response = get_ai_suggestions(
        event_name=event_name,
        event_type=event_type,
        year=year,
        distance=distance,
        location=location,
        additional_info=additional_info
    )
    
    if not response:
        print("❌ Échec de la génération de suggestions")
        return None
    
    # Afficher les suggestions
    print_suggestions(response)
    
    # Demander quelle(s) suggestion(s) générer
    print("\n🎯 Quelle(s) médaille(s) voulez-vous générer ?")
    print("   1, 2, 3 : Générer une seule proposition")
    print("   all     : Générer les 3 propositions")
    print("   q       : Quitter sans générer")
    
    choice = input("\nVotre choix [all]: ").strip().lower() or "all"
    
    if choice == 'q':
        print("👋 Au revoir !")
        return None
    
    # Déterminer les indices à générer
    if choice == 'all':
        indices = [0, 1, 2]
    elif choice in ['1', '2', '3']:
        indices = [int(choice) - 1]
    else:
        print("❌ Choix invalide")
        return None
    
    # Générer les médailles
    all_results = []
    
    for idx in indices:
        if idx >= len(response.suggestions):
            continue
            
        suggestion = response.suggestions[idx]
        params = suggestion_to_composition_params(suggestion)
        
        print(f"\n⏳ Génération du concept {idx + 1}: {suggestion.name}...")
        
        # Créer la composition
        composition = create_custom_medal(**params)
        medal = compose_medal(composition)
        
        # Générer les fichiers
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "" for c in suggestion.name)
        safe_name = safe_name.replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"ai_{safe_name}_{timestamp}"
        
        results = {
            "name": suggestion.name,
            "description": suggestion.description,
            "is_valid": medal.is_valid,
            "dimensions": {
                "width": round(medal.bounds[2] - medal.bounds[0], 1),
                "height": round(medal.bounds[3] - medal.bounds[1], 1)
            },
            "files": {}
        }
        
        # SVG preview
        svg_path = render_medal_svg(
            medal,
            str(output_path / f"{base_name}_preview.svg"),
            wood_type=params.get("wood_type", "hetre")
        )
        results["files"]["preview_svg"] = str(svg_path)
        
        # SVG production
        prod_path = render_production_svg(
            medal,
            str(output_path / f"{base_name}_production.svg")
        )
        results["files"]["production_svg"] = str(prod_path)
        
        # PNG
        png_path = render_medal_png(
            medal,
            str(output_path / f"{base_name}_preview.png"),
            wood_type=params.get("wood_type", "hetre"),
            scale=10
        )
        if png_path:
            results["files"]["preview_png"] = str(png_path)
        
        all_results.append(results)
        
        print(f"   ✅ {suggestion.name}")
        print(f"      📄 {svg_path}")
    
    # Résumé
    print("\n" + "="*70)
    print("✅ GÉNÉRATION TERMINÉE")
    print("="*70)
    
    for result in all_results:
        print(f"\n💡 {result['name']}")
        print(f"   {result['description']}")
        print(f"   Dimensions: {result['dimensions']['width']} x {result['dimensions']['height']} mm")
        for file_type, path in result['files'].items():
            print(f"   📄 {path}")
    
    print()
    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Générateur de médailles OOOVATION",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py --interactive
  python main.py --type trail --name "Ultra Trail du Mont Blanc" --distance 170K
  python main.py --type running --name "Marathon de Paris" --year 2026 --shape hexagon
  python main.py --type corporate --name "OOOVATION Awards" --diameter 80
  
  # Mode IA (suggestions créatives)
  python main.py --ai --name "Trail des Volcans" --distance 80K --location "Auvergne"
        """
    )
    
    parser.add_argument("--interactive", "-i", action="store_true", help="Mode interactif")
    parser.add_argument("--ai", action="store_true", help="Mode IA - suggestions créatives (nécessite ANTHROPIC_API_KEY)")
    parser.add_argument("--type", "-t", choices=["trail", "running", "swimming", "corporate", "custom"], default="trail")
    parser.add_argument("--name", "-n", default="Mon Événement", help="Nom de l'événement")
    parser.add_argument("--year", "-y", default=str(datetime.now().year), help="Année")
    parser.add_argument("--distance", "-d", help="Distance (pour trail/running)")
    parser.add_argument("--location", "-l", help="Lieu de l'événement (pour mode IA)")
    parser.add_argument("--info", help="Informations supplémentaires (pour mode IA)")
    parser.add_argument("--shape", "-s", help="Forme de la médaille")
    parser.add_argument("--diameter", type=float, default=70.0, help="Diamètre en mm")
    parser.add_argument("--wood", choices=["hetre", "chene", "noyer", "bouleau"], default="hetre")
    parser.add_argument("--output", "-o", default="output", help="Dossier de sortie")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.ai:
        # Mode IA
        ai_mode(
            event_name=args.name,
            event_type=args.type,
            year=args.year,
            distance=args.distance,
            location=args.location,
            additional_info=args.info,
            output_dir=args.output
        )
    else:
        print(f"\n🏅 Génération de médaille: {args.name}\n")
        
        results = generate_medal(
            event_type=args.type,
            event_name=args.name,
            year=args.year,
            distance=args.distance,
            shape=args.shape,
            diameter=args.diameter,
            wood_type=args.wood,
            output_dir=args.output
        )
        
        print(f"✅ Médaille générée: {results['name']}")
        print(f"   Dimensions: {results['dimensions']['width']} x {results['dimensions']['height']} mm")
        print(f"   Valide: {'Oui' if results['is_valid'] else 'Non'}")
        print()
        print("Fichiers:")
        for file_type, path in results['files'].items():
            print(f"   📄 {path}")


if __name__ == "__main__":
    main()
