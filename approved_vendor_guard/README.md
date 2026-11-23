# Garde-Fou d'Homologation Article-Fournisseur (approved_vendor_guard)

Liste d'homologation par article : seuls les couples article-fournisseur validés sont commandables, dérogation justifiée sinon, et rapport des tentatives bloquées.

## Problème
N'importe quel fournisseur peut être saisi sur une ligne de commande d'un article homologué : le produit d'un autre fournisseur entre dans le stock sans contrôle.

## Fonctionnalités
- Liste article-fournisseur validée
- Blocage à la ligne de commande
- Dérogation justifiée tracée
- Rapport des tentatives
- Maintenance assistée de la liste

## Dépendances
- `purchase`, `product`, `mail`
