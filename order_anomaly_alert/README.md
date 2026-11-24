# Alerte de Commande Atypique (order_anomaly_alert)

Alerte d'atypie à la commande : comparaison à l'historique client (volume, panier, produit), seuils configurables, vérification exigée avant confirmation.

## Problème
Une commande 10 fois plus grande ou sur un produit jamais acheté passe sans vérification : erreurs de saisie, achats déraisonnés et litiges suivent.

## Fonctionnalités
- Comparaison à l'historique client
- Seuils d'atypie configurables
- Vérification exigée avant confirmation
- Motif de validation enregistré
- Rapport des alertes et issues

## Dépendances
- `sale`, `mail`
