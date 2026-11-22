# Pack Fiscal Tunisie (tn_fiscal_pack)

Pack fiscal TN : plan PCN assisté, journaux fiscaux, retenue à la source et suivi de la facturation électronique TPAE.

## Problème
La Tunisie impose le PCN, la TVA collectée/déductible détaillée et la facturation électronique en déploiement.

## Fonctionnalités
- Mapping PCN
- Journaux fiscaux
- Retenue à la source
- Suivi TPAE

## Dépendances
- `account`, `mail`

## Notes QA
Génération/export/validation et journal de conformité testables localement. Les transmissions API/certificats gouvernementaux externes ne sont pas effectuées sur la VM QA.
