# Routeur d'Erreurs (error_router_notify)

Groupement des erreurs par signature, routage vers l'équipe, silencieux des erreurs connues, historique d'incidents et taux d'apparition.

## Problème
Les tracebacks apparaissent dans les logs sans alerte : les erreurs récurrentes ne remontent pas à l'équipe.

## Fonctionnalités
- Groupement par signature
- Routage vers l'équipe
- Silencieux des erreurs connues
- Taux d'apparition
- Historique d'incidents

## Dépendances
- `base`, `mail`
