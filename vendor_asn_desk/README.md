# Avis d'Expédition Fournisseur (vendor_asn_desk)

Le fournisseur déclare un avis d'expédition (ASN) par commande : lignes, quantités, transporteur, date d'arrivée ; l'entrepôt reçoit un plan de réception prêt avant le camion.

## Problème
Les réceptions sont aveugles : le magasin découvre les volumes et le contenu d'un camion à son arrivée, sans préparation possible.

## Fonctionnalités
- ASN déclaré par le fournisseur
- Plan de réception pré-généré
- Contrôle ASN vs commande
- Alerte d'ASN manquant avant échéance
- Statistiques de couverture ASN

## Dépendances
- `purchase`, `stock`, `mail`
