import timeit

setup = """
from datetime import datetime, timedelta

class MockSession:
    def __init__(self, last_active):
        self.last_active = last_active

sessions = [MockSession(datetime.now()) for _ in range(1000)]
"""

test_current = """
response_list = []
for s in sessions:
    is_today = s.last_active.date() == datetime.now().date()
    is_yesterday = s.last_active.date() == (datetime.now().date() - timedelta(days=1))
    response_list.append((is_today, is_yesterday))
"""

test_optimized = """
response_list = []
current_date = datetime.now().date()
yesterday_date = current_date - timedelta(days=1)
for s in sessions:
    is_today = s.last_active.date() == current_date
    is_yesterday = s.last_active.date() == yesterday_date
    response_list.append((is_today, is_yesterday))
"""

print("Current:", timeit.timeit(test_current, setup=setup, number=1000))
print("Optimized:", timeit.timeit(test_optimized, setup=setup, number=1000))
