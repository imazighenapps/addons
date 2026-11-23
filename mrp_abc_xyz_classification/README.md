# Classification ABC/XYZ des Références (mrp_abc_xyz_classification)

Classification automatique ABC (valeur) et XYZ (régularité de la demande) recalculée périodiquement, avec politique de planification suggérée par classe et suivi des écarts.

## Problème
Les politiques de planification (lot, stock de sécurité, revue) sont définies à l'identique pour toutes les références alors que la valeur et la variabilité diffèrent.

## Fonctionnalités
- Calcul ABC par valeur de consommation
- Calcul XYZ par variabilité
- Politique suggérée par classe (9 cases)
- Recalcul périodique automatique
- Comparaison des classes par période

## Dépendances
- `mrp`, `stock`, `mail`
