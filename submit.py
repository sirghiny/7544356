import hashlib
import hmac
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone


def main():
    signing_secret = os.environ["SIGNING_SECRET"].encode("utf-8")

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"

    payload = {
        "action_run_link": os.environ["ACTION_RUN_LINK"],
        "email": os.environ["APPLICANT_EMAIL"],
        "name": os.environ["APPLICANT_NAME"],
        "repository_link": os.environ["REPOSITORY_LINK"],
        "resume_link": os.environ["RESUME_LINK"],
        "timestamp": timestamp,
    }

    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    digest = hmac.new(signing_secret, body, hashlib.sha256).hexdigest()
    signature = f"sha256={digest}"

    req = urllib.request.Request(
        "https://b12.io/apply/submission",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": signature,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(f"Submission: {result}")
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8")
        raise SystemExit(f"HTTP {e.code}: {body_text}") from e


if __name__ == "__main__":
    main()
