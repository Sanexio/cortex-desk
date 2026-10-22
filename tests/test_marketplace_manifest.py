"""Marketplace-Manifest der Einzel-App."""
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "marketplace" / "app.json"


class MarketplaceManifestTests(unittest.TestCase):
    def test_pflichtfelder(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data["id"], "cortex-desk")
        self.assertEqual(data["version"], "0.1.0")
        self.assertEqual(data["bundle_id"], "de.sanexio.cortex-desk")
        self.assertIn("kurzbeschreibung", data)
        self.assertTrue((REPO / "marketplace" / data["symbol"]).is_file())
        self.assertTrue((REPO / "marketplace" / data["symbol_qr"]).is_file())

    def test_klasse_k0(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data["klasse"], "K0")
