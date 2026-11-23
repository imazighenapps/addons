# Consolidation des Expéditions (shipment_consolidation_desk)

File de consolidation : expéditions du jour regroupables par destination et fenêtre, déclenchement au seuil de rentabilité, manifeste de groupage généré.

## Problème
Des colis partent séparément le même jour vers la même destination : facturation transport multipliée pour rien.

## Fonctionnalités
- Détection des groupages possibles
- Seuil de déclenchement chiffré
- Manifeste de groupage
- Économie affichée
- Traçabilité des expéditions regroupées

## Dépendances
- `stock`, `sale`, `mail`
