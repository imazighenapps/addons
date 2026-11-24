# Aiguillage Automatique des Commandes (order_routing_rules)

Aiguillage par règles : région, canal, montant ou famille renvoient chaque commande à l'équipe et au propriétaire adéquats, avec file d'attente par équipe et statistiques de traitement.

## Problème
Les commandes arrivent toutes dans une file unique : l'équipe de nuit traite celles du sud, les urgences attendent derrière des dossiers simples.

## Fonctionnalités
- Règles d'aiguillage configurables
- Propriétaire assigné automatiquement
- Files d'attente par équipe
- Statistiques de traitement par équipe
- Re-routage justifié

## Dépendances
- `sale`, `mail`
