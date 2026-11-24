# Facturation Multi-Entités Client (split_billing_entities)

Répartition de la commande entre entités du client : lignes affectées à chaque filiale, factures séparées et suivi du CA par entité du groupe.

## Problème
Un devis pour un groupe doit être facturé à plusieurs filiales du client : la répartition se fait à la main et le suivi par entité est impossible.

## Fonctionnalités
- Affectation des lignes par filiale client
- Factures séparées automatiques
- Suivi du CA par entité
- Contrôle de la répartition totale
- Historique par groupe

## Dépendances
- `sale`, `account`, `mail`
