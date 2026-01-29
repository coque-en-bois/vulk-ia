"""
Module d'intégration IA pour suggestions créatives de médailles.
Utilise l'API Anthropic (Claude) pour générer des concepts originaux.
"""

import json
import os
from typing import List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Charger les variables d'environnement depuis .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv non installé, on utilise les variables système

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from shapes import MedalShape
from motifs import MotifType


@dataclass
class MedalSuggestion:
    """Une suggestion de médaille générée par l'IA."""
    name: str                          # Nom du concept (accrocheur!)
    tagline: str                       # Slogan vendeur
    description: str                   # Description créative et immersive
    shape: str                         # Forme suggérée
    primary_motif: str                 # Motif principal
    secondary_motif: Optional[str]     # Motif secondaire (optionnel)
    color_wood: str                    # Type de bois suggéré
    text_main: str                     # Texte principal
    text_secondary: str                # Texte secondaire
    text_year: str                     # Année/date
    style_notes: str                   # Notes sur le style
    diameter: int                      # Diamètre suggéré (mm)
    # Nouvelles options couleur UV
    uv_colors: Optional[List[str]]     # Couleurs UV à appliquer (ex: ["#FF6B35", "#2E86AB"])
    uv_zones: Optional[str]            # Description des zones colorées
    finish: str                        # Finition (naturel, vernis, mat, brillant)
    emotional_impact: str              # Impact émotionnel recherché
    unique_feature: str                # Élément différenciant unique


@dataclass 
class AIResponse:
    """Réponse complète de l'IA."""
    event_analysis: str                # Analyse de l'événement
    suggestions: List[MedalSuggestion] # 3 suggestions
    recommendation: str                # Recommandation finale
    creative_vision: str = ""          # Vision créative globale


# Formes et motifs disponibles pour le prompt
AVAILABLE_SHAPES = [s.value for s in MedalShape]
AVAILABLE_MOTIFS = [m.value for m in MotifType]
AVAILABLE_WOODS = ["hetre", "chene", "noyer", "bouleau", "erable"]

