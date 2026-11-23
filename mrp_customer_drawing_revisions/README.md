# Révisions de Plans et Specs Client (mrp_customer_drawing_revisions)

Registre de révisions client : chaque révision par référence avec date, pièce jointe, réception confirmée par l'atelier et blocage de MOs non alignées.

## Problème
Les clients envoient des révisions de plans et specs par email : l'atelier fabrique parfois sur une révision obsolète.

## Fonctionnalités
- Révision par référence avec pièce jointe
- Acquittement par l'atelier
- Alerte sur les MOs obsolètes
- Historique des révisions par client
- Différences décrites entre révisions

## Dépendances
- `mrp`, `sale`, `mail`
