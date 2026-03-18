# Smart Waiting Room — Odoo 19 Module

**Version:** 19.0.1.0.0 | **License:** OPL-1 

A professional, universal intelligent queue management solution for Odoo 19.

---

## 🎯 Overview

Smart Waiting Room transforms your reception area into an efficient, modern experience. Real-time queue tracking, a stunning TV display, and a self check-in kiosk — all integrated into Odoo.

**Works for:** Dental clinics · Medical centers · Banks · Government offices · Training centers · Any service business

---

## ✨ Features

### Core Queue Management
- Real-time dynamic waiting list with live status updates
- Token/number generation per department
- Smart prioritization: **Normal / Priority / Urgent / VIP**
- Multi-room & multi-department support
- Estimated wait time calculation
- Complete visit history & statistics

### Visitor States
- **Waiting** → **Called** → **In Service** → **Done**
- No Show & Cancelled tracking
- Re-queue capability
- Bulk actions

### TV Display Screen (Public URL — no login)
- Stunning sci-fi holographic dark design
- Live "Now Serving" panel with animations
- Called / Please Proceed panel
- Full waiting list with estimated times
- Audio announcements (browser TTS)
- Animated particles & scan effects
- Auto-refresh every 4 seconds
- Scrolling ticker footer

### Self Check-in Kiosk (Public URL — no login)
- 3-step intuitive check-in flow
- Department selection with icons
- Name, phone, visit type collection
- Token confirmation with position & wait time
- Touch-friendly for tablets/touchscreens
- Auto-reset after inactivity

### Backend (Odoo)
- Kanban board grouped by status
- Quick-add form
- Dashboard statistics
- Daily PDF report (print from action menu)
- Scheduled auto no-show after configurable delay
- Daily archive cron job

### Multilingual
Translated into: **English · French · Arabic · Spanish · German · Portuguese · Chinese (Simplified)**

---

## 🚀 Installation

1. Copy the `smart_waiting_room` folder to your Odoo addons directory
2. Update the apps list (Settings → Apps → Update Apps List)
3. Search for "Smart Waiting Room" and install
4. Go to **Waiting Room → Rooms** and create your first room
5. Share the **TV Display URL** with your screen and **Kiosk URL** for self check-in

---

## 📺 Usage

### Setting up a Room
1. Create a waiting room with a name and code
2. Link departments/services
3. Copy the **Display URL** → open on your TV/screen
4. Copy the **Kiosk URL** → open on a tablet at reception

### Managing the Queue
- Use the **Queue Board** (Kanban view) for live management
- Click **📢 Call** to call a patient
- Click **▶ Start** to mark In Service
- Click **✔ Done** when finished

### TV Display
The display auto-refreshes every 4 seconds. Audio announcements are made automatically when a patient is called (uses browser Text-to-Speech).

### Kiosk Mode
Visitors can self check-in using the kiosk URL. They select their department, enter their name, and receive a token number.

---

## ⚙️ Configuration

Go to **Settings → Smart Waiting Room**:
- Auto No-Show delay (default: 10 min)
- Overdue threshold (default: 45 min)
- Enable/disable audio
- Show/hide estimated wait time

---

## 📦 Module Structure

```
smart_waiting_room/
├── models/
│   ├── waiting_room.py          # Room model
│   ├── queue_line.py            # Queue entry model
│   ├── department.py            # Department/service model
│   └── res_config_settings.py   # Settings
├── controllers/
│   └── controllers.py           # Public routes + JSON API
├── wizard/
│   └── bulk_action_wizard.py    # Bulk state changes
├── views/                       # All Odoo XML views
├── static/src/
│   ├── css/                     # Display, kiosk, backend CSS
│   └── js/                     # Display, kiosk, OWL2 widgets
├── i18n/                        # FR, AR, ES, DE, PT, ZH_CN
├── data/                        # Sequences, cron jobs, departments
├── demo/                        # Demo data
└── report/                      # PDF daily report
```

---

## 🔧 Technical Notes

- **Odoo Version:** 19.0
- **Python:** 3.10+
- **Dependencies:** base, web, mail, calendar
- **Public routes:** No authentication required for display & kiosk
- **Real-time:** Polling every 4s (no websocket required)
- **Audio:** Browser Web Speech API (no external service)

---

## 📞 Support

- **Website:** https://www.smartdentalsuite.com
- **Email:** contact@smartdentalsuite.com
- **License:** OPL-1 (Odoo Proprietary License)

---

## 📝 Changelog

### 19.0.1.0.0 (2025)
- Initial release
- Full queue management
- TV Display with holographic design
- Kiosk self check-in
- 7 language translations
- PDF daily report
- OWL2 backend widgets
