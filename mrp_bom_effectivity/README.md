# Effet de Série et Dates d'Effet (mrp_bom_effectivity)

Effet de série : chaque ligne de BOM porte une plage d'effectivité (numéros de série ou dates), les MOs n'assemblent que les lignes actives pour leur position.

## Problème
Un composant remplacé au cours d'une série (design ou fourniture) s'applique à tous les nouveaux MOs sans distinction : les fabrications en cours utilisent le mauvais composant.

## Fonctionnalités
- Plages d'effectivité par ligne de BOM
- Sélection automatique selon la série
- Rapport de conformité par unité
- Transition tracée entre versions
- Contrôle des chevauchements

## Dépendances
- `mrp`, `stock`, `mail`
