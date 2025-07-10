import json
from pathlib import Path
from intent_gateway import IntentModel


def test_schemas_match_intent_model():
    model_fields = set(IntentModel.model_fields.keys())
    for path in Path('schemas').glob('*.json'):
        schema = json.loads(path.read_text())
        schema_fields = set(schema.get('properties', {}).keys())
        assert schema_fields.issubset(model_fields)
