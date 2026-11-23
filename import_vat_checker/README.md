# Contrôle TVA Import (import_vat_checker)

Contrôleur de TVA import : croisement des déclarations d'importation (pièces douanières jointes) avec les écritures de TVA, écarts signalés et justification.

## Problème
La TVA à l'import (auto-liquidée) doit être déclarée ET déduite : les écarts entre déclarations et pièces douanières coûtent des redressements.

## Fonctionnalités
- Croisement pièces douanières/écritures
- Écarts signalés et justifiés
- Tableau de bord TVA import
- Journal de conformité

## Dépendances
- `account`, `mail`
