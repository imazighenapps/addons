# OCR des Reçus (expense_ocr)

OCR des justificatifs de dépenses : extraction (montant, TVA, date, fournisseur), rattachement à la ligne de frais et contrôle de cohérence.

## Problème
Les reçus de notes de frais sont saisis à la main ligne par ligne : friction des employés et erreurs de montants.

## Fonctionnalités
- Extraction du reçu
- Rattachement à la ligne
- Contrôle de cohérence
- File d'exceptions
- Historique

## Dépendances
- `hr_expenses`, `mail`
