import os
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

# Evita chiamate Gemini/File API durante l'import del server Flask.
os.environ["GOOGLE_API_KEY"] = ""
os.environ["ENABLE_LEGACY_MAPS"] = "0"

# Stub minimo di google.genai: /analysis non usa Gemini, ma chatbot.py lo importa
# a livello modulo. Questo evita dipendenze esterne nei test backend minimi.
google_module = types.ModuleType("google")
genai_module = types.ModuleType("google.genai")
genai_types_module = types.ModuleType("google.genai.types")
genai_module.types = genai_types_module
google_module.genai = genai_module
sys.modules.setdefault("google", google_module)
sys.modules.setdefault("google.genai", genai_module)
sys.modules.setdefault("google.genai.types", genai_types_module)

import chatbot  # noqa: E402


class AnalysisEndpointTest(unittest.TestCase):
    def setUp(self):
        chatbot.app.config["TESTING"] = True
        self.client = chatbot.app.test_client()

    def test_analysis_requires_course_id(self):
        response = self.client.get("/analysis")
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertIn("course_id", payload["error"])
        self.assertTrue(payload["available_ids"])

    def test_analysis_returns_known_course(self):
        course_id = chatbot.get_all_course_ids()[0]
        response = self.client.get(f"/analysis?course_id={course_id}")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsInstance(payload, dict)
        self.assertTrue(payload)

    def test_analysis_rejects_unknown_course(self):
        response = self.client.get("/analysis?course_id=UNKNOWN")
        self.assertEqual(response.status_code, 404)
        payload = response.get_json()
        self.assertIn("non trovato", payload["error"])
        self.assertTrue(payload["available_ids"])


if __name__ == "__main__":
    unittest.main()
