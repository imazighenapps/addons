# Calendrier de Capacité par Équipe (mrp_shift_capacity_calendar)

Calendrier de capacité par équipe et par site : heures disponibles planifiées par semaine, fermetures, jours fériés locaux et semaines incomplètes intégrées au calcul de charge.

## Problème
Odoo calcule la capacité des postes de charge sur une base horaire théorique qui ignore les horaires d'équipe, les jours fériés et les fermetures d'atelier.

## Fonctionnalités
- Calendriers d'équipe par site
- Semaine de référence avec heures réelles
- Fermetures et jours fériés intégrés
- Capacité reportée automatiquement
- Comparaison capacité théorique vs planifiée

## Dépendances
- `mrp`, `resource_calendar`, `mail`
