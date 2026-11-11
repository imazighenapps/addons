# -*- coding: utf-8 -*-
{
    'name': 'VendorReturn',
    'version': '20.0.1.0.0',
    'summary': 'Return rejected goods to your supplier with the trace, the transport and the credit note you expect back.',
    'description': '''VendorReturn - Rejected Goods, Credits Back
===========================================
Rejected goods leave the dock with a promise: the supplier will take them
back, the carrier will move them and a credit note will follow. In practice
the parcel has no trace, the transport reference lives in an email and the
expected credit disappears before anyone asks for it. Weeks later the
purchasing team pays the original invoice and the claim is lost.

VendorReturn keeps one Odoo case per return to vendor: who receives the
goods back, which items are rejected, how the parcel travels and which
credit note you expect. Each line records the product, the quantity and the
reason, so the decision to return is documented on the case itself. The
transport reference and the expected credit amount stay visible until the
credit is received and the case is closed. A credits-awaited screen shows
every return still waiting for money back instead of buried in a mailbox.
The case the buyer needs is the one the module already holds.

* A return case per supplier with reference and company.
* Return lines with product, quantity and rejection reason.
* Transport trace kept on the case for every parcel.
* The expected credit amount recorded and followed to receipt.
* A credits-awaited screen for returns still waiting for money.
* Decision states from draft to sent, credited and closed.
* A received credit requires a positive expected amount.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/rvd_return_0_views.xml',
        'views/rvd_return_line_1_views.xml',
        'views/rvd_return_pending_2_views.xml',
        'views/menus.xml',
        'views/rvd_return_pending_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
