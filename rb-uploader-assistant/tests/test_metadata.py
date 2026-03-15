from app.services.metadata_pipeline import generate_metadata, validate_metadata
from pathlib import Path


def test_generate_metadata_has_valid_shape():
    meta = generate_metadata(Path('sample-cat-design.png'), niche='cats')
    assert 20 <= len(meta['title']) <= 80
    assert meta['description']
    assert 10 <= len(meta['tags']) <= 20
    assert len(meta['tags']) == len(set(meta['tags']))


def test_validate_metadata_rejects_bad_input():
    errors = validate_metadata({'title': 'short', 'description': '', 'tags': ['a']})
    assert errors
