import importlib.machinery
import importlib.util
import os
import unittest
from unittest import mock

_ARRIVALS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Arrivals")
_loader = importlib.machinery.SourceFileLoader("arrivals", _ARRIVALS_PATH)
_spec = importlib.util.spec_from_file_location("arrivals", _ARRIVALS_PATH, loader=_loader)
arrivals_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(arrivals_module)


ARRIVALS_HTML = """
<html><body>
<table class="arrivals-table">
  <tbody>
    <tr>
      <td class="flight">AA 100</td>
      <td class="airline">American Airlines</td>
      <td class="origin">JFK</td>
      <td class="sched">10:15</td>
      <td class="status">Landed</td>
    </tr>
    <tr>
      <td class="flight">BA 112</td>
      <td class="airline">British Airways</td>
      <td class="origin">LHR</td>
      <td class="sched">11:40</td>
      <td class="status">Delayed</td>
    </tr>
  </tbody>
</table>
</body></html>
"""


class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


class ScrapeJfkArrivalsTest(unittest.TestCase):
    def scrape(self):
        with mock.patch.object(
            arrivals_module.requests, "get", return_value=FakeResponse(ARRIVALS_HTML)
        ) as mocked_get:
            rows = arrivals_module.scrape_jfk_arrivals("https://example.test/arrivals")
        mocked_get.assert_called_once()
        return rows

    def test_parses_every_field(self):
        rows = self.scrape()
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            rows[0],
            {
                "flight": "AA 100",
                "airline": "American Airlines",
                "origin": "JFK",
                "sched": "10:15",
                "status": "Landed",
            },
        )
        self.assertEqual(rows[1]["sched"], "11:40")

    def test_schedule_key_has_no_trailing_period(self):
        rows = self.scrape()
        self.assertIn("sched", rows[0])
        self.assertNotIn("sched.", rows[0])


if __name__ == "__main__":
    unittest.main()
