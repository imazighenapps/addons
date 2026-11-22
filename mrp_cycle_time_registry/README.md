# Référentiel de Temps de Cycle (mrp_cycle_time_registry)

Référentiel centralisé de temps de cycle par combinaison produit+opération+machine, sources multiples (standard, chronométrage, réalisé) et propagation contrôlée aux gammes.

## Problème
Les temps d'opération saisis dans les gammes sont des ordres de grandeur approximatifs, souvent jamais revus : plannings faussés et coûts erronés.

## Fonctionnalités
- Temps par produit/opération/machine
- Sources hiérarchisées (standard, étude, réalisé)
- Propagation contrôlée aux gammes
- Comparaison standard vs réalisé
- Alerte sur les temps obsolètes

## Dépendances
- `mrp`, `mail`
