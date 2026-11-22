# Séquences d'Appel JIT (mrp_jit_sequences)

Gestion des séquences d'appel : réception de la séquence, planification des MOs dans l'ordre, contrôle de conformité de la séquence à l'expédition.

## Problème
Les clients en flux tiré envoient des séquences d'appel (ordre exact de livraison) : la production ne suit pas la séquence et les pénalités s'enchaînent.

## Fonctionnalités
- Réception des séquences d'appel
- Planification dans l'ordre demandé
- Conformité de la séquence à l'expédition
- Alerte de déséquilibre de cadence
- Historique des séquences livrées

## Dépendances
- `mrp`, `sale`, `stock`, `mail`
