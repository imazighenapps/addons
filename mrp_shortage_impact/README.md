# Impact des Pénuries Composants (mrp_shortage_impact)

Propagation des pénuries : liste des MOs bloquées par composant manquant, nouvelle date de fin calculée, impact sur les commandes clients et actions de dépannage suggérées.

## Problème
Quand une réception glisse, personne ne sait quelles MOs sont impactées et de combien de jours les livraisons clients décalent.

## Fonctionnalités
- Cartographie MOs bloquées par composant
- Re-dating automatique des dates de fin
- Impact remonté aux commandes clients
- Suggestions de substitution ou d'échange
- Alerte quotidienne aux planificateurs

## Dépendances
- `mrp`, `stock`, `sale`, `mail`
