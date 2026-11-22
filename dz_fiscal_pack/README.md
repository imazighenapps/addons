# Pack Fiscal Algérie (dz_fiscal_pack)

Pack fiscal DZ : journal G50 mensuel (TVA/TAP/retenues), calendrier des échéances DGI, plan SCF assisté, documents fiscaux normalisés (facture avec NIF/NIU/RC) et états de conformité.

## Problème
Les entreprises algériennes gèrent G50, la retenue à la source (TAP, IRG/IS), les journaux fiscaux et la facturation depuis des classeurs Excel.

## Fonctionnalités
- Journal G50 mensuel détaillé
- Calendrier fiscal DGI
- Plan SCF assisté
- Facture conforme (NIF/NIU/RC, timbre)
- États de retenue à la source

## Dépendances
- `account`, `mail`

## Notes QA
Génération/export/validation et journal de conformité testables localement. Les transmissions API/certificats gouvernementaux externes ne sont pas effectuées sur la VM QA.
