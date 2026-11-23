# Composants à Délai Long (purchase_long_lead_watch)

Registre des composants à délai long : fenêtre de commande avancée calculée depuis les prévisions, alerte quand la fenêtre s'ouvre et suivi des commandes anticipées.

## Problème
Les composants à délai de 12-40 semaines arrivent après les dates de besoin MRP : les lancements glissent sans que personne ne anticipe.

## Fonctionnalités
- Registre par composant long délai
- Fenêtre de commande calculée
- Alerte d'ouverture de fenêtre
- Commandes anticipées tracées
- Impact du retard sur les MOs

## Dépendances
- `purchase`, `mrp`, `mail`
