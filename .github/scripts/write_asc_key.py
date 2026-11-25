"""Write the App Store Connect API key from the ASC_KEY_P8 secret to KEY_OUT as a clean PEM file.

Accepts whatever the paste looked like: Windows line endings, lost line breaks, extra
spaces, or the whole .p8 file base64-encoded. Prints only lengths and yes/no facts,
never the key itself.
"""
import base64
import binascii
import os
import re
import sys
import textwrap

raw = os.environ["ASC_KEY_P8"]
print(f"ASC_KEY_P8: {len(raw)} characters, {raw.count(chr(10)) + 1} lines, "
      f"Windows line endings: {'yes' if chr(13) in raw else 'no'}, "
      f"BEGIN line: {'yes' if 'BEGIN PRIVATE KEY' in raw else 'no'}, "
      f"END line: {'yes' if 'END PRIVATE KEY' in raw else 'no'}")


def body_of(text):
    m = re.search(r"-----BEGIN PRIVATE KEY-----(.*?)-----END PRIVATE KEY-----", text, re.S)
    return re.sub(r"\s+", "", m.group(1) if m else text)


body = body_of(raw)
if "BEGIN PRIVATE KEY" not in raw:
    try:
        decoded = base64.b64decode(body, validate=True).decode("ascii")
        if "BEGIN PRIVATE KEY" in decoded:
            print("ASC_KEY_P8 holds the whole .p8 file base64-encoded; decoding it.")
            body = body_of(decoded)
    except (binascii.Error, UnicodeDecodeError):
        pass
try:
    der = base64.b64decode(body, validate=True)
except binascii.Error:
    sys.exit("::error::ASC_KEY_P8 is not a .p8 private key. Paste the whole text of "
             "AuthKey_XXXXXXXXXX.p8, BEGIN and END lines included.")
print(f"Key body: {len(body)} base64 characters, {len(der)} bytes.")
with open(os.environ["KEY_OUT"], "w") as f:
    f.write("-----BEGIN PRIVATE KEY-----\n" + "\n".join(textwrap.wrap(body, 64))
            + "\n-----END PRIVATE KEY-----\n")
