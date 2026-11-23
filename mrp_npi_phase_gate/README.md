# Industrialisation NPI Phase-Gate (mrp_npi_phase_gate)

Phase-gate NPI : étapes (échantillon, présérie, série) avec critères de sortie (BOM figé, FAI validé, docs clients), passage de phase tracé et bloquant.

## Problème
Passer d'un prototype à la série se fait sans étapes formelles : des produits arrivent en série sans BOM propre, ni gamme validée, ni FAI.

## Fonctionnalités
- Phases avec critères de sortie
- Passage de phase bloquant
- Checklist par phase (BOM, FAI, docs)
- Statut NPI par projet
- Historique des gate

## Dépendances
- `mrp`, `project`, `quality`, `mail`
