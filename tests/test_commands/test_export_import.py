from srl.commands import export, import_
from types import SimpleNamespace
import json
import tempfile
from pathlib import Path


def test_export_full_data(mock_data, console, dump_json, load_json):
    """Test exporting all data types."""
    # Setup test data
    progress_data = {
        "Two Sum": {
            "history": [{"rating": 4, "date": "2024-01-01"}],
            "leetcode_id": "1"
        }
    }
    mastered_data = {
        "Valid Parentheses": {
            "history": [{"rating": 5, "date": "2024-01-02"}],
            "leetcode_id": "20"
        }
    }
    nextup_data = {"Reverse Linked List": {"added": "2024-01-03"}}
    
    dump_json(mock_data.PROGRESS_FILE, progress_data)
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    dump_json(mock_data.NEXT_UP_FILE, nextup_data)
    
    # Export data
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = Path(tmp_dir) / "export.json"
        args = SimpleNamespace(
            output=str(output_file),
            include_config=False,
            include_audit=False,
            mastered_only=False,
            progress_only=False
        )
        export.handle(args, console)
        
        # Verify export file
        with open(output_file, 'r') as f:
            exported = json.load(f)
        
        assert "exported_at" in exported
        assert exported["srl_version"] == "1.0.0"
        assert exported["export_type"] == "full"
        
        assert exported["data"]["problems_in_progress"] == progress_data
        assert exported["data"]["problems_mastered"] == mastered_data
        assert exported["data"]["next_up"] == nextup_data


def test_export_mastered_only(mock_data, console, dump_json):
    """Test exporting only mastered problems."""
    mastered_data = {
        "Valid Parentheses": {
            "history": [{"rating": 5, "date": "2024-01-01"}],
            "leetcode_id": "20"
        }
    }
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    dump_json(mock_data.PROGRESS_FILE, {"Some Problem": {"history": []}})
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = Path(tmp_dir) / "export.json"
        args = SimpleNamespace(
            output=str(output_file),
            include_config=False,
            include_audit=False,
            mastered_only=True,
            progress_only=False
        )
        export.handle(args, console)
        
        with open(output_file, 'r') as f:
            exported = json.load(f)
        
        assert exported["export_type"] == "mastered_only"
        assert exported["data"]["problems_mastered"] == mastered_data
        assert "problems_in_progress" not in exported["data"]
        assert "next_up" not in exported["data"]


def test_export_progress_only(mock_data, console, dump_json):
    """Test exporting only problems in progress."""
    progress_data = {
        "Two Sum": {
            "history": [{"rating": 4, "date": "2024-01-01"}],
            "leetcode_id": "1"
        }
    }
    dump_json(mock_data.PROGRESS_FILE, progress_data)
    dump_json(mock_data.MASTERED_FILE, {"Some Mastered": {"history": []}})
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = Path(tmp_dir) / "export.json"
        args = SimpleNamespace(
            output=str(output_file),
            include_config=False,
            include_audit=False,
            mastered_only=False,
            progress_only=True
        )
        export.handle(args, console)
        
        with open(output_file, 'r') as f:
            exported = json.load(f)
        
        assert exported["export_type"] == "progress_only"
        assert exported["data"]["problems_in_progress"] == progress_data
        assert "problems_mastered" not in exported["data"]
        assert "next_up" not in exported["data"]


def test_export_with_config_and_audit(mock_data, console, dump_json):
    """Test exporting with config and audit data."""
    config_data = {"audit_probability": 0.1}
    audit_data = {"history": [{"date": "2024-01-01", "problem": "Test", "result": "pass"}]}
    
    dump_json(mock_data.CONFIG_FILE, config_data)
    dump_json(mock_data.AUDIT_FILE, audit_data)
    dump_json(mock_data.PROGRESS_FILE, {})
    dump_json(mock_data.MASTERED_FILE, {})
    dump_json(mock_data.NEXT_UP_FILE, {})
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = Path(tmp_dir) / "export.json"
        args = SimpleNamespace(
            output=str(output_file),
            include_config=True,
            include_audit=True,
            mastered_only=False,
            progress_only=False
        )
        export.handle(args, console)
        
        with open(output_file, 'r') as f:
            exported = json.load(f)
        
        assert exported["data"]["config"] == config_data
        assert exported["data"]["audit"] == audit_data


