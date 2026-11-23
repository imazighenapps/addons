# OCR Factures Fournisseurs (vendor_bill_ocr)

OCR de factures : extraction (montant, TVA, dates, IBAN, référence), correspondance avec commande, contrôle de cohérence avant comptabilisation, apprentissage des formats.

## Problème
Saisir les factures fournisseurs papier/PDF reste manuel ; l'OCR commercial coûte cher et est couplé.

## Fonctionnalités
- Extraction structurée des champs
- Correspondance avec PO
- Contrôle de cohérence
- Apprentissage des formats récurrents
- File de traitement et exceptions

## Dépendances
- `account`, `purchase`, `mail`
