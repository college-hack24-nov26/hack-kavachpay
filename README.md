# KAVACHSETU – THE GHOST PROTOCOL
> **Stage 1: Complete Application Foundation**  
> *Tagline: Prove, Don't Share.*

---

## 1. Product Overview
**KavachSetu** is a privacy-first digital trust and financial verification platform. It allows users to prove specific eligibility predicates required by banks and financial institutions (e.g., verifying whether monthly income exceeds ₹25,000) without disclosing raw bank statements, identity papers, or unnecessary personal data.

### Core Product Vision
- **Ghost-Vault**: Self-custodial decoupled credential vault.
- **ZK-Shield**: Zero-Knowledge proof generation engine *(Planned for Stage 2)*.
- **Consent Manager**: Granular verifier authorization *(Planned for Stage 2)*.
- **Decoupled Identity**: Complete isolation between identity and financial metadata.
- **Audit Ledger**: Chronological tamper-evident activity ledger.

---

## 2. What Is Built in Stage 1
Stage 1 implements the complete production-grade application foundation:
- **Splash & Welcome Screen**: KavachSetu brand identity, Ghost Protocol branding, "Prove, Don't Share" tagline, and "Get Started" / "Sign In" actions.
- **User Authentication**: Secure login with email and bcrypt password verification, form validation, error handling, and 1-tap demo credentials autofill.
- **Personalized Dashboard**: Greeting for Aarav Mehta, Ghost-Vault overview card with real-time credential counts (3 total, 3 valid), credential previews, security architecture breakdown, and recent activity logs.
- **Ghost-Vault**: Full credential manager with category filtering (*Identity*, *KYC*, *Income*), credential status pills, and synthetic disclosures.
- **Individual Credential Details**: Dedicated page for each credential displaying Credential ID, type, issuer, issue date, expiry date, validity status, safe verified predicates (e.g. ₹35,000 income band / > ₹25,000 threshold test), and SHA-256 fingerprint digest.
- **Activity History**: Live audit recording tracking `LOGIN`, `VIEW_CREDENTIAL`, and `LOGOUT` events chronologically.
- **Settings & Security**: Profile summary, account details, verified security guarantees (Bcrypt 12 rounds, HMAC-SHA256 session tokens, decoupled local storage mode), synthetic demo notice, and working logout action.

---

## 3. Technology Stack & Clean Architecture

### Frontend (Flutter & Dart)
Located in `flutter_app/`:
- **UI Framework**: Customized Material 3 adhering to an 8-point spacing grid and 14–18px border radii.
- **Centralized Design System**:
  - `lib/core/theme/app_colors.dart`: Strict centralized color palette.
  - `lib/core/theme/app_typography.dart`: Consistent Inter sans-serif typography hierarchy.
  - `lib/core/theme/app_theme.dart`: Material 3 theme configuration.
- **State Management**: Riverpod (`StateNotifierProvider`, `FutureProvider`).
- **Navigation**: GoRouter with `StatefulShellRoute` supporting smooth bottom navigation and deep-linking (`/`, `/login`, `/dashboard`, `/vault`, `/vault/:id`, `/activity`, `/settings`).
- **Security**: Flutter Secure Storage abstraction with local encrypted fallback.

### Backend (Python & FastAPI)
Located in `backend/`:
- **Framework**: FastAPI with RESTful endpoints.
- **Database**: SQLAlchemy ORM with SQLite database (`kavachsetu.db`).
- **Cryptographic Security**:
  - Password Hashing: Bcrypt with 12 adaptive work rounds and salt.
  - Session Management: Cryptographically signed HMAC-SHA256 bearer tokens with automatic expiration.
  - Audit Trail: Automatic logging of security and credential viewing events.

### Interactive Web Client
Located in `backend/static/index.html`:
- Served directly by FastAPI at `http://127.0.0.1:8000`.
- Mirrors the Flutter Material 3 design system, colors, 8pt spacing, and mobile/desktop toggle frame.
- Connected live to all FastAPI backend endpoints.

---

## 4. Centralized Color Palette

All screens and components reference the centralized palette defined in `flutter_app/lib/core/theme/app_colors.dart` and CSS variables:

| Role | Hex | Usage |
| :--- | :--- | :--- |
| **Brand Green** | `#0B6B58` | Primary buttons, active tabs, hero cards |
| **Brand Pressed** | `#095646` | Pressed states and dark hero gradients |
| **Brand Tint** | `#E6F2EE` | Verified pills, selected rows, category icons |
| **Background** | `#F4F3EF` | Main application background |
| **Card** | `#FFFFFF` | Cards, bottom navigation, and sheets |
| **Card Subtle** | `#FAF9F6` | Nested blocks, input fields, code blocks |
| **Border** | `#E3E1DA` | Borders and dividers |
| **Text Primary** | `#1C1F1D` | Main titles and primary text |
| **Text Secondary** | `#5F645F` | Supporting text and secondary labels |
| **Text Hint** | `#8A8E88` | Placeholders and inactive labels |
| **Success** | `#1E8E5A` (Bg: `#E3F4EA`) | Active status badges and confirmed states |
| **Warning** | `#B7791F` (Bg: `#FDF3DC`) | Synthetic demo banners and notices |
| **Danger** | `#C5382F` (Bg: `#FCE9E7`) | Sign out and error alerts |
| **Info** | `#2F63B5` (Bg: `#E7EEF9`) | Informational badges and category tags |

