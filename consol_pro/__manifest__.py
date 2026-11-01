# -*- coding: utf-8 -*-
{
    'name': 'ConsolPro',
    'version': '18.0.1.0.0',
    'summary': 'Aggregate the posted balances of several companies by account code, zero the tagged intercompany lines and lock the consolidation once it is posted.',
    'description': '''ConsolPro - Multi-Company Consolidation and Eliminations
========================================================
Groups that run one Odoo database per country finalize the books twice:
every ledger balances, but nobody can answer the two questions of a group
closing without another week of spreadsheets. What does the group look
like once the ledgers are put together, and how much of the turnover is
internal and must disappear? The consolidating accountant rekeys each
company balances into Excel, retypes them in the group chart and hopes
both versions agree before the closing meeting.

ConsolPro takes over the mechanical part of the consolidation inside
Odoo. Pick the companies and the period, run the compute, and every
posted journal entry line of those companies is aggregated by company
and by account code into one consolidation line per account, with its
debit, credit and net balance. An account that nets to zero over the
period is dropped, so the extraction only carries live balances. Tag
the intercompany lines with a mapping reference, run the elimination,
and the tagged lines are flagged and zeroed out of the run totals. Post
the run to freeze the whole consolidation: compute and elimination are
refused afterwards. Reset a run to draft when the ledger was corrected,
because the lines are rebuilt from scratch on every compute while a
mapping already typed on a line is preserved, so the tags survive. The
module works with several companies or with the current one alone,
traces every step in the chatter and needs no Enterprise dependency.

* One consolidation line per company and account code, aggregated from
  the posted entries of the selected companies and period.
* Debit, credit and net balance per line with stored run totals.
* Accounts that net to zero over the period are skipped automatically.
* Mapping reference on each line to tag the intercompany balances.
* One-click elimination zeroes and flags the mapped lines.
* Posting locks the run: compute and elimination are refused afterwards.
* Reset to draft clears the lines and a recompute always reflects the
  corrected ledger while preserving the mappings already typed.
* Multi-company, works with the current company alone, no Enterprise
  dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 179.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/consol_run_0_views.xml',
        'views/consol_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
