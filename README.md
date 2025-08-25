# Bookora Test Navigator

A secure automation tool built with **SeleniumBase** and an undetected Chrome driver. It monitors the driving test booking system and sends real-time **WhatsApp alerts** when user input is required (e.g., CAPTCHA solving or manual confirmation).

## Project Structure
<img width="569" height="397" alt="image" src="https://github.com/user-attachments/assets/a0183abe-b59f-4e1f-9613-7621359b596a" />

## Setup Instructions
### 1. Run Setup
* **Action:** Double-click `setup.bat`
* **Result:**
  * Creates a virtual environment (if needed)
  * Installs dependencies from `requirements.txt`

### 2. Configure Environment
Edit `config/.env` with your details:
```env
LOGIN_URL=https://www.gov.uk/book-pupil-driving-test
USERNAME=your_username_here
PASSWORD=your_password_here
BOOKING_CENTER=Preferred Test Center
CATEGORY=Car
DISABILITY=No
TEXTMAGIC_USERNAME=your_textmagic_user
TEXTMAGIC_API_KEY=your_textmagic_api_key
```
Add WhatsApp recipients in `config/recipients.txt` (one per line).

## Running Bookora Test Navigator
**Windows (Auto-Launch):**
Double-click `main.bat`
**All Platforms (Manual):**
```bash
python main.py
```
## 🔄 Bot Workflow
1. **Launch:** Opens browser and navigates to driving test login page.
2. **CAPTCHA Detection:** Pauses if CAPTCHA is detected → sends WhatsApp alert.
3. **Login Screen Detection:** Sends WhatsApp alert when login screen appears.
4. **Autologin:** Uses `.env` credentials to log in automatically.
5. **Form Autofill:** Fills form with booking values from `.env`.
6. **Slot Scanning:** Continuously scans for available green slots.
7. **Slot Found:** Clicks the slot, sends WhatsApp alert → waits for manual confirmation.

## WhatsApp Alerts
* **CAPTCHA detected:** "CAPTCHA detected. Please complete it to continue."
* **Login screen visible:** "Login screen ready. Logging in now\..."
* **Green slot found:** "Green slot found! Please jump on the PC and complete the booking manually."

## Logging
Logs are stored at: `logs/YYYY-MM-DD.log`
**Log Includes:**
* CAPTCHA detection
* WhatsApp alerts sent
* Login attempts
* Slot discovery events
* Manual action prompts

## ✅ Example Flow
1. Run `main.bat` → Bookora Test Navigator launches browser.
2. CAPTCHA appears → bot pauses, sends WhatsApp alert.
3. Solve CAPTCHA manually.
4. Bot auto-fills login credentials and proceeds.
5. Booking form auto-filled.
6. Bot scans for slots → refreshes until found.
7. Green slot found → bot clicks slot → WhatsApp alert sent.
8. Confirm booking manually.
