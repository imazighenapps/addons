# Inde GST e-Invoice (in_gst_einvoice)

Connecteur IRN : génération JSON GST, obtention IRN/QR, re-récupération et gestion des cancelations.

## Problème
L'Inde impose l'e-invoicing GST (IRN via GSP) au-delà des seuils de chiffre d'affaires.

## Fonctionnalités
- JSON GST conforme
- IRN + QR
- Requête IRN par IRN (get)
- Annulation avec fenêtre réglementaire

## Dépendances
- `account`, `mail`

## Notes QA
Génération/export/validation et journal de conformité testables localement. Les transmissions API/certificats gouvernementaux externes ne sont pas effectuées sur la VM QA.
