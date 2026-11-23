#!/usr/bin/env python3
"""Cross-platform smoke test for ReturnZero AI Backend API.

Exercises /healthz and key operational endpoints against local or deployed environments.
Uses standard library urllib for zero external dependencies.

Usage:
    python scripts/smoke_test.py [base_url]
Default base_url: http://localhost:8000
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any


def check_health(base_url: str) -> bool:
    url = f"{base_url.rstrip('/')}/healthz"
    print(f"[*] Checking health endpoint: {url} ...")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ReturnZero-SmokeTest/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            status_code = resp.status
            body_bytes = resp.read()
            body_text = body_bytes.decode("utf-8")
            data: dict[str, Any] = json.loads(body_text)

            print(f"[+] Status Code: {status_code}")
            print(f"[+] Response: {json.dumps(data, indent=2)}")

            if status_code != 200:
                print(f"[FAIL] Expected status code 200, got {status_code}", file=sys.stderr)
                return False

            if data.get("status") != "ok":
                print(f"[FAIL] Expected status 'ok', got {data.get('status')}", file=sys.stderr)
                return False

            if data.get("service") != "returnzero-api":
                print(f"[FAIL] Expected service 'returnzero-api', got {data.get('service')}", file=sys.stderr)
                return False

            print("[PASS] /healthz is healthy and reporting status: ok")
            return True

    except urllib.error.HTTPError as exc:
        print(f"[FAIL] HTTP error: {exc.code} {exc.reason}", file=sys.stderr)
        return False
    except urllib.error.URLError as exc:
        print(f"[FAIL] URL error (service down or unreachable?): {exc.reason}", file=sys.stderr)
        return False
    except Exception as exc:
        print(f"[FAIL] Unexpected error: {exc}", file=sys.stderr)
        return False


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    print("=" * 60)
    print(f"ReturnZero AI Smoke Test — Target: {base_url}")
    print("=" * 60)

    success = check_health(base_url)
    if not success:
        print("\n[RESULT] Smoke test failed.", file=sys.stderr)
        return 1

    print("\n[RESULT] Smoke test passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
