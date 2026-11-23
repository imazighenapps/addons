# Impact des Dérives de Coût sur la Marge (cost_drift_margin)

Poncteur de dérive : chaque hausse de coût d'achat est projetée sur les prix de vente en vigueur, la marge future recalculée et les articles en danger listés pour décision.

## Problème
Les hausses de coûts d'achat passent inaperçues jusqu'à ce que la marge s'effondre : le lien coût d'achat → marge produit n'est jamais regardé.

## Fonctionnalités
- Projection de marge après hausse
- Liste des articles en danger
- Seuils d'alerte de marge
- Décision de prix tracée
- Historique des dérives

## Dépendances
- `purchase`, `sale`, `mail`
