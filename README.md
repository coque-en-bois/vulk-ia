# 🏅 Générateur de Médailles OOOVATION

Outil de génération de médailles personnalisées en bois pour découpe laser Trotec.

## 🎯 Objectif

Générer des propositions visuelles de médailles pour les devis clients, avec validation automatique des contraintes de fabrication.

## 🚀 Installation

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

## 📖 Utilisation

### Mode interactif (recommandé)

```bash
python main.py --interactive
```

### Mode ligne de commande

```bash
# Médaille trail
python main.py --type trail --name "Ultra Trail du Mont Blanc" --distance 170K

# Médaille running
python main.py --type running --name "Marathon de Paris" --year 2026 --shape hexagon

# Médaille entreprise
python main.py --type corporate --name "OOOVATION Awards" --diameter 80
```

### Options disponibles

| Option             | Description                               | Défaut        |
| ------------------ | ----------------------------------------- | ------------- |
| `--type`, `-t`     | Type: trail, running, swimming, corporate | trail         |
| `--name`, `-n`     | Nom de l'événement                        | Mon Événement |
| `--year`, `-y`     | Année                                     | 2026          |
| `--distance`, `-d` | Distance (trail/running)                  | 42K           |
| `--shape`, `-s`    | Forme: circle, hexagon, shield, etc.      | auto          |
| `--diameter`       | Diamètre en mm                            | 70            |
| `--wood`           | Bois: hetre, chene, noyer, bouleau        | hetre         |

## 📁 Fichiers générés

1. **`*_preview.svg`** - Prévisualisation couleur (pour le client)
2. **`*_production.svg`** - Fichier Trotec (rouge=découpe, bleu=gravure)
3. **`*_preview.png`** - Image PNG haute résolution

## 📐 Formes disponibles

- `circle` - Ronde
- `hexagon` - Hexagonale
- `octagon` - Octogonale
- `shield` - Écusson
- `star` - Étoile
- `drop` - Goutte
- `gear` - Engrenage
- `leaf` - Feuille

## 🎨 Motifs disponibles

- `mountains` - Montagnes (trail)
- `waves` - Vagues (natation)
- `trees` - Sapins (nature)
- `laurel` - Couronne de laurier
- `chevrons` - Chevrons dynamiques
- `running_track` - Piste d'athlétisme

## ⚙️ Contraintes Trotec

Le générateur valide automatiquement:

- ✅ Dimensions min/max (40-120mm)
- ✅ Épaisseur minimum des ponts (2mm)
- ✅ Position du trou ruban (marge 5mm)
- ✅ Taille minimum du texte (3mm)

## 🔮 Évolutions prévues

- [ ] Intégration IA pour suggestions créatives
- [ ] Interface web pour l'équipe commerciale
- [ ] Import de logos SVG
- [ ] Prévisualisation 3D
