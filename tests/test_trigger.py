import time

import pytest

from harness import trigger


def fire(trig, results):
    """Run fire() with a fake HTTP call; returns the urls called and the records written."""
    urls, recs = [], []

    def post(url, timeout_s):
        urls.append(url)
        return results(len(urls))

    orig, trigger._post = trigger._post, post
    try:
        trigger.fire(trig, "http://x", time.monotonic(), recs.append)
    finally:
        trigger._post = orig
    return urls, recs


PREEMPT = {"at_s": 0, "mode": "preempt", "request_timeout_s": 1}
IDLE = {"at_s": 0, "mode": "idle", "request_timeout_s": 1, "retry_interval_s": 0.001, "max_wait_s": 0.05}
FAILED, OK = {"status": 200, "success": False}, {"status": 200, "success": True}


def test_preempt_calls_once_with_the_flag_even_if_it_fails():
    urls, recs = fire(PREEMPT, lambda n: FAILED)
    assert urls == ["http://x/reset_prefix_cache?reset_running_requests=true"] and len(recs) == 1


def test_idle_never_sends_the_flag_and_stops_at_first_success():
    urls, recs = fire(IDLE, lambda n: OK if n == 3 else FAILED)
    assert set(urls) == {"http://x/reset_prefix_cache"} and [r["success"] for r in recs] == [False, False, True]


def test_idle_gives_up_at_max_wait():
    t = time.monotonic()
    _, recs = fire(IDLE, lambda n: FAILED)
    assert not any(r["success"] for r in recs) and time.monotonic() - t < 1


def test_idle_stops_on_an_http_error():
    urls, _ = fire(IDLE, lambda n: {"status": 500, "success": False, "error": "x"})
    assert len(urls) == 1


def cfg(**trig):
    return {"name": "x", "workload": {"warmup_s": 240, "duration_s": 3000},
            "server": {"env": {trigger.DEV_MODE_ENV: "1"}},
            "trigger": {"kind": "cache_wipe", "mode": "preempt", "at_s": 1200, **trig}}


def test_validate_accepts_a_good_trigger():
    trigger.validate(cfg())


@pytest.mark.parametrize("bad", [{"kind": "burst"}, {"mode": "other"}, {"at_s": 100}, {"at_s": 3000},
                                 {"mode": "idle", "max_wait_s": 1800}])
def test_validate_rejects(bad):
    with pytest.raises(SystemExit):
        trigger.validate(cfg(**bad))


def test_validate_requires_dev_mode():
    c = cfg()
    c["server"]["env"] = {}
    with pytest.raises(SystemExit):
        trigger.validate(c)
