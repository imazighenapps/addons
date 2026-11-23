# Contrôle des Modifications Post-Confirmation (po_change_control)

Versionnage des modifications : chaque changement après confirmation crée une révision datée, exige un nouvel accusé du fournisseur et trace l'écart accepté ou contesté.

## Problème
Modifier une commande déjà confirmée par le fournisseur se fait sans nouveau feu vert : quantités et dates divergent sans que personne ne sache qui a accepté quoi.

## Fonctionnalités
- Révision datée à chaque changement
- Nouvel accusé exigé
- Diff entre versions
- Écart accepté ou contesté tracé
- Historique complet

## Dépendances
- `purchase`, `mail`
