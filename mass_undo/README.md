# Annulation en Masse (mass_undo)

Instantanés avant actions en masse : capture des champs modifiés, retour arrière sélectif, journal complet et rapport.

## Problème
Une modification en masse erronée est définitive : restauration de sauvegarde seule, catastrophique.

## Fonctionnalités
- Capture avant action
- Retour arrière sélectif
- Journal complet
- Rapport
- Coordination avec MassActionGuard

## Dépendances
- `base`, `mail`
