# tests/python/test_import_integration.py

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from kinda.langs.python.transformer import transform_file, transform_line, KindaParseError


class TestImportConstructsIntegration(unittest.TestCase):
    """Integration tests for import constructs with the full transformer pipeline"""
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / "test_imports.knda"
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_kinda_import_file_transformation(self):
        """Test transforming a file containing kinda import constructs"""
        # Create test file content
        content = """# Test kinda imports
~kinda import os
~kinda import json as j
~kinda import numpy.random
~sorta print("Testing imports")
"""
        self.test_file.write_text(content)
        
        # Transform the file
        result = transform_file(self.test_file)
        
        # Verify the transformation
        self.assertIn("from kinda.langs.python.runtime.fuzzy import", result)
        self.assertIn("kinda_import", result)
        self.assertIn("sorta_print", result)
        self.assertIn("os = kinda_import('os')", result)
        self.assertIn("j = kinda_import('json', alias='j')", result)
        self.assertIn("random = kinda_import('numpy.random')", result)
        self.assertIn('sorta_print("Testing imports")', result)
    
    def test_maybe_import_file_transformation(self):
        """Test transforming a file containing maybe import constructs"""
        # Create test file content
        content = """# Test maybe imports
~maybe import requests
~maybe import requests as req
~maybe import requests ~welp urllib
~maybe import requests as req ~welp urllib
~sorta print("Testing maybe imports")
"""
        self.test_file.write_text(content)
        
        # Transform the file
        result = transform_file(self.test_file)
        
        # Verify the transformation
        self.assertIn("from kinda.langs.python.runtime.fuzzy import", result)
        self.assertIn("maybe_import", result)
        self.assertIn("sorta_print", result)
        self.assertIn("requests = maybe_import('requests')", result)
        self.assertIn("req = maybe_import('requests', alias='req')", result)
        self.assertIn("requests = maybe_import('requests', fallback_module='urllib')", result)
        self.assertIn("req = maybe_import('requests', alias='req', fallback_module='urllib')", result)
    
    def test_mixed_constructs_file_transformation(self):
        """Test transforming a file with mixed import and other constructs"""
        # Create test file content
        content = """# Mixed constructs test
~kinda import os
~kinda int x ~= 42
~maybe import requests ~welp urllib
~sometimes() {
    ~sorta print("Sometimes we print")
}
value ~= 100~ish
"""
        self.test_file.write_text(content)
        
        # Transform the file
        result = transform_file(self.test_file)
        
        # Verify all constructs are properly transformed
        expected_imports = [
            "kinda_import", "maybe_import", "kinda_int", 
            "sometimes", "sorta_print", "ish_value"
        ]
        
        for expected in expected_imports:
            self.assertIn(expected, result)
        
        # Verify specific transformations
        self.assertIn("os = kinda_import('os')", result)
        self.assertIn("x = kinda_int(42)", result)
        self.assertIn("requests = maybe_import('requests', fallback_module='urllib')", result)
        self.assertIn("if sometimes():", result)
        self.assertIn("ish_value(100)", result)
    
    def test_import_with_welp_integration(self):
        """Test import constructs working with welp fallback patterns"""
        content = """# Import with welp integration
~kinda import os
result = os.getcwd() ~welp "/default/path"
~maybe import json ~welp simplejson
data = json.loads('{"test": true}') ~welp {}
"""
        self.test_file.write_text(content)
        
        # Transform the file
        result = transform_file(self.test_file)
        
        # Verify welp integration
        self.assertIn("kinda_import", result)
        self.assertIn("maybe_import", result)
        self.assertIn("welp_fallback", result)
        self.assertIn("os = kinda_import('os')", result)
        self.assertIn("json = maybe_import('json', fallback_module='simplejson')", result)
        self.assertIn("welp_fallback(lambda: os.getcwd(), \"/default/path\")", result)
        self.assertIn("welp_fallback(lambda: json.loads('{\"test\": true}'), {})", result)
    
    def test_nested_import_constructs(self):
        """Test import constructs in nested contexts"""
        content = """# Nested import constructs
~sometimes() {
    ~kinda import sys
    ~maybe import platform ~welp os
}
~maybe() {
    ~kinda import time as t
}
"""
        self.test_file.write_text(content)
        
        # Transform the file
        result = transform_file(self.test_file)
        
        # Verify nested constructs are properly handled
        self.assertIn("if sometimes():", result)
        self.assertIn("if maybe():", result)
        self.assertIn("sys = kinda_import('sys')", result)
        self.assertIn("platform = maybe_import('platform', fallback_module='os')", result)
        self.assertIn("t = kinda_import('time', alias='t')", result)
    
    def test_import_error_handling(self):
        """Test error handling in import transformations"""
        # Test invalid module names
        invalid_content = """~kinda import 123invalid
~maybe import also.123invalid
"""
        self.test_file.write_text(invalid_content)
        
        # These should not match the patterns and pass through as regular Python
        result = transform_file(self.test_file)
        self.assertIn("~kinda import 123invalid", result)
        self.assertIn("~maybe import also.123invalid", result)
    
    def test_personality_integration_with_imports(self):
        """Test that imports work with personality system integration"""
        content = """# Personality integration test
~kinda import os
~kinda import json as j
~maybe import requests ~welp urllib
~sometimes() {
    ~sorta print("Personality test")
}
"""
        self.test_file.write_text(content)
        
        # Mock personality functions
        with patch('kinda.personality.chaos_probability') as mock_prob, \
             patch('kinda.personality.update_chaos_state') as mock_update, \
             patch('kinda.personality.get_personality') as mock_get_pers:
            
            # Set up personality mock
            mock_personality = MagicMock()
            mock_personality.get_error_message_style.return_value = 'friendly'
            mock_get_pers.return_value = mock_personality
            mock_prob.return_value = 0.7
            
            # Transform the file
            result = transform_file(self.test_file)
            
            # Verify transformation includes personality integration
            expected_imports = ["kinda_import", "maybe_import", "sometimes", "sorta_print"]
            for expected in expected_imports:
                self.assertIn(expected, result)
    
    def test_complex_import_scenario(self):
        """Test a complex scenario with multiple import types and usage"""
        content = """# Complex import scenario
~kinda import os
~kinda import json as j
~maybe import requests ~welp urllib
~maybe import numpy as np ~welp math

# Use the imports
~sometimes() {
    path = os.getcwd() ~welp "/tmp"
    data = j.loads('{"key": "value"}') ~welp {}
    
    ~maybe() {
        response = requests.get("http://example.com") ~welp None
        array = np.array([1, 2, 3]) ~welp [1, 2, 3]
    }
}

~sorta print("Complex scenario complete")
"""
        self.test_file.write_text(content)
        
        # Transform the file
        result = transform_file(self.test_file)
        
        # Verify comprehensive transformation
        self.assertIn("os = kinda_import('os')", result)
        self.assertIn("j = kinda_import('json', alias='j')", result)
        self.assertIn("requests = maybe_import('requests', fallback_module='urllib')", result)
        self.assertIn("np = maybe_import('numpy', alias='np', fallback_module='math')", result)
        
        # Verify nested usage with welp
        self.assertIn("welp_fallback(lambda: os.getcwd(), \"/tmp\")", result)
        self.assertIn("welp_fallback(lambda: j.loads('{\"key\": \"value\"}'), {})", result)
        self.assertIn("welp_fallback(lambda: requests.get(\"http://example.com\"), None)", result)
        self.assertIn("welp_fallback(lambda: np.array([1, 2, 3]), [1, 2, 3])", result)
        
        # Verify all helpers are imported
        expected_helpers = ["kinda_import", "maybe_import", "sometimes", "maybe", "sorta_print", "welp_fallback"]
        for helper in expected_helpers:
            self.assertIn(helper, result)
    
    def test_line_by_line_transformation(self):
        """Test individual line transformations for import constructs"""
        test_cases = [
            ("~kinda import os", "os = kinda_import('os')"),
            ("~kinda import json as j", "j = kinda_import('json', alias='j')"),
            ("~maybe import requests", "requests = maybe_import('requests')"),
            ("~maybe import requests as req", "req = maybe_import('requests', alias='req')"),
            ("~maybe import requests ~welp urllib", "requests = maybe_import('requests', fallback_module='urllib')"),
            ("~maybe import requests as req ~welp urllib", "req = maybe_import('requests', alias='req', fallback_module='urllib')"),
        ]
        
        for input_line, expected_output in test_cases:
            with self.subTest(input_line=input_line):
                result = transform_line(input_line)
                self.assertEqual(len(result), 1)
                self.assertIn(expected_output, result[0])
    
    def test_whitespace_and_comments_handling(self):
        """Test that imports handle whitespace and comments properly"""
        test_cases = [
            "   ~kinda import os   ",
            "~kinda import os  # system functions",
            "\t~maybe import requests\t# http library",
            "~maybe import json ~welp simplejson  # JSON parsing",
        ]
        
        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                result = transform_line(test_case)
                self.assertEqual(len(result), 1)
                # Should contain either kinda_import or maybe_import
                self.assertTrue(
                    "kinda_import" in result[0] or "maybe_import" in result[0],
                    f"Expected import function in: {result[0]}"
                )


