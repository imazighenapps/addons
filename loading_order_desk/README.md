# Ordres de Chargement Multi-Livraisons (loading_order_desk)

Ordre de chargement : séquence chargée en inverse des arrêts, contrôle de chaque palette au chargement, scellé enregistré et départ validé.

## Problème
Charger dans le désordre oblige à vider la moitié du camion à chaque arrêt : temps perdu, colis oubliés à l'arrière.

## Fonctionnalités
- Séquence en inverse des arrêts
- Contrôle palette par palette
- Scellé et départ validés
- Colis restants signalés
- Historique des erreurs de chargement

## Dépendances
- `stock`, `sale`, `mail`
