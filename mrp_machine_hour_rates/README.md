# Référentiel de Taux Horaires Machines (mrp_machine_hour_rates)

Référentiel de taux horaires par machine : composantes (amortissement, énergie, maintenance, occupation), recalcul périodique et application au coût des opérations.

## Problème
Chiffrer une opération au coût juste exige un taux horaire machine réel (amortissement, énergie, maintenance) que personne ne tient à jour.

## Fonctionnalités
- Décomposition du taux horaire par machine
- Recalcul périodique paramétrable
- Application aux opérations de MO
- Comparaison des machines par coût horaire
- Historique des taux

## Dépendances
- `mrp`, `maintenance`, `mail`
