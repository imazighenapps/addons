# Screening des Fournisseurs sur Listes de Contrôle (supplier_screening_guard)

Screening interne : listes importées (sanctions, embargos, blacklist interne), contrôle à la création et à la commande, alerte bloquante avec trace datée et réévaluation programmée.

## Problème
Les listes de sanctions et d'embargos évoluent : vérifier manuellement chaque fournisseur à chaque commande est irréaliste, et l'oubli coûte cher.

## Fonctionnalités
- Import des listes de contrôle
- Contrôle à la création et à la commande
- Alerte bloquante tracée
- Réévaluation programmée
- Journal d'audit de conformité

## Dépendances
- `purchase`, `mail`
