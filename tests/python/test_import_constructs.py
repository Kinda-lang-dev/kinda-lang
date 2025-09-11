# tests/python/test_import_constructs.py

import unittest
import re
from unittest.mock import patch, MagicMock
from kinda.grammar.python.constructs import KindaPythonConstructs
from kinda.grammar.python.matchers import match_python_construct
from kinda.langs.python.transformer import transform_line


class TestImportConstructsMatchers(unittest.TestCase):
    """Test import construct pattern matching and parsing"""

    def test_kinda_import_pattern_basic(self):
        """Test basic kinda import pattern matching"""
        pattern = KindaPythonConstructs["kinda_import"]["pattern"]

        # Basic import
        match = pattern.match("~kinda import os")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "os")
        self.assertIsNone(match.group(2))  # No alias

        # Import with alias
        match = pattern.match("~kinda import json as j")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "json")
        self.assertEqual(match.group(2), "j")

        # Dotted module
        match = pattern.match("~kinda import numpy.random")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "numpy.random")
        self.assertIsNone(match.group(2))

        # With comment
        match = pattern.match("~kinda import sys  # for system stuff")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "sys")

    def test_kinda_import_pattern_invalid(self):
        """Test invalid kinda import patterns"""
        pattern = KindaPythonConstructs["kinda_import"]["pattern"]

        # Invalid patterns should not match
        invalid_patterns = [
            "kinda import os",  # Missing ~
            "~import os",  # Missing kinda
            "~kinda import",  # No module name
            "~kinda import 123",  # Invalid module name (starts with number)
            "~kinda import os.123",  # Invalid dotted name
        ]

        for invalid in invalid_patterns:
            with self.subTest(invalid=invalid):
                match = pattern.match(invalid)
                self.assertIsNone(match, f"Should not match: {invalid}")

    def test_maybe_import_pattern_basic(self):
        """Test basic maybe import pattern matching"""
        pattern = KindaPythonConstructs["maybe_import"]["pattern"]

        # Basic maybe import
        match = pattern.match("~maybe import requests")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "requests")
        self.assertIsNone(match.group(2))  # No alias
        self.assertIsNone(match.group(3))  # No fallback

        # With alias
        match = pattern.match("~maybe import requests as req")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "requests")
        self.assertEqual(match.group(2), "req")
        self.assertIsNone(match.group(3))  # No fallback

        # With fallback
        match = pattern.match("~maybe import requests ~welp urllib")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "requests")
        self.assertIsNone(match.group(2))  # No alias
        self.assertEqual(match.group(3), "urllib")

        # With alias and fallback
        match = pattern.match("~maybe import requests as req ~welp urllib")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "requests")
        self.assertEqual(match.group(2), "req")
        self.assertEqual(match.group(3), "urllib")

    def test_match_python_construct_imports(self):
        """Test that match_python_construct recognizes import constructs"""

        # Test kinda import
        key, groups = match_python_construct("~kinda import os")
        self.assertEqual(key, "kinda_import")
        self.assertEqual(groups[0], "os")

        # Test maybe import
        key, groups = match_python_construct("~maybe import requests")
        self.assertEqual(key, "maybe_import")
        self.assertEqual(groups[0], "requests")

        # Test with alias
        key, groups = match_python_construct("~kinda import json as j")
        self.assertEqual(key, "kinda_import")
        self.assertEqual(groups[0], "json")
        self.assertEqual(groups[1], "j")


