# Roll-Up Multi-Niveaux du Coût Standard (mrp_cost_rollup_multilevel)

Roll-up multi-niveaux : calcul du coût standard de chaque sous-ensemble depuis ses composants et opérations, recalcul en cascade avec rapport des écarts avant/après.

## Problème
Dans les nomenclatures profondes, le coût standard des sous-ensembles n'est pas recalculé en cascade : les coûts de niveaux intermédiaires divergent.

## Fonctionnalités
- Recalcul en cascade des nomenclatures
- Rapport avant/après par niveau
- Exécution planifiée ou manuelle
- Alerte sur les écarts anormaux
- Journal des recalculs

## Dépendances
- `mrp`, `account`, `mail`
