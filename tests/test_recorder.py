"""harness.recorder.LagTail must never crash on, or consume, a half-written line of requests.jsonl (open question A14)."""
import json

from harness.recorder import LagTail


def line(tp, ts):
    return json.dumps({"t_planned": tp, "t_sent": ts}) + "\n"


def test_partial_line_is_left_for_the_next_read(tmp_path):
    p = tmp_path / "requests.jsonl"
    full, nxt = line(0.0, 0.1), line(1.0, 1.5)
    p.write_text(full + nxt[:10])                       # the writer is partway through the second line
    tail = LagTail(p)
    assert tail.recent_max() == 0.1
    with open(p, "a") as f:
        f.write(nxt[10:])                               # ... and finishes it
    assert tail.recent_max() == 0.5                     # read whole, not from the middle
    assert tail.bad_lines == 0


def test_no_complete_line_yet(tmp_path):
    p = tmp_path / "requests.jsonl"
    p.write_text('{"t_planned": 0')
    tail = LagTail(p)
    assert tail.recent_max() is None and tail.pos == 0


def test_bad_complete_line_is_skipped_and_counted(tmp_path):
    p = tmp_path / "requests.jsonl"
    p.write_text(line(0.0, 0.2) + "{not json\n" + line(1.0, 1.1))
    tail = LagTail(p)
    assert tail.recent_max() == 0.2 and tail.bad_lines == 1


def test_unsent_requests_and_missing_file(tmp_path):
    p = tmp_path / "requests.jsonl"
    assert LagTail(p).recent_max() is None
    p.write_text(json.dumps({"t_planned": 0.0, "t_sent": None}) + "\n")
    assert LagTail(p).recent_max() is None
