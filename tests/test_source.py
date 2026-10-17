import base64
import json
import unittest

from book_creator_program_data.capture import normalize
from book_creator_program_data.cli import resource, validate


class SourceTests(unittest.TestCase):
    def test_github_sponsors_fixture(self):
        text = "\n".join(
            (
                "title: About GitHub Sponsors",
                "{% data reusables.sponsors.sponsorship-details %}",
                "{% data reusables.sponsors.no-fees %}",
                "{% data reusables.sponsors.you-can-be-a-sponsored-developer %}",
            )
        )
        raw = json.dumps(
            {
                "name": "about-github-sponsors.md",
                "encoding": "base64",
                "content": base64.b64encode(text.encode()).decode(),
            }
        ).encode()
        source = resource("source.json")
        data = normalize(raw, source, "2026-09-08T00:00:00Z")
        data["items"][0]["provenance"].update(
            raw_object_key="landing/test", bronze_manifest_key="control/manifests/test"
        )
        self.assertEqual(data["items"][0]["category"], "open-source-sponsorship")
        self.assertEqual(validate(data)["schema_version"], "creator_program.v1")

    def test_source_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize(b"{}", resource("source.json"), "2026-09-08T00:00:00Z")

    def test_additional_creator_sources_normalize(self):
        fixtures = {
            "source-youtube-partner-program.json": "YouTube Partner Program monetization eligibility requirements",
            "source-google-developer-experts.json": "Google Developer Experts community expertise",
            "source-github-sponsorship-program.json": "GitHub Sponsors sponsor developers",
            "source-mozilla-contributor-program.json": "Contribute to Mozilla worldwide community Get involved",
        }
        for filename, text in fixtures.items():
            with self.subTest(source=filename):
                source = resource(filename)
                data = normalize(f"<p>{text}</p>".encode(), source, "2026-09-08T00:00:00Z")
                data["items"][0]["provenance"].update(
                    raw_object_key="landing/test", bronze_manifest_key="control/manifests/test"
                )
                self.assertEqual(data["items"][0]["category"], source["category"])
                self.assertEqual(validate(data)["schema_version"], "creator_program.v1")


if __name__ == "__main__":
    unittest.main()