---

## 5. Demo User & Synthetic Data

### Demo User
- **User ID**: `KVS-001`
- **Name**: Aarav Mehta
- **Email**: `user@kavachsetu.demo`
- **Password**: `GhostProtocol@2026`
- **Phone**: `+91 ••••• ••421`

### Synthetic Credentials (Ghost-Vault)
1. **Identity Credential (`KVS-ID-001`)**
   - Category: `IDENTITY`
   - Issuer: `KavachSetu Demo Issuer`
   - Status: `VALID`
   - Safe Attributes: `Synthetic National Digital ID`, Pseudonym `AARAV-M-***4`.
2. **KYC Credential (`KVS-KYC-001`)**
   - Category: `KYC`
   - Issuer: `KavachSetu Demo Issuer`
   - Status: `VALID`
   - Safe Attributes: `KYC Equivalent (Synthetic Sandbox)`, Region `Western Region (India)`.
3. **Income Credential (`KVS-INC-001`)**
   - Category: `INCOME`
   - Issuer: `KavachSetu Demo Issuer`
   - Status: `VALID`
   - Synthetic Monthly Income: `₹35,000`
   - Predicate Test Satisfied: `Monthly Income > ₹25,000`
   - Raw Bank Statement Shared: `No (Decoupled proof model)`

> **Synthetic Notice**: All data is synthetic for demonstration and testing purposes. It is never represented as officially bank-verified or government-issued.

---

## 6. Verification & Step-by-Step User Journey

The entire user journey specified in the requirements is tested and working:
1. **Welcome Screen**: Open the app, view KavachSetu branding, and tap "Sign In".
2. **Login**: Enter `user@kavachsetu.demo` / `GhostProtocol@2026` (or tap **Autofill**). Tap "Sign In".
3. **Dashboard**: Greets Aarav Mehta. Ghost-Vault overview shows **Total: 3**, **Valid: 3**.
4. **Ghost-Vault**: Tap "Ghost-Vault" in the bottom nav to view all 3 credentials with category filtering.
5. **Credential Details**: Tap **Income Credential** (`KVS-INC-001`). View the synthetic income attribute of **₹35,000**, verification predicate, issuer info, and SHA-256 fingerprint.
6. **Activity Log**: Navigate to "Activity". Verify that the login and credential viewing events were automatically recorded with timestamps and client details.
7. **Settings & Logout**: Open "Settings" to inspect the profile and verified security guarantees. Tap "Sign Out" to end the session and return to login.

---

## 7. How to Run & Test

### Option A: Run the Live Application Server
Start the FastAPI server and interactive web client:
```powershell
python run_server.py
```
Then open your browser to:
- **Web Application**: `http://127.0.0.1:8000`
- **Interactive API Documentation (Swagger)**: `http://127.0.0.1:8000/docs`

### Option B: Run Automated Test Suite
Run the automated test suite verifying every endpoint and workflow:
```powershell
python -m backend.tests.test_api
```

### Option C: Run Flutter Application
```powershell
cd flutter_app
flutter pub get
flutter run
```

---

## 8. Honest Report: Working vs. Future Stages

### What is Working in Stage 1:
- [x] Full Splash & Welcome screen with branding.
- [x] User authentication with bcrypt 12 rounds password hashing.
- [x] Secure session token creation and verification (HMAC-SHA256).
- [x] Dynamic dashboard with real database credential counts and activities.
- [x] Ghost-Vault credential listing and category filtering.
- [x] Detailed credential view with zero-exposure predicate attributes.
- [x] Automatic activity audit trail recording (login, view credential, logout).
- [x] Settings screen with profile information and genuine security guarantees.
- [x] Complete Flutter/Dart codebase with Riverpod, GoRouter, and centralized `app_colors.dart`.
- [x] Tested live interactive web interface matching the exact design system.

### What is Planned for Future Stages:
- [ ] *Stage 2*: Zero-Knowledge (ZK-SNARK / ZK-STARK) on-device proof generation circuit (`ZK-Shield`).
- [ ] *Stage 2*: Granular verifier Consent Manager and expiring authorization tokens.
- [ ] *Stage 3*: Lender portal and Hyperledger Fabric audit ledger integration.
- [ ] *Stage 3*: Hardware-backed Android Keystore / iOS Secure Enclave TEE signing.

