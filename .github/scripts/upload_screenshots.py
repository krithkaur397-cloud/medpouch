"""Upload screenshots to the App Store version being prepared, replacing what is in that slot.

Usage: python upload_screenshots.py shot1.jpg shot2.jpg ...   (uploaded in this order)
Environment: ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_PATH, BUNDLE_ID,
             DISPLAY_TYPE (default APP_IPHONE_67, the 6.9-inch iPhone slot), LOCALE (default en-US)
Needs PyJWT with the cryptography extra.
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import jwt

API = "https://api.appstoreconnect.apple.com/v1"
KEY_ID = os.environ["ASC_KEY_ID"]
ISSUER = os.environ["ASC_ISSUER_ID"]
with open(os.environ["ASC_KEY_PATH"]) as f:
    PRIVATE_KEY = f.read()
BUNDLE_ID = os.environ["BUNDLE_ID"]
DISPLAY_TYPE = os.environ.get("DISPLAY_TYPE") or "APP_IPHONE_67"
LOCALE = os.environ.get("LOCALE") or "en-US"
EDITABLE = {"PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED", "REJECTED", "METADATA_REJECTED", "INVALID_BINARY"}


def token():
    now = int(time.time())
    return jwt.encode({"iss": ISSUER, "iat": now, "exp": now + 900, "aud": "appstoreconnect-v1"},
                      PRIVATE_KEY, algorithm="ES256", headers={"kid": KEY_ID, "typ": "JWT"})


def call(method, path, body=None, query=None):
    url = API + path + ("?" + urllib.parse.urlencode(query) if query else "")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": "Bearer " + token(),
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"::error::{method} {path} failed with HTTP {e.code}: {e.read().decode(errors='replace')[:3000]}")


def main(files):
    if not files:
        sys.exit("::error::No screenshot files given")

    apps = call("GET", "/apps", query={"filter[bundleId]": BUNDLE_ID})["data"]
    if not apps:
        sys.exit(f"::error::No App Store Connect app has bundle ID {BUNDLE_ID}")
    app_id = apps[0]["id"]

    versions = call("GET", f"/apps/{app_id}/appStoreVersions",
                    query={"filter[platform]": "IOS", "limit": "20"})["data"]
    version = next((v for v in versions
                    if v["attributes"].get("appStoreState") in EDITABLE
                    or v["attributes"].get("appVersionState") in EDITABLE), None)
    if not version:
        states = [(v["attributes"].get("versionString"), v["attributes"].get("appStoreState")) for v in versions]
        sys.exit(f"::error::No editable iOS version found. Versions: {states}")
    print(f"Version {version['attributes'].get('versionString')} ({version['id']})")

    locs = call("GET", f"/appStoreVersions/{version['id']}/appStoreVersionLocalizations")["data"]
    loc = next((l for l in locs if l["attributes"].get("locale") == LOCALE), None)
    if not loc:
        sys.exit(f"::error::No {LOCALE} localization. Found: {[l['attributes'].get('locale') for l in locs]}")

    sets = call("GET", f"/appStoreVersionLocalizations/{loc['id']}/appScreenshotSets")["data"]
    print("Existing screenshot sets:", [s["attributes"].get("screenshotDisplayType") for s in sets])
    shot_set = next((s for s in sets if s["attributes"].get("screenshotDisplayType") == DISPLAY_TYPE), None)
    if not shot_set:
        shot_set = call("POST", "/appScreenshotSets", {"data": {
            "type": "appScreenshotSets",
            "attributes": {"screenshotDisplayType": DISPLAY_TYPE},
            "relationships": {"appStoreVersionLocalization": {
                "data": {"type": "appStoreVersionLocalizations", "id": loc["id"]}}}}})["data"]
        print(f"Created {DISPLAY_TYPE} screenshot set")
    set_id = shot_set["id"]

    old = call("GET", f"/appScreenshotSets/{set_id}/appScreenshots")["data"]
    for shot in old:
        call("DELETE", f"/appScreenshots/{shot['id']}")
    if old:
        print(f"Removed {len(old)} earlier screenshot(s)")

    uploaded = []
    for path in files:
        with open(path, "rb") as f:
            data = f.read()
        name = os.path.basename(path)
        shot = call("POST", "/appScreenshots", {"data": {
            "type": "appScreenshots",
            "attributes": {"fileName": name, "fileSize": len(data)},
            "relationships": {"appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": set_id}}}}})["data"]
        for op in shot["attributes"].get("uploadOperations") or []:
            chunk = data[op["offset"]:op["offset"] + op["length"]]
            headers = {h["name"]: h["value"] for h in op.get("requestHeaders") or []}
            req = urllib.request.Request(op["url"], data=chunk, method=op["method"], headers=headers)
            with urllib.request.urlopen(req) as resp:
                resp.read()
        call("PATCH", f"/appScreenshots/{shot['id']}", {"data": {
            "type": "appScreenshots", "id": shot["id"],
            "attributes": {"uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()}}})
        print(f"Uploaded {name} ({len(data)} bytes)")
        uploaded.append((name, shot["id"]))

    # Wait for Apple to accept each image (it checks the size matches the display slot)
    pending = dict(uploaded)
    failed = []
    for _ in range(40):
        for name, shot_id in list(pending.items()):
            state = call("GET", f"/appScreenshots/{shot_id}")["data"]["attributes"].get("assetDeliveryState") or {}
            if state.get("state") == "COMPLETE":
                print(f"{name}: accepted")
                del pending[name]
            elif state.get("state") == "FAILED":
                print(f"::error::{name}: rejected: {state.get('errors')}")
                failed.append(name)
                del pending[name]
        if not pending:
            break
        time.sleep(6)
    if pending:
        print(f"::warning::Still processing after 4 minutes: {list(pending)}")
    if failed:
        sys.exit(1)
    print(f"{len(uploaded) - len(failed)} screenshot(s) are in the {DISPLAY_TYPE} slot for {LOCALE}.")


if __name__ == "__main__":
    main(sys.argv[1:])
