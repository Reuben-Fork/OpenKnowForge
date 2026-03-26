from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import api.ingestors.note_ingestor as note_ingestor
from api.main import app


def _override_paths(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    docs_dir = root / 'docs'
    notes_dir = docs_dir / 'notes'
    images_dir = docs_dir / 'assets' / 'images'
    public_dir = docs_dir / '.vitepress' / 'public'

    monkeypatch.setattr(note_ingestor, 'ROOT_DIR', root)
    monkeypatch.setattr(note_ingestor, 'DOCS_DIR', docs_dir)
    monkeypatch.setattr(note_ingestor, 'NOTES_DIR', notes_dir)
    monkeypatch.setattr(note_ingestor, 'IMAGES_DIR', images_dir)
    monkeypatch.setattr(note_ingestor, 'PUBLIC_DIR', public_dir)
    monkeypatch.setattr(note_ingestor, 'NOTES_INDEX_PATH', notes_dir / 'index.md')
    monkeypatch.setattr(note_ingestor, 'SEARCH_INDEX_PATH', public_dir / 'search-index.json')


def _disable_git_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_commit(self: note_ingestor.NoteIngestor, slug: str) -> dict[str, object]:
        return {'committed': False, 'message': f'disabled in test for {slug}'}

    monkeypatch.setattr(note_ingestor.NoteIngestor, '_git_commit', fake_commit)


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    _override_paths(monkeypatch, tmp_path)
    _disable_git_commit(monkeypatch)
    return TestClient(app)


def test_post_note_creates_markdown_assets_and_indexes(client: TestClient, tmp_path: Path) -> None:
    image_bytes = b'unit-test-image'
    image_data_url = 'data:image/png;base64,' + base64.b64encode(image_bytes).decode('ascii')

    response = client.post(
        '/note',
        json={
            'title': 'Graph Theory',
            'content': 'Graphs model relationships.',
            'tags': ['math', 'graph'],
            'images': [image_data_url],
            'type': 'concept',
            'status': 'draft',
            'related': ['combinatorics'],
        },
    )

    assert response.status_code == 200
    payload = response.json()['result']
    slug = payload['slug']

    note_path = tmp_path / payload['note_path']
    assert note_path.exists()
    note_text = note_path.read_text(encoding='utf-8')
    assert '# Graph Theory' in note_text
    assert 'title: Graph Theory' in note_text
    assert '<img src="/assets/images/' in note_text
    assert f'/notes/{slug}' in (tmp_path / 'docs' / 'notes' / 'index.md').read_text(encoding='utf-8')

    image_files = list((tmp_path / 'docs' / 'assets' / 'images').glob('*.png'))
    assert len(image_files) == 1

    search_index_path = tmp_path / 'docs' / '.vitepress' / 'public' / 'search-index.json'
    assert search_index_path.exists()
    search_index = json.loads(search_index_path.read_text(encoding='utf-8'))
    assert search_index['notes'][0]['title'] == 'Graph Theory'
    assert 'math' in search_index['notes'][0]['tags']


def test_post_note_rejects_invalid_image_payload(client: TestClient) -> None:
    response = client.post(
        '/note',
        json={
            'title': 'Broken Image Note',
            'content': 'content',
            'tags': [],
            'images': ['not-a-valid-image-format'],
            'type': 'note',
            'status': 'draft',
            'related': [],
        },
    )

    assert response.status_code == 400
    assert 'images entries must be data URLs' in response.json()['detail']


def test_post_note_empty_title_fails_validation(client: TestClient) -> None:
    response = client.post(
        '/note',
        json={
            'title': '',
            'content': 'content',
            'tags': [],
            'images': [],
            'type': 'note',
            'status': 'draft',
            'related': [],
        },
    )

    assert response.status_code == 422
