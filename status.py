#!/usr/bin/env python3
"""Update the "Where are Maddie & Michael?" box on the site.

  python3 status.py "Drowned Valley Brewing Company" "Setting up for rehearsal dinner" "6:30 PM" --map "Drowned Valley Brewing Company Cartersville GA"

Arguments: where, what you're doing (optional), here until (optional). --map adds a Google Maps link.
Asks for the site password (or reads SITE_PASSWORD), writes status.json, then commit and push.
Needs: pip install cryptography
"""
import argparse, base64, datetime, getpass, hashlib, json, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

here = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("where")
ap.add_argument("doing", nargs="?", default="")
ap.add_argument("until", nargs="?", default="")
ap.add_argument("--map", default="", help="Google Maps search text for the place")
args = ap.parse_args()

vault = json.load(open(os.path.join(here, "vault.json")))
pw = os.environ.get("SITE_PASSWORD") or getpass.getpass("Site password: ")
key = hashlib.pbkdf2_hmac("sha256", pw.strip().lower().encode(), base64.b64decode(vault["salt"]), vault["iter"], 32)
aes = AESGCM(key)
aes.decrypt(base64.b64decode(vault["html"]["iv"]), base64.b64decode(vault["html"]["ct"]), None)  # wrong password fails here

status = {"where": args.where, "doing": args.doing, "until": args.until, "map": args.map,
          "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
iv = os.urandom(12)
out = {"iv": base64.b64encode(iv).decode(), "ct": base64.b64encode(aes.encrypt(iv, json.dumps(status).encode(), None)).decode()}
with open(os.path.join(here, "status.json"), "w") as f:
    json.dump(out, f)
print("Updated status.json:", status)
