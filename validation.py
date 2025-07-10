import json
from pathlib import Path
from typing import Dict, Any
from jsonschema import validate, ValidationError

SCHEMAS_DIR = Path(__file__).parent / 'schemas'

_schema_cache = {}

def _load_schema(intent_type: str) -> Dict[str, Any]:
    if intent_type not in _schema_cache:
        path = SCHEMAS_DIR / f"{intent_type}.json"
        with open(path, 'r') as f:
            _schema_cache[intent_type] = json.load(f)
    return _schema_cache[intent_type]


def validate_intent(intent: Dict[str, Any]) -> None:
    intent_type = intent.get('intent')
    if not intent_type:
        raise ValidationError('intent field missing')
    schema = _load_schema(intent_type)
    validate(instance=intent, schema=schema)