class TestImportConstructsFileProcessing(unittest.TestCase):
    """Test import constructs in complete file processing scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_multiple_file_transformation(self):
        """Test transforming multiple files with import constructs"""
        # Create multiple test files
        file1_content = """~kinda import os
~sorta print("File 1")"""
        
        file2_content = """~maybe import requests ~welp urllib
~sometimes() {
    ~sorta print("File 2")
}"""
        
        file1 = self.test_dir / "file1.knda"
        file2 = self.test_dir / "file2.knda"
        
        file1.write_text(file1_content)
        file2.write_text(file2_content)
        
        # Transform both files
        result1 = transform_file(file1)
        result2 = transform_file(file2)
        
        # Verify both transformations
        self.assertIn("kinda_import", result1)
        self.assertIn("os = kinda_import('os')", result1)
        
        self.assertIn("maybe_import", result2)
        self.assertIn("requests = maybe_import('requests', fallback_module='urllib')", result2)
    
    def test_import_constructs_with_python_extension(self):
        """Test import constructs in .py.knda files"""
        content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"Module with kinda imports\"\"\"

~kinda import os
~maybe import sys ~welp platform

def main():
    ~sorta print("Main function")
    path = os.getcwd() ~welp "/tmp"
    
if __name__ == "__main__":
    main()
"""
        
        test_file = self.test_dir / "module.py.knda"
        test_file.write_text(content)
        
        # Transform the file
        result = transform_file(test_file)
        
        # Verify Python-style structure is preserved
        self.assertIn("#!/usr/bin/env python3", result)
        self.assertIn("# -*- coding: utf-8 -*-", result)
        self.assertIn('"""Module with kinda imports"""', result)
        self.assertIn("def main():", result)
        self.assertIn('if __name__ == "__main__":', result)
        
        # Verify imports are transformed
        self.assertIn("os = kinda_import('os')", result)
        self.assertIn("sys = maybe_import('sys', fallback_module='platform')", result)
        self.assertIn("welp_fallback(lambda: os.getcwd(), \"/tmp\")", result)


if __name__ == '__main__':
    unittest.main()