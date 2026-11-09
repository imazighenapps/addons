# -*- coding: utf-8 -*-
{
    'name': 'SiteAudit',
    'version': '19.0.1.0.0',
    'summary': 'Build reusable site inspection templates with weighted points, run an audit from a template in one click and let the score, the failed points and the trend do the talking.',
    'description': '''SiteAudit - Templates That Score A Site
=======================================
Site inspections are filled once in a spreadsheet and never rebuilt.
Two inspectors bring different templates and weight the points
differently, so two visits of the same site cannot be compared, the
score means whatever the pen wants it to mean, and the proof that the
fixes worked stays anecdotal.

SiteAudit builds reusable inspection templates made of weighted points.
An audit is instantiated from its template in one click, every point is
scored on site in the form against its weight, and the global score is
computed - without scores, the audit cannot be closed. Each point turns
passed or failed at the threshold of its weight, the failed points have
their own screen, and a reset rebuilds the file on its template so a
second visit starts from the same basis. Nothing to install beyond the
base, nothing to configure before the first template.

* Inspection templates with scored points and weights.
* An audit instantiated from a template in one click.
* Every point scored in the form, out of its weight.
* A weighted global score computed and stored.
* No closing while points stay unscored.
* A failed-points screen and a reset on the template.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Field Service',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/site_audit_0_views.xml',
        'views/site_audit_template_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
