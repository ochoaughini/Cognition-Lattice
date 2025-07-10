import pytest
from jsonschema.exceptions import ValidationError

from validation import validate_intent


def test_validate_echo_success():
    intent = {"intent": "echo", "args": "hi", "intent_id": "123"}
    validate_intent(intent)


def test_validate_echo_missing_field():
    with pytest.raises(ValidationError):
        validate_intent({"intent": "echo"})


def test_validate_echo_extra_field():
    with pytest.raises(ValidationError):
        validate_intent({"intent": "echo", "intent_id": "1", "extra": 1})
