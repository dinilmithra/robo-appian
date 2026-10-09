from types import SimpleNamespace

from robo_appian import (
    AppianRuntime,
    RoboAppianError,
    automation_context_for,
    automation_test_log_path,
)


def test_appian_runtime_is_public_boundary_without_exposing_lower_types() -> None:
    runtime = AppianRuntime(object(), None, wait_time_seconds=45)
    assert runtime.wait_time_seconds == 45
    assert runtime.measure("example") is not None


def test_automation_context_for_reads_pytest_correlation_metadata() -> None:
    item = SimpleNamespace(
        nodeid="tests/test_example.py::test_example",
        _robo_test_case_id="TC-1",
        _robo_process_id="PR-1",
        _robo_attempt_id="A1",
        _robo_testcase_log_path="logs/test.log",
    )
    context = automation_context_for(item)
    assert context.test_case_id == "TC-1"
    assert context.process_id == "PR-1"
    assert context.attempt_id == "A1"
    assert automation_test_log_path(item) == "logs/test.log"


def test_core_can_use_robo_appian_error_boundary() -> None:
    error = RoboAppianError("failure", code="APP_TEST")
    assert error.code == "APP_TEST"
