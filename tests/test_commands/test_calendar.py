from srl.commands import calendar
import pytest
from types import SimpleNamespace
from unittest.mock import patch
from datetime import date


@pytest.fixture
def audit_data_pass_fail():
    return {
        "history": [
            {"date": "2024-06-06", "problem": "problem3", "result": "pass"},
            {"date": "2024-06-07", "problem": "problem3", "result": "fail"},
            {"date": "2024-06-08", "problem": "problem3", "result": "pass"},
        ]
    }


@pytest.fixture
def mastered_data():
    return {
        "problem1": {
            "history": [
                {"rating": 3, "date": "2024-06-01"},
                {"rating": 5, "date": "2024-06-02"},
            ]
        },
        "problem2": {
            "history": [
                {"rating": 3, "date": "2024-06-01"},
                {"rating": 4, "date": "2024-06-03"},
            ]
        },
    }


@pytest.fixture
def inprogress_data():
    return {
        "problem3": {
            "history": [
                {"rating": 5, "date": "2024-06-04"},
                {"rating": 5, "date": "2024-06-05"},
            ]
        }
    }


def test_get_audit_dates(mock_data, dump_json, audit_data_pass_fail):
    dump_json(mock_data.AUDIT_FILE, audit_data_pass_fail)

    result = calendar.get_audit_dates()

    assert result == ["2024-06-06", "2024-06-08"]


def test_get_dates(mock_data, dump_json, mastered_data):
    dump_json(mock_data.MASTERED_FILE, mastered_data)

    result = calendar.get_dates(mock_data.MASTERED_FILE)

    assert result == ["2024-06-01", "2024-06-02", "2024-06-01", "2024-06-03"]


def test_get_all_date_counts(
    mock_data,
    dump_json,
    audit_data_pass_fail,
    mastered_data,
    inprogress_data,
):
    dump_json(mock_data.AUDIT_FILE, audit_data_pass_fail)
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    dump_json(mock_data.PROGRESS_FILE, inprogress_data)

    result = calendar.get_all_date_counts()

    assert result["2024-06-01"] == 2  # Two history entries from mastered data
    assert result["2024-06-02"] == 1
    assert result["2024-06-03"] == 1
    assert result["2024-06-04"] == 1
    assert result["2024-06-05"] == 1
    assert result["2024-06-06"] == 1  # audit pass
    assert result["2024-06-08"] == 1  # audit pass
    assert "2024-06-07" not in result  # audit fail, should not be included


def test_handle_single_month_header(mock_data, console):
    """Test calendar shows correct header for single month"""
    args = SimpleNamespace(months=1, summary=False)
    
    with patch('srl.commands.calendar.date') as mock_date:
        mock_date.today.return_value = date(2025, 12, 14)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        calendar.handle(args, console)
        
        output = console.export_text()
        assert "December 2025" in output


def test_handle_multiple_months_same_year_header(mock_data, console):
    """Test calendar shows correct header for multiple months in same year"""
    args = SimpleNamespace(months=3, summary=False)
    
    with patch('srl.commands.calendar.date') as mock_date:
        mock_date.today.return_value = date(2025, 12, 14)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        calendar.handle(args, console)
        
        output = console.export_text()
        assert "Oct - December 2025" in output


def test_handle_cross_year_header(mock_data, console):
    """Test calendar shows correct header for cross-year range"""
    args = SimpleNamespace(months=15, summary=False)
    
    with patch('srl.commands.calendar.date') as mock_date:
        mock_date.today.return_value = date(2025, 12, 14)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        calendar.handle(args, console)
        
        output = console.export_text()
        assert "October 2024 - December 2025" in output


def test_handle_default_twelve_months_header(mock_data, console):
    """Test calendar shows correct header for default 12 months"""
    args = SimpleNamespace(months=12, summary=False)
    
    with patch('srl.commands.calendar.date') as mock_date:
        mock_date.today.return_value = date(2025, 12, 14)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        calendar.handle(args, console)
        
        output = console.export_text()
        assert "Jan - December 2025" in output


def test_handle_includes_legend(mock_data, console):
    """Test calendar includes the legend"""
    args = SimpleNamespace(months=1, summary=False)
    
    calendar.handle(args, console)
    
    output = console.export_text()
    assert "Less" in output
    assert "More" in output
    assert "-----" in output


def test_handle_includes_summary(mock_data, console):
    """Test calendar includes activity summary when requested"""
    args = SimpleNamespace(months=1, summary=True)
    
    calendar.handle(args, console)
    
    output = console.export_text()
    # Should include some summary text when summary=True
    assert ("problems solved" in output or "No activity" in output)


def test_handle_excludes_summary_by_default(mock_data, console):
    """Test calendar excludes summary by default"""
    args = SimpleNamespace(months=1, summary=False)
    
    calendar.handle(args, console)
    
    output = console.export_text()
    # Should NOT include summary text when summary=False
    assert "problems solved" not in output and "No activity" not in output


def test_handle_current_day_indicator(mock_data, console):
    """Test calendar shows current day with special indicator"""
    args = SimpleNamespace(months=1, summary=False)
    
    with patch('srl.commands.calendar.date') as mock_date:
        mock_date.today.return_value = date(2025, 12, 14)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        calendar.handle(args, console)
        
        output = console.export_text()
        # Should contain today indicator (⬜)
        assert "⬜" in output


def test_handle_includes_activity_calendar_heading(mock_data, console):
    """Test calendar always includes the Activity Calendar heading"""
    args = SimpleNamespace(months=1, summary=False)
    
    calendar.handle(args, console)
    
    output = console.export_text()
    # Should include the Activity Calendar heading
    assert "Activity Calendar" in output
