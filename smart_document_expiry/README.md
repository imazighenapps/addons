# Smart Document Expiry Tracker — Odoo 19

**Automatically track, alert, and manage expiring documents across your entire organization.**

---

## 🎯 Overview

Smart Document Expiry Tracker is a production-ready Odoo 19 module that gives HR managers, fleet administrators, procurement officers, and HSE teams complete visibility over every document that carries an expiry date — work permits, visas, vehicle registrations, equipment certifications, vendor licenses, insurance policies, and more.

Never be caught off-guard by an expired document again.

---

## ✅ Features

### 🗂 Universal Document Management
Attach any document to:
- **Persons** — work permits, visas, driving licenses, medical certificates, safety training
- **Vendors / Partners** — trade licenses, insurance certificates, vendor contracts
- **Vehicles** — registrations, insurance, technical inspections
- **Equipment** — calibration certificates, warranties, equipment certifications
- **Other** — ISO certificates, site permits, custom entity types

### 🔔 Configurable Email Alerts
- Three-tier alert schedule per document type: **90 days → 30 days → 7 days**
- Alerts sent to the designated responsible person + optional CC list
- **Escalation alert**: if a document expires and hasn't been renewed after N days, the system escalates automatically

### 📊 Real-Time Dashboard
- Live compliance overview with animated ring chart
- Color-coded stat boxes: 🟢 Valid / 🟠 Expiring Soon / 🔴 Expired
- "Upcoming Expirations" table with 1-click navigation
- Graph and Pivot analytics views

### 📋 Kanban & List Views
- Full Kanban view grouped by status with color borders
- Rich list view with row decoration and inline Renew button
- Powerful search & filter: by status, entity type, time window, responsible

### 🔄 Renewal & History
- One-click renewal wizard — creates a new document, archives the old one
- Full renewal chain traceable from any document
- Optional: require an attachment when renewing (per document type)

### 📄 PDF Compliance Report
- Printable full compliance report with summary stats + full document table
- Color-coded rows, sortable by expiry date
- Available as a Print action from any document list

### 🏢 Smart Buttons on Related Records
Every person, vendor, vehicle, and equipment form shows:
- Smart button with document count
- Red badge if expired documents exist
- Embedded documents tab with compliance score

### 🔐 Multi-company & Role-based Security
- **User**: can read/write/create documents
- **Manager**: can configure document types, delete, access all alert logs
- Full multi-company isolation via record rules

---

## 🛠 Installation

1. Copy the `smart_document_expiry` folder to your Odoo `addons` directory
2. Restart the Odoo server
3. Enable **Developer Mode** (Settings → Activate Developer Mode)
4. Go to **Apps → Update Apps List**
5. Search for "Smart Document Expiry" and click **Install**

### Dependencies
This module only requires:
- `base` (always present)
- `mail` (Messaging)
- `web` (Frontend)

No dependency on `hr`, `fleet`, `stock`, `maintenance`, or `portal` modules.

---

## ⚙️ Configuration

### 1. Document Types
Go to **Document Expiry → Configuration → Document Types** to:
- Create custom document types for your industry
- Set per-type alert schedules (override the global defaults)
- Enable/disable attachment requirement on renewal

### 2. Scheduled Actions
Two cron jobs are auto-configured at install time:
- **Send Expiry Alerts** — runs daily at 07:00, sends all pending notifications
- **Refresh States** — runs daily at 00:05, recalculates valid/expiring/expired status

Adjust via **Settings → Technical → Automation → Scheduled Actions**.

### 3. Email Configuration
Alerts use standard Odoo mail templates. Customize templates under:
**Settings → Technical → Email → Templates** (search "Document Expiry")

---

## 📁 Module Structure

```
smart_document_expiry/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── document_expiry.py       ← Core model (tracking, alerts, renewal)
│   ├── document_type.py         ← Configurable document categories
│   ├── document_person.py       ← Standalone person/employee model
│   ├── document_partner.py      ← Standalone vendor/partner model
│   ├── document_vehicle.py      ← Standalone vehicle model
│   └── document_equipment.py    ← Standalone equipment model
├── wizards/
│   └── document_renew_wizard.py ← Renewal workflow
├── views/
│   ├── document_expiry_views.xml     ← Form / List / Kanban / Search
│   ├── document_type_views.xml
│   ├── document_dashboard_views.xml  ← Graph + Pivot
│   ├── document_person_views.xml
│   ├── document_partner_views.xml
│   ├── document_vehicle_views.xml
│   ├── stock_equipment_views.xml
│   └── menu_views.xml
├── data/
│   ├── document_type_data.xml    ← 14 pre-configured document types
│   ├── mail_template_data.xml    ← 4 HTML email templates
│   └── ir_cron_data.xml          ← 2 scheduled actions
├── demo/
│   └── demo_data.xml             ← 20 realistic demo records
├── security/
│   ├── ir.model.access.csv
│   └── document_expiry_security.xml
├── controllers/
│   └── main.py                   ← JSON dashboard endpoint
├── report/
│   ├── document_expiry_report.xml
│   └── document_expiry_report_templates.xml
└── static/
    ├── description/
    │   └── index.html            ← Odoo Apps store page
    └── src/
        ├── css/document_expiry.css
        ├── xml/document_expiry_dashboard.xml   ← OWL dashboard template
        └── js/document_expiry_widget.js        ← OWL dashboard component
```

---

## 📦 Demo Data

Install with **Load Demo Data** enabled to get 20 realistic records across all entity types and statuses:
- **Valid** documents (several entities, long remaining validity)
- **Expiring Soon** documents (5, 8, 12, 18, 20, 28 days remaining)
- **Expired** documents (5 to 35 days past deadline)
- **Renewed** documents with full renewal chain (old → new linked records)
- **Other** entity type example (ISO certificate)

---

## 🔮 Roadmap / Suggested Enhancements

- **Bulk import** via Excel/CSV for migrating existing document data
- **QR code** on printed reports for quick document verification
- **Mobile push notifications** (Odoo mobile app integration)
- **Document request workflow** — HR can request missing docs from employees
- **Vendor portal** — vendors upload their own compliance documents
- **API endpoint** for external HR/ERP integration

---

## 💬 Support

For questions, bugs, or customization requests:
- 📧 support@smartmodules.io
- 🌐 https://www.smartmodules.io

---

## 📜 License

This module is licensed under the **OPL-1 (Odoo Proprietary License v1.0)**.
See https://www.odoo.com/documentation/user/legal/licenses.html

© 2025 Smart Modules. All rights reserved.
