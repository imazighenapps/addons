# Plans d'Échantillonnage AQL (quality_aql_sampling)

Plans d'échantillonnage ISO 2859 : niveau d'inspection, taille de lot → échantillon et AC/RE calculés automatiquement, verdict par lot et registre des décisions.

## Problème
Les quantités à contrôler sur les réceptions et expéditions sont décidées à l'instinct, sans plan normalisé : audits non défendables.

## Fonctionnalités
- Tables ISO 2859 intégrées
- Niveaux spéciaux et switched rules
- AC/RE calculés par lot
- Verdict tracé sur la réception ou l'expédition
- Historique des plans appliqués

## Dépendances
- `quality`, `stock`, `mail`