SYSTEM_PROMPT = """Tu es un DIRECTEUR ARTISTIQUE de renom, spécialisé dans le design de médailles d'exception.
Tu travailles pour OOOVATION, créateur français de médailles sportives qui allie artisanat du bois et innovation.

🎯 TON OBJECTIF : Créer des propositions qui font RÊVER le client et lui donnent envie de SIGNER IMMÉDIATEMENT.

Tu ne crées pas de simples médailles, tu crées des ŒUVRES D'ART, des TROPHÉES ÉMOTIONNELS que les athlètes 
garderont toute leur vie. Chaque médaille raconte une HISTOIRE, capture un MOMENT, immortalise un EXPLOIT.

🎨 NOTRE ATELIER DISPOSE DE :
• Découpe laser Trotec haute précision (formes complexes possibles)
• Gravure laser pour détails fins et textures
• IMPRESSION UV COULEUR (couleurs vibrantes sur bois!)
• 5 essences de bois nobles
• Finitions premium (vernis, mat, brillant, effet vieilli)

FORMES DISPONIBLES :
{shapes}

MOTIFS DISPONIBLES (peuvent être combinés, superposés, stylisés) :
{motifs}

ESSENCES DE BOIS :
- hetre : Élégance scandinave, tons miel lumineux
- chene : Noblesse française, caractère et robustesse  
- noyer : Luxe absolu, profondeur chocolatée
- bouleau : Pureté nordique, blancheur immaculée
- erable : Veinage artistique, lumière naturelle

🌈 IMPRESSION UV - LIBÈRE TA CRÉATIVITÉ !
Tu peux proposer des touches de couleur UV sur certaines zones :
- Dégradés de couleurs sur les motifs
- Accents colorés (ex: orange pour le feu, bleu pour l'eau)
- Logo ou éléments graphiques en couleur
- Contraste couleur/bois naturel
Propose des palettes de 1 à 3 couleurs cohérentes avec le thème.

💫 STYLE DE COMMUNICATION :
- Utilise un vocabulaire ÉVOCATEUR et SENSORIEL
- Crée des noms de concepts MÉMORABLES 
- Décris l'ÉMOTION que procurera la médaille
- Imagine le moment où l'athlète la recevra

Tu dois TOUJOURS répondre en JSON valide avec exactement cette structure :
{{
    "event_analysis": "Analyse immersive de l'événement - son âme, son histoire, ce qui le rend unique",
    "creative_vision": "Ta vision artistique globale pour ce projet",
    "suggestions": [
        {{
            "name": "Nom mémorable et évocateur",
            "tagline": "Slogan accrocheur en 5-7 mots",
            "description": "Description immersive de 3-4 phrases qui fait vivre le design, évoque les sensations, l'émotion du finisher",
            "shape": "forme_choisie",
            "primary_motif": "motif_principal",
            "secondary_motif": "motif_secondaire ou null",
            "color_wood": "type_de_bois",
            "text_main": "TEXTE PRINCIPAL",
            "text_secondary": "Texte secondaire poétique",
            "text_year": "2026",
            "style_notes": "Description artistique du rendu visuel",
            "diameter": 75,
            "uv_colors": ["#HEX1", "#HEX2"] ou null si tout bois naturel,
            "uv_zones": "Description des zones colorées (ex: 'dégradé sunset sur les montagnes, accent doré sur le texte')",
            "finish": "naturel/vernis/mat/brillant/vieilli",
            "emotional_impact": "L'émotion que ressentira l'athlète en recevant cette médaille",
            "unique_feature": "L'élément WOW qui différencie ce design"
        }}
    ],
    "recommendation": "Conseil passionné sur LE concept qui fera mouche, avec des arguments émotionnels"
}}

📦 PROPOSE EXACTEMENT 3 CONCEPTS DISTINCTS :

1. 🏆 PRESTIGE CLASSIQUE 
   - Élégance intemporelle, lignes épurées, bois nobles
   - Pour les clients qui aiment le raffinement traditionnel
   - Peut inclure des accents dorés ou argentés en UV

2. 🚀 AUDACE CONTEMPORAINE
   - Formes originales, couleurs vibrantes, design impactant  
   - Pour marquer les esprits et créer le buzz
   - Ose les couleurs vives et les formes atypiques

3. 🌿 ESSENCE NATURE
   - Connexion à l'environnement, authenticité, bois brut
   - Pour les événements éco-responsables ou nature
   - Peut jouer sur les textures et le bois apparent

SOIS AUDACIEUX, CRÉATIF, INSPIRANT ! Le client doit sentir que tu as compris son événement et que tu lui proposes quelque chose d'UNIQUE.
"""