def test_import_full_data(mock_data, console, load_json):
    """Test importing complete data set."""
    # Create import data
    import_data = {
        "exported_at": "2024-01-01T10:00:00",
        "srl_version": "1.0.0",
        "export_type": "full",
        "data": {
            "problems_in_progress": {
                "Two Sum": {
                    "history": [{"rating": 4, "date": "2024-01-01"}],
                    "leetcode_id": "1"
                }
            },
            "problems_mastered": {
                "Valid Parentheses": {
                    "history": [{"rating": 5, "date": "2024-01-02"}],
                    "leetcode_id": "20"
                }
            },
            "next_up": {
                "Reverse Linked List": {"added": "2024-01-03"}
            }
        }
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        import_file = Path(tmp_dir) / "import.json"
        with open(import_file, 'w') as f:
            json.dump(import_data, f)
        
        args = SimpleNamespace(
            file=str(import_file),
            merge=False,
            dry_run=False,
            force=True
        )
        import_.handle(args, console)
        
        # Verify imported data
        progress = load_json(mock_data.PROGRESS_FILE)
        mastered = load_json(mock_data.MASTERED_FILE)
        nextup = load_json(mock_data.NEXT_UP_FILE)
        
        assert progress == import_data["data"]["problems_in_progress"]
        assert mastered == import_data["data"]["problems_mastered"]
        assert nextup == import_data["data"]["next_up"]


def test_import_merge_mode(mock_data, console, dump_json, load_json):
    """Test importing with merge mode."""
    # Setup existing data
    existing_progress = {"Existing Problem": {"history": [{"rating": 3}]}}
    dump_json(mock_data.PROGRESS_FILE, existing_progress)
    
    # Import data
    import_data = {
        "exported_at": "2024-01-01T10:00:00",
        "srl_version": "1.0.0",
        "export_type": "full",
        "data": {
            "problems_in_progress": {
                "Two Sum": {
                    "history": [{"rating": 4, "date": "2024-01-01"}],
                    "leetcode_id": "1"
                }
            },
            "problems_mastered": {},
            "next_up": {}
        }
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        import_file = Path(tmp_dir) / "import.json"
        with open(import_file, 'w') as f:
            json.dump(import_data, f)
        
        args = SimpleNamespace(
            file=str(import_file),
            merge=True,
            dry_run=False,
            force=True
        )
        import_.handle(args, console)
        
        # Verify merged data
        progress = load_json(mock_data.PROGRESS_FILE)
        assert "Existing Problem" in progress  # Original data preserved
        assert "Two Sum" in progress  # New data added
        assert len(progress) == 2


def test_import_dry_run(mock_data, console, load_json):
    """Test import dry run mode."""
    original_data = {"Original": {"history": []}}
    with open(mock_data.PROGRESS_FILE, 'w') as f:
        json.dump(original_data, f)
    
    import_data = {
        "exported_at": "2024-01-01T10:00:00",
        "srl_version": "1.0.0",
        "export_type": "full",
        "data": {
            "problems_in_progress": {"New Problem": {"history": []}},
            "problems_mastered": {},
            "next_up": {}
        }
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        import_file = Path(tmp_dir) / "import.json"
        with open(import_file, 'w') as f:
            json.dump(import_data, f)
        
        args = SimpleNamespace(
            file=str(import_file),
            merge=False,
            dry_run=True,
            force=True
        )
        import_.handle(args, console)
        
        # Verify no changes were made
        progress = load_json(mock_data.PROGRESS_FILE)
        assert progress == original_data
        
        output = console.export_text()
        assert "Dry run complete" in output


def test_import_invalid_file(console):
    """Test importing non-existent file."""
    args = SimpleNamespace(
        file="nonexistent.json",
        merge=False,
        dry_run=False,
        force=True
    )
    import_.handle(args, console)
    
    output = console.export_text()
    assert "File nonexistent.json not found" in output


def test_import_invalid_json(console):
    """Test importing malformed JSON."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        import_file = Path(tmp_dir) / "invalid.json"
        with open(import_file, 'w') as f:
            f.write("invalid json content")
        
        args = SimpleNamespace(
            file=str(import_file),
            merge=False,
            dry_run=False,
            force=True
        )
        import_.handle(args, console)
        
        output = console.export_text()
        assert "Invalid JSON file" in output


def test_export_creates_directory(console, mock_data, dump_json):
    """Test that export creates output directory if it doesn't exist."""
    # Setup minimal data
    dump_json(mock_data.PROGRESS_FILE, {})
    dump_json(mock_data.MASTERED_FILE, {})
    dump_json(mock_data.NEXT_UP_FILE, {})
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "subdir" / "export.json"
        
        args = SimpleNamespace(
            output=str(output_path),
            include_config=False,
            include_audit=False,
            mastered_only=False,
            progress_only=False
        )
        export.handle(args, console)
        
        # Verify file was created
        assert output_path.exists()
        
        # Verify it's valid JSON
        with open(output_path, 'r') as f:
            data = json.load(f)
        assert "exported_at" in data


def test_roundtrip_export_import(mock_data, console, dump_json, load_json):
    """Test that export->import preserves all data."""
    # Setup comprehensive test data
    progress_data = {
        "Two Sum": {
            "history": [
                {"rating": 3, "date": "2024-01-01", "note": "Used hashmap"},
                {"rating": 5, "date": "2024-01-02", "time": "15 mins"}
            ],
            "leetcode_id": "1"
        }
    }
    mastered_data = {
        "Valid Parentheses": {
            "history": [
                {"rating": 4, "date": "2024-01-01"},
                {"rating": 5, "date": "2024-01-02"}
            ],
            "leetcode_id": "20"
        }
    }
    nextup_data = {"Reverse Linked List": {"added": "2024-01-03"}}
    
    dump_json(mock_data.PROGRESS_FILE, progress_data)
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    dump_json(mock_data.NEXT_UP_FILE, nextup_data)
    
    # Export
    with tempfile.TemporaryDirectory() as tmp_dir:
        export_file = Path(tmp_dir) / "export.json"
        export_args = SimpleNamespace(
            output=str(export_file),
            include_config=False,
            include_audit=False,
            mastered_only=False,
            progress_only=False
        )
        export.handle(export_args, console)
        
        # Clear data
        dump_json(mock_data.PROGRESS_FILE, {})
        dump_json(mock_data.MASTERED_FILE, {})
        dump_json(mock_data.NEXT_UP_FILE, {})
        
        # Import
        import_args = SimpleNamespace(
            file=str(export_file),
            merge=False,
            dry_run=False,
            force=True
        )
        import_.handle(import_args, console)
        
        # Verify data integrity
        new_progress = load_json(mock_data.PROGRESS_FILE)
        new_mastered = load_json(mock_data.MASTERED_FILE)
        new_nextup = load_json(mock_data.NEXT_UP_FILE)
        
        assert new_progress == progress_data
        assert new_mastered == mastered_data
        assert new_nextup == nextup_data