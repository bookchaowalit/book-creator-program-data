"""Capture GitHub Sponsors documentation through the public Contents API."""
import argparse
import base64
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from .cli import resource, validate


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, value):
        if not self.hidden:
            self.parts.append(value)


REQUIRED_MARKERS = {
    "youtube-partner-program": ("youtube partner program", "monetization", "eligibility requirements"),
    "google-developer-experts": ("google developer experts", "community", "expertise"),
    "github-sponsorship-program": ("github sponsors", "sponsor", "developers"),
    "mozilla-contributor-program": ("contribute to mozilla", "worldwide community", "get involved"),
}


def normalize(raw, source, checked_at):
    if source["id"] != "github-sponsors-open-source" and source["id"] not in REQUIRED_MARKERS:
        raise ValueError("unknown creator-program source")
    if source["id"] != "github-sponsors-open-source":
        parser = Text()
        parser.feed(raw.decode("utf-8"))
        text = " ".join(" ".join(parser.parts).split())
        folded = text.casefold()
        if not all(marker.casefold() in folded for marker in REQUIRED_MARKERS[source["id"]]):
            raise ValueError("creator-program source drift or challenge page")
        item = {
            "id": source["id"],
            "title": source["title"],
            "category": source["category"],
            "source_url": source["source_url"],
            "provider": source["provider"],
            "status": "unknown",
            "deadline": {"kind": "unknown", "at": None},
            "eligible_countries": ["GLOBAL"],
            "eligibility_text": source["eligibility_text"],
            "value": {"kind": "variable", "amount": None, "currency": None, "guaranteed": False},
            "cost": {"fee_amount": None, "currency": None, "auto_renewal": None, "notes": source["cost_notes"]},
            "terms": {
                "creator_medium": source["creator_medium"],
                "audience_requirement": source["audience_requirement"],
                "deliverables": source["deliverables"],
                "content_rights": source["content_rights"],
            },
            "related_records": [],
            "provenance": {
                "evidence_kind": "captured",
                "source_id": source["id"],
                "source_record_id": source["id"],
                "checked_at": checked_at,
                "raw_object_key": None,
                "bronze_manifest_key": None,
            },
        }
        return {"schema_version": source["schema_version"], "source": source["product"], "retrieved_at": checked_at, "data_status": "live", "items": [item]}

    body = json.loads(raw)
    if not isinstance(body, dict):
        raise ValueError("unexpected GitHub Contents response")
    if body.get("encoding") != "base64" or body.get("name") != source["expected_filename"]:
        raise ValueError("unexpected GitHub Contents response")
    try:
        text = base64.b64decode("".join(body["content"].split()), validate=True).decode("utf-8")
    except (KeyError, ValueError, UnicodeDecodeError):
        raise ValueError("invalid GitHub documentation payload") from None
    required = ("title: About GitHub Sponsors", "sponsors.sponsorship-details", "sponsors.no-fees", "sponsors.you-can-be-a-sponsored-developer")
    if not all(marker in text for marker in required):
        raise ValueError("GitHub Sponsors source drift or challenge page")
    item = {
        "id": source["id"],
        "title": source["title"],
        "category": source["category"],
        "source_url": source["source_url"],
        "provider": source["provider"],
        "status": "unknown",
        "deadline": {"kind": "unknown", "at": None},
        "eligible_countries": ["GLOBAL"],
        "eligibility_text": source["eligibility_text"],
        "value": {"kind": "variable", "amount": None, "currency": None, "guaranteed": False},
        "cost": {"fee_amount": None, "currency": None, "auto_renewal": None, "notes": source["cost_notes"]},
        "terms": {
            "creator_medium": "Open-source software and related contributions.",
            "audience_requirement": "A sponsored developer or organization profile and supported-region eligibility are required; audience size is not inferred.",
            "deliverables": "Contribution types may include code, documentation, design, project management, mentorship and related open-source work.",
            "content_rights": "Sponsorship terms and the sponsored account's project rights remain subject to GitHub's additional terms.",
        },
        "related_records": [],
        "provenance": {
            "evidence_kind": "captured",
            "source_id": source["id"],
            "source_record_id": source["id"],
            "checked_at": checked_at,
            "raw_object_key": None,
            "bronze_manifest_key": None,
        },
    }
    return {"schema_version": source["schema_version"], "source": source["product"], "retrieved_at": checked_at, "data_status": "live", "items": [item]}


def source_config(source_id=None):
    if source_id is None:
        return resource("source.json")
    if not re.fullmatch(r"[a-z0-9-]+", source_id):
        raise ValueError("invalid source id")
    base = resource("source.json")
    if base["id"] == source_id:
        return base
    try:
        return resource("source-" + source_id + ".json")
    except FileNotFoundError:
        raise ValueError("unknown source id") from None


def main(argv=None):
    selector = argparse.ArgumentParser(add_help=False)
    selector.add_argument("--source-id")
    selected, remaining = selector.parse_known_args(argv)
    root = os.environ.get("SOLO_EMPIRE_ROOT")
    if not root:
        print("Set SOLO_EMPIRE_ROOT to the local shared capture/lake runtime.", file=sys.stderr)
        return 2
    runtime = Path(root).resolve() / "infra/scripts"
    if not (runtime / "discovery/capture_runtime.py").is_file():
        print("Shared discovery runtime is unavailable.", file=sys.stderr)
        return 2
    sys.path.insert(0, str(runtime))
    from discovery.capture_runtime import VERSION, run

    if VERSION != 1:
        raise RuntimeError("unsupported shared capture runtime")
    return run(source_config(selected.source_id), normalize, validate, remaining)


if __name__ == "__main__":
    raise SystemExit(main())
