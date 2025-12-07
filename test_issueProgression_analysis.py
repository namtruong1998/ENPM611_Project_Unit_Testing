import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import io
from contextlib import redirect_stdout

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from issueProgression_analysis import IssueProgressionAnalysis
from model import Issue


class TestIssueProgressionAnalysis(unittest.TestCase):
    """
    Unit tests for IssueProgressionAnalysis class
    """

    def _create_issue(self, created_date: str) -> Issue:
        """Helper to create an Issue with a created_date."""
        issue = Issue()
        issue.created_date = created_date
        return issue

    @patch('issueProgression_analysis.config.get_parameter')
    def test_init_uses_config_user(self, mock_get_parameter):
        """Test that __init__ reads USER from config."""
        mock_get_parameter.return_value = "test_user"

        analysis = IssueProgressionAnalysis()

        self.assertEqual(analysis.USER, "test_user")
        mock_get_parameter.assert_called_once_with("user")

    @patch('issueProgression_analysis.plt.show')
    @patch('issueProgression_analysis.DataLoader')
    @patch('issueProgression_analysis.config.get_parameter')
    def test_run_with_mock_issues_counts_correct(
        self, mock_get_parameter, mock_loader, mock_show
    ):
        """
        Test run() with mocked issues and verify month counting logic.
        """
        mock_get_parameter.return_value = "test_user"

        # 3 issues in January, 2 in February, 1 in March
        mock_issues = [
            self._create_issue("2024-01-05"),
            self._create_issue("2024-01-10"),
            self._create_issue("2024-01-20"),
            self._create_issue("2024-02-01"),
            self._create_issue("2024-02-15"),
            self._create_issue("2024-03-03"),
        ]

        mock_loader_instance = MagicMock()
        mock_loader_instance.get_issues.return_value = mock_issues
        mock_loader.return_value = mock_loader_instance

        analysis = IssueProgressionAnalysis()

        buf = io.StringIO()
        with redirect_stdout(buf):
            analysis.run()
        output = buf.getvalue()

        # Loader and plotting called
        mock_loader_instance.get_issues.assert_called_once()
        mock_show.assert_called_once()

        # Check that the printed Series contains the right counts
        self.assertRegex(output, r"January\s+3\b")
        self.assertRegex(output, r"February\s+2\b")
        self.assertRegex(output, r"March\s+1\b")

    @patch('issueProgression_analysis.plt.show')
    @patch('issueProgression_analysis.DataLoader')
    @patch('issueProgression_analysis.config.get_parameter')
    def test_run_with_no_issues_handles_gracefully(
        self, mock_get_parameter, mock_loader, mock_show
    ):
        """
        Previously, run() crashed with KeyError('created_date') when there were no issues.
        This test verifies that case is now handled gracefully.
        """
        mock_get_parameter.return_value = "test_user"

        mock_loader_instance = MagicMock()
        mock_loader_instance.get_issues.return_value = []
        mock_loader.return_value = mock_loader_instance

        analysis = IssueProgressionAnalysis()

        buf = io.StringIO()
        with redirect_stdout(buf):
            analysis.run()
        output = buf.getvalue()

        mock_loader_instance.get_issues.assert_called_once()

        # Short message instead of a crash shows the bug is fixed
        self.assertIn("Issue counts by month:", output)
        self.assertIn("No issues found.", output)

        # With no data, we don't expect a plot
        mock_show.assert_not_called()

    @patch('issueProgression_analysis.plt.show')
    def test_run_with_real_data_expected_counts(self, mock_show):
        """
        Test run() against the real dataset and verify the expected
        issue counts per month.
        """
        expected_counts = {
            "January": 584,
            "February": 515,
            "March": 501,
            "April": 396,
            "May": 447,
            "June": 468,
            "July": 494,
            "August": 509,
            "September": 543,
            "October": 655,
            "November": 540,
            "December": 462,
        }

        analysis = IssueProgressionAnalysis()

        buf = io.StringIO()
        with redirect_stdout(buf):
            analysis.run()
        output = buf.getvalue()

        # Ensure header and dtype line are present
        self.assertIn("Issue counts by month:", output)
        self.assertIn("dtype: int64", output)

        # Each expected "Month  count" should appear somewhere in the output
        for month, count in expected_counts.items():
            pattern = rf"{month}\s+{count}\b"
            self.assertRegex(
                output,
                pattern,
                msg=f"Expected line with {month} {count} not found in output",
            )

        mock_show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
