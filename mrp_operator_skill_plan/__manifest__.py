# -*- coding: utf-8 -*-
{
    "name": "Mrp Operator Skill Plan",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Give production teams real-time control over capacity, costs and delivery dates.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mrp", "hr", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_operator_skill_plan_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
