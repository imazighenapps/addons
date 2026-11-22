# Allocation d'Énergie par MO (mrp_energy_allocation)

Allocation des coûts d'énergie aux MOs à partir des relevés de consommation du site et des profils d'usage des machines, sans matériel IoT : répartition par puissance x heures.

## Problème
La facture d'énergie du site reste un coût global : impossible de dire combien coûte l'énergie dans le coût de revient d'une référence.

## Fonctionnalités
- Répartition par puissance et heures machine
- Import des factures d'énergie
- Coût énergie par MO et par référence
- Suivi du coût par kWh produit
- Rapport mensuel d'attribution

## Dépendances
- `mrp`, `account`, `maintenance`, `mail`
