# Plan d'Arrivage ASN (stock_asn_receiving)

Import des avis d'expédition : lecture du fichier fournisseur, création des réceptions attendues avec volumes, planning des créneaux et statut de chaque arrivage.

## Problème
Les warehouses reçoivent des avis d'expédition fournisseurs (ASN) par email/Excel et les retapent à la main pour planifier les quais.

## Fonctionnalités
- Import ASN CSV/Excel
- Création des réceptions attendues
- Planning de charge des quais
- Suivi des statuts d'arrivage
- Volumétrie par réception

## Dépendances
- `stock`, `purchase`, `mail`
