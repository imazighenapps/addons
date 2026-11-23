# Application de Traductions en Masse (translation_batch_apply)

Import de traductions en masse par module et langue depuis CSV, avec essai à blanc, rollback et journal des termes remplacés.

## Problème
Appliquer une glossaire client sur un module exige des manipulations ir.translation manuelles et risquées.

## Fonctionnalités
- Import CSV par module/langue
- Essai à blanc
- Rollback des remplacements
- Journal des termes
- Glossaire réutilisable

## Dépendances
- `base`, `mail`
