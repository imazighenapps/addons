# Partner Duplicate Detector for Odoo 19

**Detect and merge duplicate contacts in 2 minutes. Plug & Play — zero configuration required.**

---

## The Problem

Every Odoo database accumulates duplicate contacts over time:
- Imports from Excel or CRM migrations
- Customers registering twice on the portal
- Sales reps creating a contact that already exists
- Vendors added multiple times by different departments

Odoo stores birthdays, emails and phone numbers but **never tells you when two contacts are the same person**. This breaks your reporting, clutters your pipeline, and makes your CRM unreliable.

---

## The Solution — Install & Done

Install this module → **scan runs automatically** → duplicates appear in a list sorted by similarity score. No settings page. No configuration wizard. Just results.

---

## Features

### 🔍 Smart 4-Layer Detection Engine
| Method | What it detects |
|---|---|
| **Exact email match** | Same email address → 100% score |
| **Exact phone match** | Same phone/mobile (normalized) → 95% score |
| **Exact VAT match** | Same tax number → 98% score |
| **Name similarity** | Very similar names (≥85%) → fuzzy score |

### 🗂 Grouped Results
Duplicates are grouped together, not just listed as pairs. If "ACME", "Acme Ltd" and "ACME Corporation" all exist, they appear as one group — not two separate pairs.

### 🔀 Safe One-Click Merge
The merge wizard:
- Lets you choose which record to **keep** (the master)
- Automatically reroutes **Sales Orders, Invoices, Purchase Orders, Deliveries, CRM Leads, Helpdesk Tickets** to the master record
- Moves all **chatter messages** and **followers**
- Fills empty fields on the master from the duplicate (email, phone, address...)
- Posts an audit note in the chatter
- **Archives** (never deletes) the duplicates — safe and reversible

### 📅 Weekly Auto-Scan
A scheduled cron job re-scans your database every week automatically and creates new groups as new duplicates appear.

### 🔔 Smart Button on Partner Form
When a contact has potential duplicates, a **warning badge** appears directly on their form view. One click to see all related groups.

### 🌍 Multilingual
- English ✅
- French ✅ (more languages on request)

---

## Technical Info

- **Odoo version**: 19.0
- **License**: OPL-1
- **Dependencies**: `contacts`, `mail`
- **No external libraries** required
- Compatible with Community and Enterprise editions

---

## Installation

1. Copy the `partner_duplicate_detector` folder to your Odoo `addons` path
2. Update the app list (Settings → Apps → Update App List)
3. Search for "Partner Duplicate Detector" and install
4. Go to **Contacts → Duplicate Detector → Run Scan Now**

The first scan runs automatically. On large databases (10,000+ partners), allow 1–2 minutes.

---

## Changelog

### v19.0.1.0.0 (2025-09)
- Initial release for Odoo 19
- 4-layer detection engine (email, phone, VAT, name similarity)
- One-click merge with full relation rerouting
- Weekly cron auto-scan
- French translation

---

## Support

For bug reports and feature requests, please use the **Odoo Apps reviews** section or contact us directly via our website.
