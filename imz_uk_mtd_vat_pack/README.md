# MTD VAT Royaume-Uni (uk_mtd_vat_pack)

Pack MTD : calcul du VAT return aux 9 boxes, transmission API HMRC, historique des soumissions et audit trail.

## Problème
Les entreprises britanniques doivent soumettre la TVA via Making Tax Digital (liens API HMRC, données digitalisées).

## Fonctionnalités
- VAT return 9 boxes calculé
- Transmission API HMRC
- Historique des soumissions
- Journal d'audit MTD

## Dépendances
- `account`, `mail`

## Notes QA
Génération/export/validation et journal de conformité testables localement. Les transmissions API/certificats gouvernementaux externes ne sont pas effectuées sur la VM QA.
