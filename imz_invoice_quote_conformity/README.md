# Conformité Facture-Devis (invoice_quote_conformity)

Contrôle de conformité à la facturation : comparaison ligne à ligne avec le devis confirmé, alerte des écarts, justification obligatoire avant validation.

## Problème
La facture s'écarte du devis confirmé (prix, quantités, frais) sans que personne ne le voie : conflits clients et pertes silencieuses.

## Fonctionnalités
- Comparaison ligne à ligne devis/facture
- Alerte des écarts de prix et quantité
- Justification obligatoire avant validation
- Rapport des écarts par vendeur
- Journal de conformité

## Dépendances
- `sale`, `account`, `mail`
