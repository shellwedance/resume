#!/usr/bin/env python3
"""Print the published resume to an A4 PDF with per-item page breaks.

Drives a headless Google Chrome over the DevTools Protocol, emulates the
"screen" media (the print CSS in this repo is a compact layout that we do not
want), injects the page-break rules from ``paginate.js`` and calls
``Page.printToPDF``.

Usage:
    python3 -m venv .venv && .venv/bin/pip install websocket-client
    .venv/bin/python scripts/print_pdf.py ~/Desktop/taeuk_kim_resume.pdf
    .venv/bin/python scripts/print_pdf.py out.pdf --url http://127.0.0.1:4000/resume/

Options:
    --url URL        Page to print (default: https://shellwedance.github.io/resume/)
    --chrome PATH    Chrome binary (default: macOS Google Chrome.app)
    --no-paginate    Skip paginate.js and print the page as-is
"""
import argparse
import base64
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket

DEFAULT_URL = "https://shellwedance.github.io/resume/"
DEFAULT_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGINATE_JS = Path(__file__).with_name("paginate.js")
PORT = 9333

A4 = {
    "paperWidth": 8.27,
    "paperHeight": 11.69,
    "marginTop": 0.4,
    "marginBottom": 0.4,
    "marginLeft": 0.4,
    "marginRight": 0.4,
    "printBackground": True,
    "displayHeaderFooter": False,
    "preferCSSPageSize": False,
}


class Cdp:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, suppress_origin=True)
        self.ws.settimeout(60)
        self.next_id = 0

    def send(self, method, params=None, session=None):
        self.next_id += 1
        payload = {"id": self.next_id, "method": method, "params": params or {}}
        if session:
            payload["sessionId"] = session
        self.ws.send(json.dumps(payload))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.next_id:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    def wait_event(self, name, session):
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("method") == name and msg.get("sessionId") == session:
                return msg


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("output", help="Output PDF path")
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--chrome", default=DEFAULT_CHROME)
    ap.add_argument("--no-paginate", action="store_true")
    args = ap.parse_args()

    if not Path(args.chrome).exists():
        sys.exit(f"Chrome not found at {args.chrome} (use --chrome)")

    profile_dir = tempfile.mkdtemp(prefix="resume-print-")
    proc = subprocess.Popen(
        [
            args.chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            f"--remote-debugging-port={PORT}",
            f"--user-data-dir={profile_dir}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        version = None
        for _ in range(100):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version") as r:
                    version = json.load(r)
                break
            except Exception:
                time.sleep(0.2)
        if version is None:
            sys.exit("Chrome did not expose the DevTools endpoint in time")

        cdp = Cdp(version["webSocketDebuggerUrl"])
        target = cdp.send("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.send("Target.attachToTarget", {"targetId": target, "flatten": True})["sessionId"]
        cdp.send("Page.enable", session=session)
        cdp.send("Emulation.setEmulatedMedia", {"media": "screen"}, session=session)
        cdp.send("Page.navigate", {"url": args.url}, session=session)
        cdp.wait_event("Page.loadEventFired", session)
        time.sleep(2)  # let web fonts and the avatar image settle

        if not args.no_paginate:
            cdp.send("Runtime.evaluate", {"expression": PAGINATE_JS.read_text()}, session=session)
            time.sleep(0.5)

        result = cdp.send("Page.printToPDF", A4, session=session)
        out = Path(args.output)
        out.write_bytes(base64.b64decode(result["data"]))
        print(f"written {out}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
