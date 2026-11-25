# MedPouch

A personal medical wallet for iPhone: medications with reminders, prescriptions with photos, allergies, emergency contacts, family members, a travel packing list, and an emergency card with a QR code.

- **Platform:** iPhone, iOS 17+
- **Tech:** SwiftUI, Core Data (on-device only), local notifications
- **Backend:** none. All data stays on the device.

## Opening the project

You need a Mac with **Xcode 26** or later.

1. Copy this whole `Medpouch` folder to the Mac.
2. Double-click `MedPouch.xcodeproj`.
3. Select the **MedPouch** target → **Signing & Capabilities** → choose your **Team**.
4. If `com.krithkaur.medpouch` is already taken, change the **Bundle Identifier**.
5. Pick an iPhone simulator and press **⌘R**.

Files inside `MedPouch/` are picked up automatically (Xcode folder sync), so there is nothing to add by hand.

## Releasing without a Mac (GitHub Actions)

`.github/workflows/ios.yml` builds the app on GitHub's macOS machines. Every push to `main` compiles it; **Actions → iOS → Run workflow** also archives, signs and uploads it to App Store Connect.

One-time setup:

1. **GitHub repo** `medpouch`, pushed from this folder. Turn on **Settings → Pages → Deploy from a branch → `main` / `docs`**. The support page is then `https://krithkaur397-cloud.github.io/medpouch/` and the privacy policy `https://krithkaur397-cloud.github.io/medpouch/privacy.html` (already set in the app and in `docs/`).
2. **App Store Connect → Apps → + → New App**: iOS, name `MedPouch`, bundle ID `com.krithkaur.medpouch`, any SKU (e.g. `medpouch`). Uploads fail until this record exists.
3. **App Store Connect → Users and Access → Integrations → App Store Connect API → Team Keys → +**: role **Admin**. Download the `.p8` (only possible once) and note the Key ID and the Issuer ID.
4. **GitHub → Settings → Secrets and variables → Actions → New repository secret**, four times:
   - `APPLE_TEAM_ID`: Team ID from developer.apple.com/account → Membership details
   - `ASC_KEY_ID`: the key's Key ID
   - `ASC_ISSUER_ID`: the Issuer ID
   - `ASC_KEY_P8`: the whole text of the `.p8` file, including the BEGIN/END lines

Screenshots: **Actions → Screenshots → Run workflow** runs a Debug build in a 6.9-inch iPhone simulator with sample data (`MedPouch/App/DemoData.swift`, used only with the `-MedPouchDemo` launch argument and absent from Release builds), captures one screen per tab, and uploads them to the App Store version being prepared.

Each release: run the workflow, wait for the build to finish processing in App Store Connect → TestFlight, install it on an iPhone with TestFlight, take screenshots, then fill in the listing from `docs/APP_STORE_SUBMISSION.md` and **Add for Review**. The build number is the workflow run number, so it always goes up; bump `MARKETING_VERSION` in the project for a new version (1.1, 2.0, ...).

## Project layout

```
MedPouch/
  App/            App entry point, tab bar
  Data/           Core Data model, persistence, helpers
  Services/       Notifications, QR codes, image handling
  Views/
    Home/         Dashboard, setup checklist
    Medications/  Medications list, add/edit
    Prescriptions/
    Profile/      Profile, allergies, contacts, privacy & data
    Family/       Family members and their records
    Emergency/    Emergency card, travel meds
    Onboarding/
  Assets.xcassets App icon, accent colour
  PrivacyInfo.xcprivacy
docs/             Privacy policy, support page, App Store submission kit
Info.plist        Export compliance flag (merged with generated Info.plist)
```

## Manual test checklist

Run through on a real iPhone before each release:

- [ ] Fresh install → onboarding → can't finish without accepting the disclaimer
- [ ] Add a medication (Daily) → reminder permission prompt → reminder arrives at 9:00 AM
- [ ] Edit medication to "As needed" → reminder is cancelled
- [ ] Untick "Essential" → medication stays in the list (no star) and leaves the emergency card
- [ ] Add prescription with camera photo and with library photo
- [ ] Add allergy, "No Known Allergies", and emergency contact; tap the call button
- [ ] Emergency card shows everything; QR code scans with another phone's camera; share image works
- [ ] Add a family member with their own medication, allergy, contact; their card shows only their data
- [ ] Delete a family member → their records and reminders are gone
- [ ] Travel Meds quantities update with trip length; share list works
- [ ] Privacy & Data → Delete All Data → app returns to onboarding with everything empty
- [ ] Lock the phone while the app is open, unlock → data still loads
