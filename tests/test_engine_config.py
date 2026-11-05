from analysis import engine_config as ec

STARTED = (
    "(APIServer pid=1) INFO 11-04 13:42:08 [api_utils.py:286] non-default args: {'model_tag': 'Qwen/Qwen3-4B', "
    "'enable_prompt_tokens_details': True, 'host': '127.0.0.1', 'model': 'Qwen/Qwen3-4B', "
    "'enable_prefix_caching': False, 'kv_cache_metrics': True, 'max_num_seqs': 256}\n"
    "(EngineCore pid=2) INFO 11-04 13:42:21 [core.py:133] Initializing a V1 LLM engine (v0.32.0) with config: "
    "model='Qwen/Qwen3-4B', speculative_config=None, max_seq_len=40960, enable_prefix_caching=False, "
    "enable_chunked_prefill=True, compilation_config={'mode': 3, 'compile_ranges_endpoints': [2048], "
    "'cudagraph_capture_sizes': [1, 2]}\n"
)


def _run(tmp_path, name, text):
    d = tmp_path / name
    d.mkdir()
    if text is not None:
        (d / "server.log").write_text(text)
    return d


def test_engine_settings_reads_the_logged_config(tmp_path):
    s = ec.engine_settings(_run(tmp_path, "r1", STARTED))
    assert s["started"] and s["vllm"] == "0.32.0" and s["model"] == "Qwen/Qwen3-4B"
    assert s["chunked_prefill"] is True
    assert s["compile_ranges_endpoints"] == [2048]
    assert s["scheduler_overrides"] == []  # max_num_seqs is not a scheduler-budget flag in SCHEDULER_ARGS
    assert s["async_off_warning"] is False


def test_override_warning_and_unstarted_runs_are_flagged(tmp_path):
    text = STARTED.replace("'max_num_seqs': 256}", "'max_num_seqs': 256, 'max_num_batched_tokens': 8192}")
    text += "(EngineCore pid=2) WARNING Async scheduling will be disabled because it is not supported with x.\n"
    s = ec.engine_settings(_run(tmp_path, "r2", text))
    assert s["scheduler_overrides"] == ["max_num_batched_tokens"]
    assert s["async_off_warning"] is True
    failed = ec.engine_settings(_run(tmp_path, "r3", "taskset: failed to execute vllm: No such file or directory\n"))
    assert failed["started"] is False and failed["chunked_prefill"] is None
    missing = ec.engine_settings(_run(tmp_path, "r4", None))
    assert missing["started"] is False


def test_a10_table_counts(tmp_path):
    _run(tmp_path, "a", STARTED)
    _run(tmp_path, "b", STARTED)
    _run(tmp_path, "c", "taskset: failed to execute vllm\n")
    t = dict(ec.a10_table(tmp_path).values)
    assert t["run folders"] == 3 and t["started a server (engine config logged)"] == 2
    assert t["not started"] == "c"
    assert t["compile_ranges_endpoints"] == {"[2048]": 2}
    assert t["runs with a scheduler flag in non-default args"] == 0
    assert t["runs that logged an async-scheduling-off warning"] == 0
