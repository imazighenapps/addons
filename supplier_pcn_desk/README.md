# Notifications de Fin de Vie Fournisseurs (supplier_pcn_desk)

Registre des notices de fin de vie : annonce tracée avec date d'effet, stock restant et couverture calculée, actions de transition (dernière commande, substitut, requalification) suivies.

## Problème
Les fournisseurs abandonnent des références (PCN/EOL) : l'annonce arrive par email et se perd, la rupture tombe sans plan de transition.

## Fonctionnalités
- Notice EOL tracée avec date d'effet
- Couverture calculée du stock
- Dernière commande recommandée
- Substitut proposé et suivi
- Statistiques de notices par fournisseur

## Dépendances
- `purchase`, `stock`, `mail`
