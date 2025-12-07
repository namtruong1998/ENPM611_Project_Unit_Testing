import unittest
from unittest.mock import patch
import sys
import os
import io
from contextlib import redirect_stdout

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wordCount_analysis import WordCountAnalysis


class TestWordCountAnalysis(unittest.TestCase):
    """
    Unit tests for WordCountAnalysis class
    """

    @patch('wordCount_analysis.plt.show')
    @patch('builtins.input', side_effect=['100', '100'])
    def test_run_with_real_data_100_limits(self, mock_input, mock_show):
        """
        Test run() using the real dataset when both limits are set to 100.
        Verifies that the printed describe() output matches the expected stats.
        """
        expected_lines = {
            "header": "Word Count vs Resolution Time",
            "columns": "word_count  resolve_time_days",
            "count":  r"count\s+402\.000000\s+402\.000000",
            "mean":   r"mean\s+59\.664179\s+11\.716418",
            "std":    r"std\s+27\.277171\s+22\.888087",
            "min":    r"min\s+0\.000000\s+0\.000000",
            "p25":    r"25%\s+40\.000000\s+0\.000000",
            "p50":    r"50%\s+62\.500000\s+0\.000000",
            "p75":    r"75%\s+82\.000000\s+10\.750000",
            "max":    r"max\s+100\.000000\s+99\.000000",
        }

        analysis = WordCountAnalysis()

        buf = io.StringIO()
        with redirect_stdout(buf):
            analysis.run()
        output = buf.getvalue()

        # Basic header / column checks
        self.assertIn(expected_lines["header"], output)
        self.assertIn(expected_lines["columns"], output)

        # Detailed stats checks using regex so spacing doesn't have to be exact
        import re
        self.assertRegex(output, expected_lines["count"])
        self.assertRegex(output, expected_lines["mean"])
        self.assertRegex(output, expected_lines["std"])
        self.assertRegex(output, expected_lines["min"])
        self.assertRegex(output, expected_lines["p25"])
        self.assertRegex(output, expected_lines["p50"])
        self.assertRegex(output, expected_lines["p75"])
        self.assertRegex(output, expected_lines["max"])

        # Make sure the plot is still called
        mock_show.assert_called_once()

    @patch('wordCount_analysis.plt.show')
    @patch('builtins.input', side_effect=['abc', '100', 'notnum', '100'])
    def test_input_validation_loops(self, mock_input, mock_show):
        """
        Test that invalid inputs hit the ValueError branches in both while loops.
        First input for each loop is invalid (non-numeric), second is valid.
        """
        analysis = WordCountAnalysis()

        buf = io.StringIO()
        with redirect_stdout(buf):
            analysis.run()
        output = buf.getvalue()

        # We should have printed the validation error message at least twice
        self.assertIn("Please enter a valid number.", output)

        # Ensure plot still called (so rest of run() executes)
        mock_show.assert_called_once()


if __name__ == '__main__':
    unittest.main()