class TestImportConstructsTransformation(unittest.TestCase):
    """Test import construct transformation to Python code"""

    def test_kinda_import_transformation_basic(self):
        """Test basic kinda import transformation"""
        result = transform_line("~kinda import os")
        self.assertEqual(len(result), 1)
        self.assertIn("os = kinda_import('os')", result[0])

        # Dotted import
        result = transform_line("~kinda import numpy.random")
        self.assertEqual(len(result), 1)
        self.assertIn("random = kinda_import('numpy.random')", result[0])

    def test_kinda_import_transformation_with_alias(self):
        """Test kinda import transformation with alias"""
        result = transform_line("~kinda import json as j")
        self.assertEqual(len(result), 1)
        self.assertIn("j = kinda_import('json', alias='j')", result[0])

    def test_maybe_import_transformation_basic(self):
        """Test basic maybe import transformation"""
        result = transform_line("~maybe import requests")
        self.assertEqual(len(result), 1)
        self.assertIn("requests = maybe_import('requests')", result[0])

    def test_maybe_import_transformation_with_alias(self):
        """Test maybe import transformation with alias"""
        result = transform_line("~maybe import requests as req")
        self.assertEqual(len(result), 1)
        self.assertIn("req = maybe_import('requests', alias='req')", result[0])

    def test_maybe_import_transformation_with_fallback(self):
        """Test maybe import transformation with fallback"""
        result = transform_line("~maybe import requests ~welp urllib")
        self.assertEqual(len(result), 1)
        self.assertIn("requests = maybe_import('requests', fallback_module='urllib')", result[0])

    def test_maybe_import_transformation_with_alias_and_fallback(self):
        """Test maybe import transformation with both alias and fallback"""
        result = transform_line("~maybe import requests as req ~welp urllib")
        self.assertEqual(len(result), 1)
        self.assertIn(
            "req = maybe_import('requests', alias='req', fallback_module='urllib')", result[0]
        )


class TestImportConstructsRuntime(unittest.TestCase):
    """Test import construct runtime behavior"""

    def test_import_constructs_have_required_structure(self):
        """Test that import constructs have the required structure for runtime generation"""
        kinda_construct = KindaPythonConstructs.get("kinda_import")
        self.assertIsNotNone(kinda_construct)
        self.assertEqual(kinda_construct["type"], "import")
        self.assertIn("body", kinda_construct)
        self.assertIn("def kinda_import", kinda_construct["body"])

        maybe_construct = KindaPythonConstructs.get("maybe_import")
        self.assertIsNotNone(maybe_construct)
        self.assertEqual(maybe_construct["type"], "import")
        self.assertIn("body", maybe_construct)
        self.assertIn("def maybe_import", maybe_construct["body"])

    def test_import_functions_syntax_validity(self):
        """Test that the generated import functions have valid Python syntax"""
        # Test kinda_import syntax
        kinda_import_code = KindaPythonConstructs["kinda_import"]["body"]
        try:
            compile(kinda_import_code, "<string>", "exec")
        except SyntaxError as e:
            self.fail(f"kinda_import function has invalid syntax: {e}")

        # Test maybe_import syntax
        maybe_import_code = KindaPythonConstructs["maybe_import"]["body"]
        try:
            compile(maybe_import_code, "<string>", "exec")
        except SyntaxError as e:
            self.fail(f"maybe_import function has invalid syntax: {e}")

    def test_import_functions_contain_personality_integration(self):
        """Test that import functions integrate with personality system"""
        kinda_import_code = KindaPythonConstructs["kinda_import"]["body"]
        self.assertIn("chaos_probability", kinda_import_code)
        self.assertIn("update_chaos_state", kinda_import_code)
        self.assertIn("get_personality", kinda_import_code)

        maybe_import_code = KindaPythonConstructs["maybe_import"]["body"]
        self.assertIn("chaos_probability", maybe_import_code)
        self.assertIn("update_chaos_state", maybe_import_code)
        self.assertIn("get_personality", maybe_import_code)


class TestImportConstructsStatistical(unittest.TestCase):
    """Statistical tests for probabilistic import behavior"""

    def test_import_constructs_use_randomness(self):
        """Test that import constructs use randomness in their logic"""
        kinda_import_code = KindaPythonConstructs["kinda_import"]["body"]
        self.assertIn("random.random()", kinda_import_code)
        self.assertIn("chaos_probability", kinda_import_code)

        maybe_import_code = KindaPythonConstructs["maybe_import"]["body"]
        self.assertIn("random.random()", maybe_import_code)
        self.assertIn("chaos_probability", maybe_import_code)

    def test_import_constructs_have_fallback_behavior(self):
        """Test that import constructs have proper fallback behavior"""
        kinda_import_code = KindaPythonConstructs["kinda_import"]["body"]
        self.assertIn("KindaMockModule", kinda_import_code)
        self.assertIn("except ImportError", kinda_import_code)

        maybe_import_code = KindaPythonConstructs["maybe_import"]["body"]
        self.assertIn("MaybeMockModule", maybe_import_code)
        self.assertIn("except ImportError", maybe_import_code)
        self.assertIn("fallback_module", maybe_import_code)


if __name__ == "__main__":
    unittest.main()
