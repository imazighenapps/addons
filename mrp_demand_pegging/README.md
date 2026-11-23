# Pegging Multi-Niveaux (mrp_demand_pegging)

Pegging multi-niveaux : chaque composant des MOs est relié à la commande client d'origine à travers tous les niveaux de nomenclature, avec vue inversée.

## Problème
Impossible de savoir quelle commande client a consommé quel composant acheté : les arbitrages en pénurie se font à l'aveugle.

## Fonctionnalités
- Lien composant → commande client multi-niveaux
- Vue inversée par commande
- Recherche par lot de composant
- Allocation en cas de pénurie
- Rapport d'allocation par client

## Dépendances
- `mrp`, `sale`, `stock`, `mail`
