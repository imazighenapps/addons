# Bascule SMTP de Secours (smtp_failover_switch)

Configuration SMTP primaire/secondaire avec bascule automatique sur échec, test périodique et journal d'incidents.

## Problème
Quand le SMTP principal tombe, toute la correspondance s'arrête jusqu'à l'intervention manuelle.

## Fonctionnalités
- SMTP primaire et de secours
- Bascule automatique
- Test périodique
- Journal d'incidents
- Retour au primaire contrôlé

## Dépendances
- `mail`
