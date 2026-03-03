======================
Smart Follow-up Reminder
======================

.. image:: https://img.shields.io/badge/version-19.0.1.0.0-blue
.. image:: https://img.shields.io/badge/license-LGPL--3-green

**Automatic reminders on unanswered quotations, with 1-click notifications for salespeople.**

.. contents::
   :local:

Features
--------
* Per-team follow-up delay configuration (1st reminder, 2nd reminder, escalation)
* Computed follow-up status on sale.order (ok / pending / overdue / escalated)
* 1-click follow-up wizard with pre-filled email template
* Kanban board of quotes to follow up, grouped by status
* Daily cron creating Odoo activities and notifying managers on escalation
* Minimum amount threshold to skip reminders on small quotes

Installation
------------
1. Copy the ``smart_followup_reminder`` folder into your Odoo addons path.
2. Update the apps list (Settings > Activate Developer Mode > Update Apps List).
3. Search for "Smart Follow-up Reminder" and click Install.

Configuration
-------------
1. Go to **Sales > Follow-ups > Configuration**.
2. Create a configuration record per sales team.
3. Set the delay thresholds and optionally assign an email template.
4. The cron job runs daily at 8:00 AM. It can be adjusted under Settings > Technical > Automation.

Usage
-----
* Open any quotation in "Sent" state — a follow-up status bar is displayed.
* If status is "Pending" or "Overdue", a **Send Follow-up** button appears.
* Navigate to **Sales > Follow-ups > Quotes to Follow Up** for the full list/kanban.

Known Issues
------------
* The ``days_without_reply`` field detects inbound emails only if the partner sends via the Odoo chatter. External email replies may require Odoo's mail gateway configured.

Changelog
---------
**19.0.1.0.0** (2024-01-01)
  * Initial release.

Credits
-------
* Author: Odoo Experts
* License: LGPL-3
