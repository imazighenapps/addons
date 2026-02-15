# AI-Powered Inventory Forecasting - Odoo 18

Module complet de prévision intelligente des stocks utilisant le Machine Learning.

## Installation

### 1. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 2. Copier le module dans addons

```bash
cp -r im_ai_inventory_forecast /path/to/odoo/addons/
```

### 3. Activer le module

1. Redémarrer Odoo
2. Aller dans Apps
3. Mettre à jour la liste des applications
4. Rechercher "AI-Powered Inventory Forecasting"
5. Cliquer sur "Installer"

## Configuration

1. Aller dans **Inventaire → AI Forecasting → Configuration**
2. Créer une nouvelle configuration
3. Choisir l'algorithme (Ensemble recommandé)
4. Définir l'horizon de prévision (90 jours par défaut)
5. Activer la saisonnalité et les jours fériés
6. Sauvegarder

## Utilisation Rapide

### Générer des prévisions

1. Aller dans **Inventaire → AI Forecasting → Dashboard**
2. Utiliser le wizard "Generate Forecasts"
3. Sélectionner les produits et entrepôts
4. Cliquer sur "Generate"

### Consulter les alertes

1. Aller dans **Inventaire → AI Forecasting → Alerts**
2. Les alertes critiques apparaissent en rouge
3. Cliquer sur une alerte pour voir les détails
4. Utiliser "Create PO" pour créer un bon de commande automatiquement

### Optimiser les règles de réapprovisionnement

1. Aller dans **Inventaire → AI Forecasting → Reorder Rules**
2. Les règles optimisées sont calculées automatiquement
3. Comparer avec les règles actuelles
4. Cliquer sur "Apply to Odoo Rules" pour appliquer

## Algorithmes Disponibles

- **Prophet**: Meilleur pour les produits saisonniers
- **ARIMA**: Rapide, pour les produits stables
- **Ensemble**: Combine les deux (recommandé)

## Tâches Automatiques

Le module configure automatiquement les crons suivants:
- Génération quotidienne des prévisions (2h du matin)
- Vérification horaire des alertes
- Calcul quotidien des règles de réapprovisionnement (3h du matin)
- Nettoyage mensuel des anciennes données

## Support

Email: support@ai-inventory-forecast.com
Documentation: https://www.ai-inventory-forecast.com/docs

## Licence

OPL-1 (Odoo Proprietary License v1.0)
