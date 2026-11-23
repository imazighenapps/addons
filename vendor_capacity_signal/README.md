# Capacités Hebdomadaires Fournisseurs (vendor_capacity_signal)

Signal de capacité hebdomadaire : le fournisseur confirme chaque semaine ses capacités par famille, la projection des besoins est comparée et les tensions remontent tôt.

## Problème
Les plans de charge achats ignorent la capacité réelle des fournisseurs : on commande ce qu'ils ne peuvent pas produire cette semaine.

## Fonctionnalités
- Déclaration hebdomadaire de capacité
- Comparaison besoins vs capacités
- Alerte de tension à 4 semaines
- Historique des signaux
- Filtre des commandes à risque

## Dépendances
- `purchase`, `mail`
