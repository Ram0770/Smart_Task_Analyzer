from django.test import TestCase
from .scoring import compute_score, analyze_tasks_list
from datetime import date, timedelta

class ScoringTests(TestCase):
    def test_compute_score_basic(self):
        today = date.today().isoformat()
        t = {
            'title': 'Test',
            'due_date': today,
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': [],
            'done': False
        }
        s = compute_score(t, [t])
        self.assertTrue(s > 0)

    def test_analyze_ordering(self):
        t1 = {'title': 'A', 'due_date': None, 'importance': 10, 'estimated_hours': 5, 'dependencies': [], 'done': False}
        t2 = {'title': 'B', 'due_date': None, 'importance': 1, 'estimated_hours': 1, 'dependencies': [], 'done': False}
        result = analyze_tasks_list([t1, t2])
        self.assertEqual(result[0]['title'], 'A')
