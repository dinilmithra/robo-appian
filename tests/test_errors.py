from robo_appian import RoboAppianError
from robo_automation import RoboAutomationError


def test_robo_appian_error_is_robo_automation_error():
    error = RoboAppianError(
        "Could not select Appian option",
        details={"label": "Request Type", "value": "Conference"},
    )

    assert isinstance(error, RoboAutomationError)
    assert error.code == "ROBO_APPIAN_ERROR"
    assert error.details["label"] == "Request Type"
