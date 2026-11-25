from datetime import datetime

from infra.clock.system_clock import SystemClock


def test_system_clock_returns_the_current_moment():  # SCRUM-14
    before = datetime.now()

    moment = SystemClock().now()

    assert before <= moment <= datetime.now()
