# Autorisation des Remises au POS (pos_discount_authority)

Plafond de remise par profil de caissier : au-delà, validation par un responsable avec code, motif enregistré et journal des remises du point de vente.

## Problème
Au comptoir, un caissier accorde une remise sans autorisation : les marges du point de vente s'érodent sans contrôle ni trace.

## Fonctionnalités
- Plafond de remise par profil
- Validation responsable au comptoir
- Motif enregistré
- Journal des remises du POS
- Rapport des exceptions par caissier

## Dépendances
- `sale`, `point_of_sale`, `mail`
