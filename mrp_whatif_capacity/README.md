# Simulateur de Scénarios de Capacité (mrp_whatif_capacity)

Simulateur what-if : injection d'un volume supplémentaire dans le planning, recalcul de la charge par poste, date de fin projetée et besoins en ressources additionnels.

## Problème
Accepter un gros contrat ou ajouter une équipe se décide sans voir l'effet sur la charge : les arbitrages se font à l'aveugle.

## Fonctionnalités
- Injection de scénarios (volumes, délais)
- Recalcul de charge sans toucher les MOs réelles
- Comparaison de scénarios côte à côte
- Besoins en ressources additionnels estimés
- Rapport de décision PDF

## Dépendances
- `mrp`, `mail`
