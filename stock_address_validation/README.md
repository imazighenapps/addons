# Validation des Adresses (stock_address_validation)

Validation des adresses : contrôle de format et complétude, géolocalisation optionnelle, alerte avant confirmation et journal des corrections.

## Problème
Les adresses de livraison mal formées font échouer des livraisons entières : personne ne vérifie avant l'étiquette.

## Fonctionnalités
- Contrôle de format/complétude
- Alerte avant confirmation
- Géolocalisation optionnelle
- Journal des corrections
- Statistiques d'échecs évités

## Dépendances
- `sale`, `stock`, `mail`
