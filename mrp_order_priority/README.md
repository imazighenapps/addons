# Priorisation Commerciale des MOs (mrp_order_priority)

Moteur de priorité par MO : score calculé depuis les règles (pénalités, catégorie client, marge, retard) qui réordonne la file d'atelier et informe le lancement.

## Problème
La file des MOs est traitée en ordre d'arrivée alors que les enjeux clients diffèrent : pénalités, clients clés, marges.

## Fonctionnalités
- Règles de priorité configurables
- Score par MO et tri de la file
- Justification du score visible
- Blocage de MOs en priorité maximale
- Historique des réordonnancements

## Dépendances
- `mrp`, `sale`, `mail`
