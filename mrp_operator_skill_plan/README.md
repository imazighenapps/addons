# Planification Sensible aux Habilitations (mrp_operator_skill_plan)

Affectation des opérations restreinte aux opérateurs dont l'habilitation est valide pour le poste, avec alerte et proposition de remplacement habilité.

## Problème
Le planning affecte des opérations à des opérateurs non habilités sur la machine, causant retards et incidents qualité.

## Fonctionnalités
- Matrice habilitation x machine
- Blocage ou alerte à l'affectation
- Recherche d'opérateur habilité disponible
- Suivi des habilitations expirées
- Historique des affectations

## Dépendances
- `mrp`, `hr`, `mail`
