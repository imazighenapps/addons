# Contrôle des Actions Planifiées (cron_state_watchdog)

Veille sur les actions planifiées : dernière exécution, durée, erreurs, états bloqués, relance contrôlée et journal.

## Problème
Les tâches planifiées échouent ou restent désactivées sans que personne ne s'en aperçoive, jusqu'à l'incident métier.

## Fonctionnalités
- État de chaque tâche planifiée
- Durées et erreurs consignées
- Tâches bloquées signalées
- Relance contrôlée
- Journal des interventions

## Dépendances
- `base`, `mail`
