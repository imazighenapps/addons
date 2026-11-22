# Quantités Minimales et Multiples de Campagne (mrp_batch_size_policy)

Politique de taille de lot par référence : minimum de campagne, multiple de lot, lot fixe, lot pour couverture de X jours, application au calcul des besoins.

## Problème
Le MRP propose des quantités MO sans respecter les minimums de campagne ni les multiples de conditionnement : réglages gaspillés et découpages impossibles.

## Fonctionnalités
- Politique de lot par référence
- Application au calcul de besoins
- Rapport des lissages appliqués
- Comparaison coût des lots
- Alerte sur les lots non conformes

## Dépendances
- `mrp`, `mail`
