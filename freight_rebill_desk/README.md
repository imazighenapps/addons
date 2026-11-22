# Refacturation du Transport aux Clients (freight_rebill_desk)

Moteur de refacturation : règles par zone, poids et incoterm, calcul depuis l'expédition réelle, ajustement à la facture et rapprochement coût/facturé.

## Problème
Les frais de transport réels ne remontent jamais exactement dans la facture client : grille approximative, pertes sèches ou sur-facturation contestée.

## Fonctionnalités
- Règles par zone et poids
- Calcul depuis l'expédition réelle
- Application à la facture
- Rapprochement coût/facturé
- Écart de marge transport mesuré

## Dépendances
- `sale`, `stock`, `account`, `mail`
