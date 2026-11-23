# Scanner d'Intégrité du Stock (stock_integrity_scanner)

Scanner périodique des anomalies de stock : liste d'autocontrôles (négatifs, incohérences lot/location, mouvements sans origine, garde-fous à la validation) avec rapport quotidien et plan de correction.

## Problème
Les stocks s'abîment silencieusement : quantités négatives, mouvements orphelins, emplacements surchargés, réservations fantômes se découvrent à la clôture.

## Fonctionnalités
- Rapport quotidien d'anomalies
- Garde-fou contre le stock négatif
- Détection des mouvements orphelins
- Contrôles de cohérence location/lot
- Suivi des corrections

## Dépendances
- `stock`, `mail`
