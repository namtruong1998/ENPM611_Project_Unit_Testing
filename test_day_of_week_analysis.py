import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import io
from contextlib import redirect_stdout

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from day_of_week_analysis import DayOfWeekAnalysis
from model import Issue


class TestDayOfWeekAnalysis(unittest.TestCase):
    """
    Unit tests for DayOfWeekAnalysis class
    """

    def _create_issue(self, created_date: str) -> Issue:
        """Helper to create a mock issue with a created_date."""
        issue = Issue()
        issue.created_date = created_date
        return issue

    @patch('day_of_week_analysis.plt.show')
    @patch('day_of_week_analysis.DataLoader')
    def test_run_with_mock_issues_counts_correct(self, mock_loader, mock_show):
        """
        Test run() with mocked issues and verify day-of-week counting.
        """
        # 1 Sunday, 2 Mondays, 1 Wednesday
        mock_issues = [
            self._create_issue("2024-11-03"),  # Sunday
            self._create_issue("2024-11-04"),  # Monday
            self._create_issue("2024-11-11"),  # Monday
            self._create_issue("2024-11-06"),  # Wednesday
        ]

        mock_loader_instance = MagicMock()
        mock_loader_instance.get_issues.return_value = mock_issues
        mock_loader.return_value = mock_loader_instance

        analysis = DayOfWeekAnalysis()

        buf = io.StringIO()
        with redirect_stdout(buf):
            analysis.run()
        output = buf.getvalue()

        # Verify loader used and plot shown
        mock_loader_instance.get_issues.assert_called_once()
        mock_show.assert_called_once()

        # Check counts in printed output
        self.assertIn("Sunday: 1", output)
        self.assertIn("Monday: 2", output)
        self.assertIn("Wednesday: 1", output)

    @patch('day_of_week_analysis.plt.show')
    @patch('day_of_week_analysis.DataLoader')
    def test_run_with_no_issues(self, mock_loader, mock_show):
        """
        Test run() when there are no issues; should not crash.
        """
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_issues.return_value = []
        mock_loader.return_value = mock_loader_instance

        analysis = DayOfWeekAnalysis()

        buf = io.StringIO()
        with redirect_stdout(buf):
            analysis.run()
        output = buf.getvalue()

        mock_loader_instance.get_issues.assert_called_once()
        mock_show.assert_called_once()

        # Header should still be printed, but no day lines
        self.assertIn("Issues created by day of the week:", output)
        # No colon after a day name should appear
        self.assertNotIn("Monday:", output)
        self.assertNotIn("Tuesday:", output)
        self.assertNotIn("Wednesday:", output)
        self.assertNotIn("Thursday:", output)
        self.assertNotIn("Friday:", output)
        self.assertNotIn("Saturday:", output)
        self.assertNotIn("Sunday:", output)

    @patch('day_of_week_analysis.plt.show')
    def test_run_with_real_data_expected_counts(self, mock_show):
        """
        Test run() against the real dataset and verify the expected
        counts for each day of the week.
        """
        expected_counts = {
            "Wednesday": 1044,
            "Saturday": 489,
            "Tuesday": 1071,
            "Monday": 903,
            "Thursday": 1147,
            "Sunday": 449,
            "Friday": 1011,
        }

        analysis = DayOfWeekAnalysis()

        buf = io.StringIO()
        with redirect_stdout(buf):
            analysis.run()
        output = buf.getvalue()

        # Ensure header printed
        self.assertIn("Issues created by day of the week:", output)

        # Each expected "Day: count" should appear somewhere in the output
        for day, count in expected_counts.items():
            line = f"{day}: {count}"
            self.assertIn(line, output, msg=f"Expected line missing: {line}")

        mock_show.assert_called_once()


if __name__ == '__main__':
    unittest.main()
