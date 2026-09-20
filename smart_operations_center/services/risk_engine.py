from odoo import api, models


class SmartOperationsRiskEngine(models.AbstractModel):
    _name = 'smart.operations.risk.engine'
    _description = 'Operational Risk Engine'

    @api.model
    def calculate(
        self,
        delay_days=0.0,
        impact=0.0,
        customer_count=0,
        dependency_count=0,
        rule_weight=5.0,
        deadline_days=0.0,
    ):
        """Return an explainable risk score in the 0-100 range.

        ``deadline_days`` is positive when a deadline is approaching/overdue and
        is kept as a separate factor so custom integrations can contribute it.
        """
        delay_score = min(max(delay_days, 0.0) * 8.0, 30.0)
        deadline_score = min(max(deadline_days, 0.0) * 5.0, 15.0)
        impact_score = min(max(impact, 0.0) / 1000.0, 25.0)
        customer_score = min(max(customer_count, 0) * 4.0, 20.0)
        dependency_score = min(max(dependency_count, 0) * 3.0, 15.0)
        weight_score = min(max(rule_weight, 0.0), 10.0)
        raw = delay_score + deadline_score + impact_score + customer_score + dependency_score + weight_score
        score = min(round(raw, 2), 100.0)
        return score, {
            'delay': delay_score,
            'deadline': deadline_score,
            'business_impact': impact_score,
            'customer_impact': customer_score,
            'dependency': dependency_score,
            'rule_weight': weight_score,
        }
