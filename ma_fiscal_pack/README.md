# Pack Fiscal Maroc (ma_fiscal_pack)

Pack fiscal MA : plan comptable CGNC assisté, journal de TVA par régime, retenue à la source, export des relevés et calendrier des échéances DGI.

## Problème
Les entreprises marocaines gèrent la déclaration TVA, la retenue à la source et le reversement depuis Excel avec des formats CMI/DSN propres au Maroc.

## Fonctionnalités
- Mapping CGNC
- Journal TVA par régime
- Retenue à la source
- Calendrier DGI
- Exports de déclarations

## Dépendances
- `account`, `mail`

## Notes QA
Génération/export/validation et journal de conformité testables localement. Les transmissions API/certificats gouvernementaux externes ne sont pas effectuées sur la VM QA.