def get_ai_suggestions(
    event_name: str,
    event_type: str,
    year: str = "2026",
    distance: Optional[str] = None,
    location: Optional[str] = None,
    additional_info: Optional[str] = None,
    api_key: Optional[str] = None
) -> Optional[AIResponse]:
    """
    Obtient des suggestions créatives de l'IA pour une médaille.
    
    Args:
        event_name: Nom de l'événement
        event_type: Type (trail, running, swimming, corporate, etc.)
        year: Année de l'événement
        distance: Distance (pour les courses)
        location: Lieu de l'événement
        additional_info: Infos supplémentaires
        api_key: Clé API Anthropic (ou variable d'env ANTHROPIC_API_KEY)
        
    Returns:
        AIResponse avec 3 suggestions, ou None si erreur
    """
    if not HAS_ANTHROPIC:
        print("❌ Le package 'anthropic' n'est pas installé.")
        print("   Installez-le avec: pip install anthropic")
        return None
    
    # Récupérer la clé API
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Clé API Anthropic non trouvée.")
        print("   Définissez ANTHROPIC_API_KEY ou passez api_key en paramètre.")
        return None
    
    # Construire le prompt utilisateur
    user_prompt = f"""Propose 3 concepts de médailles pour cet événement :

ÉVÉNEMENT : {event_name}
TYPE : {event_type}
ANNÉE : {year}
"""
    
    if distance:
        user_prompt += f"DISTANCE : {distance}\n"
    if location:
        user_prompt += f"LIEU : {location}\n"
    if additional_info:
        user_prompt += f"INFORMATIONS SUPPLÉMENTAIRES : {additional_info}\n"
    
    user_prompt += "\nPropose 3 concepts variés et créatifs en JSON."
    
    # Appeler l'API
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        system = SYSTEM_PROMPT.format(
            shapes=", ".join(AVAILABLE_SHAPES),
            motifs=", ".join(AVAILABLE_MOTIFS)
        )
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            system=system
        )
        
        # Parser la réponse JSON
        response_text = message.content[0].text
        
        # Nettoyer si nécessaire (enlever les ```json si présents)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        data = json.loads(response_text.strip())
        
        # Construire la réponse
        suggestions = []
        for s in data.get("suggestions", []):
            suggestions.append(MedalSuggestion(
                name=s.get("name", ""),
                tagline=s.get("tagline", ""),
                description=s.get("description", ""),
                shape=s.get("shape", "circle"),
                primary_motif=s.get("primary_motif", "mountains"),
                secondary_motif=s.get("secondary_motif"),
                color_wood=s.get("color_wood", "hetre"),
                text_main=s.get("text_main", event_name.upper()),
                text_secondary=s.get("text_secondary", ""),
                text_year=s.get("text_year", year),
                style_notes=s.get("style_notes", ""),
                diameter=s.get("diameter", 70),
                uv_colors=s.get("uv_colors"),
                uv_zones=s.get("uv_zones"),
                finish=s.get("finish", "naturel"),
                emotional_impact=s.get("emotional_impact", ""),
                unique_feature=s.get("unique_feature", "")
            ))
        
        return AIResponse(
            event_analysis=data.get("event_analysis", ""),
            suggestions=suggestions,
            recommendation=data.get("recommendation", ""),
            creative_vision=data.get("creative_vision", "")
        )
        
    except anthropic.APIConnectionError:
        print("❌ Erreur de connexion à l'API Anthropic")
        return None
    except anthropic.RateLimitError:
        print("❌ Limite de requêtes atteinte. Réessayez dans quelques instants.")
        return None
    except anthropic.APIStatusError as e:
        print(f"❌ Erreur API Anthropic: {e.status_code} - {e.message}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        print(f"   Réponse brute: {response_text[:500]}...")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return None


def suggestion_to_composition_params(suggestion: MedalSuggestion) -> dict:
    """
    Convertit une suggestion IA en paramètres pour le composeur.
    
    Args:
        suggestion: Suggestion de l'IA
        
    Returns:
        Dict de paramètres pour create_custom_medal()
    """
    # Mapper la forme
    try:
        shape = MedalShape(suggestion.shape)
    except ValueError:
        shape = MedalShape.CIRCLE
    
    # Mapper le motif principal
    try:
        primary_motif = MotifType(suggestion.primary_motif)
    except ValueError:
        primary_motif = MotifType.MOUNTAINS
    
    # Mapper le motif secondaire
    secondary_motif = None
    if suggestion.secondary_motif:
        try:
            secondary_motif = MotifType(suggestion.secondary_motif)
        except ValueError:
            pass
    
    return {
        "shape": shape,
        "primary_motif": primary_motif,
        "secondary_motif": secondary_motif,
        "wood_type": suggestion.color_wood,
        "text_main": suggestion.text_main,
        "text_secondary": suggestion.text_secondary,
        "text_year": suggestion.text_year,
        "diameter": suggestion.diameter,
        "concept_name": suggestion.name
    }


def print_suggestions(response: AIResponse):
    """Affiche les suggestions de manière formatée et vendeuse."""
    print("\n" + "="*70)
    print("✨ PROPOSITIONS CRÉATIVES POUR VOTRE MÉDAILLE ✨")
    print("="*70)
    
    print(f"\n🎯 {response.event_analysis}\n")
    
    if hasattr(response, 'creative_vision') and response.creative_vision:
        print(f"🎨 Vision artistique : {response.creative_vision}\n")
    
    concept_icons = ["🏆", "🚀", "🌿"]
    concept_names = ["PRESTIGE CLASSIQUE", "AUDACE CONTEMPORAINE", "ESSENCE NATURE"]
    
    for i, suggestion in enumerate(response.suggestions, 1):
        icon = concept_icons[i-1] if i <= 3 else "💡"
        concept_type = concept_names[i-1] if i <= 3 else "CONCEPT"
        
        print(f"\n{'═'*70}")
        print(f"{icon} {concept_type}")
        print(f"{'═'*70}")
        print(f"\n   ✦ {suggestion.name.upper()}")
        if suggestion.tagline:
            print(f"   « {suggestion.tagline} »")
        print()
        print(f"   {suggestion.description}")
        print()
        
        print(f"   ┌─────────────────────────────────────────────────────────")
        print(f"   │ 🔷 Forme     : {suggestion.shape.upper()}")
        print(f"   │ 🎨 Motifs    : {suggestion.primary_motif}", end="")
        if suggestion.secondary_motif:
            print(f" + {suggestion.secondary_motif}")
        else:
            print()
        print(f"   │ 🪵 Essence   : {suggestion.color_wood.upper()}")
        print(f"   │ 📏 Dimension : Ø {suggestion.diameter}mm")
        print(f"   │ ✨ Finition  : {suggestion.finish}")
        
        if suggestion.uv_colors:
            colors_display = " ".join([f"[{c}]" for c in suggestion.uv_colors])
            print(f"   │ 🌈 Couleurs UV : {colors_display}")
            if suggestion.uv_zones:
                print(f"   │    └─ {suggestion.uv_zones}")
        
        print(f"   └─────────────────────────────────────────────────────────")
        
        print(f"\n   📝 Textes gravés :")
        print(f"      • Principal : \"{suggestion.text_main}\"")
        print(f"      • Secondaire : \"{suggestion.text_secondary}\"")
        print(f"      • Année : \"{suggestion.text_year}\"")
        
        if suggestion.unique_feature:
            print(f"\n   💎 Ce qui rend ce design unique :")
            print(f"      {suggestion.unique_feature}")
        
        if suggestion.emotional_impact:
            print(f"\n   💫 L'émotion au moment de la remise :")
            print(f"      {suggestion.emotional_impact}")
        
        print(f"\n   🎨 Direction artistique :")
        print(f"      {suggestion.style_notes}")
    
    print(f"\n{'═'*70}")
    print(f"⭐ NOTRE RECOMMANDATION")
    print(f"{'═'*70}")
    print(f"\n   {response.recommendation}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Test du module
    print("🧪 Test du module AI Suggester\n")
    
    if not HAS_ANTHROPIC:
        print("⚠️  Package 'anthropic' non installé")
        print("   pip install anthropic")
        exit(1)
    
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  Variable ANTHROPIC_API_KEY non définie")
        print("   export ANTHROPIC_API_KEY='votre-clé'")
        exit(1)
    
    # Test avec un événement
    response = get_ai_suggestions(
        event_name="Ultra Trail du Vercors",
        event_type="trail",
        year="2026",
        distance="80K",
        location="Massif du Vercors, France",
        additional_info="Course de montagne avec 5000m de dénivelé positif, ambiance nature et dépassement de soi"
    )
    
    if response:
        print_suggestions(response)
    else:
        print("❌ Échec de la génération de suggestions")
