from srl.commands import add, show
from types import SimpleNamespace


def test_add_with_note(mock_data, console, load_json):
    """Test adding a problem with a note"""
    problem = "Two Sum"
    rating = 4
    note = "Used hashmap for O(n) lookup"
    
    args = SimpleNamespace(
        name=problem, 
        rating=rating, 
        id=None, 
        number=None, 
        leetcode_id=None,
        note=note,
        mistake=None,
        time=None
    )
    add.handle(args=args, console=console)

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert problem in progress
    assert progress[problem]["history"][0]["note"] == note


def test_add_with_mistake(mock_data, console, load_json):
    """Test adding a problem with a mistake"""
    problem = "Valid Parentheses"
    rating = 3
    mistake = "Forgot to handle edge case"
    
    args = SimpleNamespace(
        name=problem, 
        rating=rating, 
        id=None, 
        number=None, 
        leetcode_id=None,
        note=None,
        mistake=mistake,
        time=None
    )
    add.handle(args=args, console=console)

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert progress[problem]["history"][0]["mistake"] == mistake


def test_add_with_time_spent(mock_data, console, load_json):
    """Test adding a problem with time spent"""
    problem = "Merge Two Lists"
    rating = 4
    time_spent = 25
    
    args = SimpleNamespace(
        name=problem, 
        rating=rating, 
        id=None, 
        number=None, 
        leetcode_id=None,
        note=None,
        mistake=None,
        time=time_spent
    )
    add.handle(args=args, console=console)

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert progress[problem]["history"][0]["time_spent"] == time_spent


def test_add_with_all_fields(mock_data, console, load_json):
    """Test adding a problem with note, mistake, and time"""
    problem = "Best Time to Buy Stock"
    rating = 5
    note = "One pass solution with min tracking"
    mistake = "Initially tried two pointers"
    time_spent = 30
    leetcode_id = 121
    
    args = SimpleNamespace(
        name=problem, 
        rating=rating, 
        id=leetcode_id, 
        number=None, 
        leetcode_id=None,
        note=note,
        mistake=mistake,
        time=time_spent
    )
    add.handle(args=args, console=console)

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert progress[problem]["history"][0]["note"] == note
    assert progress[problem]["history"][0]["mistake"] == mistake
    assert progress[problem]["history"][0]["time_spent"] == time_spent
    assert progress[problem]["leetcode_id"] == leetcode_id


def test_add_without_optional_fields(mock_data, console, load_json):
    """Test backward compatibility - adding without notes"""
    problem = "Contains Duplicate"
    rating = 4
    
    args = SimpleNamespace(
        name=problem, 
        rating=rating, 
        id=None, 
        number=None, 
        leetcode_id=None,
        note=None,
        mistake=None,
        time=None
    )
    add.handle(args=args, console=console)

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert "note" not in progress[problem]["history"][0]
    assert "mistake" not in progress[problem]["history"][0]
    assert "time_spent" not in progress[problem]["history"][0]


def test_show_problem_by_name(mock_data, console, dump_json):
    """Test showing a problem's history by name"""
    problem = "Two Sum"
    leetcode_id = 1
    
    # Add problem with history
    progress_data = {
        problem: {
            "leetcode_id": leetcode_id,
            "history": [
                {
                    "rating": 3,
                    "date": "2025-12-10",
                    "note": "Used hashmap",
                    "mistake": "Forgot edge case",
                    "time_spent": 35
                },
                {
                    "rating": 4,
                    "date": "2025-12-13",
                    "note": "Remembered pattern",
                    "time_spent": 15
                }
            ]
        }
    }
    dump_json(mock_data.PROGRESS_FILE, progress_data)
    
    args = SimpleNamespace(name=problem, number=None, leetcode_id=None)
    show.handle(args, console)
    
    output = console.export_text()
    assert problem in output
    assert f"#{leetcode_id}" in output
    assert "Used hashmap" in output
    assert "Forgot edge case" in output
    assert "35m" in output


def test_show_problem_by_leetcode_id(mock_data, console, dump_json):
    """Test showing a problem's history by LeetCode ID"""
    problem = "Contains Duplicate"
    leetcode_id = 217
    
    # Add problem with history
    progress_data = {
        problem: {
            "leetcode_id": leetcode_id,
            "history": [
                {
                    "rating": 4,
                    "date": "2025-12-13",
                    "note": "HashSet approach"
                }
            ]
        }
    }
    dump_json(mock_data.PROGRESS_FILE, progress_data)
    
    args = SimpleNamespace(name=None, number=None, leetcode_id=leetcode_id)
    show.handle(args, console)
    
    output = console.export_text()
    assert problem in output
    assert "HashSet approach" in output


def test_show_mastered_problem(mock_data, console, dump_json):
    """Test showing a mastered problem"""
    problem = "Best Time to Buy Stock"
    
    # Add problem to mastered
    mastered_data = {
        problem: {
            "leetcode_id": 121,
            "history": [
                {
                    "rating": 5,
                    "date": "2025-12-10",
                    "note": "Perfect solve"
                },
                {
                    "rating": 5,
                    "date": "2025-12-15",
                    "note": "Still got it"
                }
            ]
        }
    }
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    
    args = SimpleNamespace(name=problem, number=None, leetcode_id=None)
    show.handle(args, console)
    
    output = console.export_text()
    assert problem in output
    assert "Mastered" in output
    assert "Perfect solve" in output


def test_show_problem_not_found(mock_data, console):
    """Test showing a problem that doesn't exist"""
    args = SimpleNamespace(name="Nonexistent Problem", number=None, leetcode_id=None)
    show.handle(args, console)
    
    output = console.export_text()
    assert "not found" in output.lower()


def test_multiple_attempts_with_notes(mock_data, console, load_json):
    """Test adding multiple attempts with different notes"""
    problem = "Climbing Stairs"
    
    # First attempt
    args1 = SimpleNamespace(
        name=problem, 
        rating=3, 
        id=None, 
        number=None, 
        leetcode_id=None,
        note="DP approach, took time to figure out",
        mistake="Confused with recursion",
        time=45
    )
    add.handle(args=args1, console=console)
    
    # Second attempt
    args2 = SimpleNamespace(
        name=problem, 
        rating=4, 
        id=None, 
        number=None, 
        leetcode_id=None,
        note="Much clearer now",
        mistake=None,
        time=20
    )
    add.handle(args=args2, console=console)

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert len(progress[problem]["history"]) == 2
    assert progress[problem]["history"][0]["note"] == "DP approach, took time to figure out"
    assert progress[problem]["history"][1]["note"] == "Much clearer now"
    assert progress[problem]["history"][0]["time_spent"] == 45
    assert progress[problem]["history"][1]["time_spent"] == 20


def test_show_compact_view(mock_data, console, dump_json):
    """Test compact view shows only attempts with notes/mistakes"""
    problem = "Test Problem"
    leetcode_id = 999
    
    # Add problem with mix of attempts with and without notes across multiple dates
    progress_data = {
        problem: {
            "leetcode_id": leetcode_id,
            "history": [
                {
                    "rating": 2,
                    "date": "2025-12-08",
                    "note": "First attempt - struggled with the approach, need to review fundamentals",
                    "mistake": "Completely wrong algorithm, used brute force",
                    "time_spent": 45
                },
                {
                    "rating": 3,
                    "date": "2025-12-10",
                    "note": "Better understanding after reading solution",
                    "time_spent": 35
                },
                {
                    "rating": 3,
                    "date": "2025-12-10", 
                    "time_spent": 20  # No note/mistake - should be skipped
                },
                {
                    "rating": 4,
                    "date": "2025-12-12",
                    "note": "Almost perfect, just small issues",
                    "mistake": "Off-by-one error in loop condition",
                    "time_spent": 25
                },
                {
                    "rating": 5,
                    "date": "2025-12-13",
                    "note": "Perfect solve! Finally understood the pattern completely",
                    "time_spent": 15
                }
            ]
        }
    }
    dump_json(mock_data.PROGRESS_FILE, progress_data)
    
    args = SimpleNamespace(name=problem, number=None, leetcode_id=None, compact=True)
    show.handle(args, console)
    
    output = console.export_text()
    assert problem in output
    assert "First attempt - struggled" in output
    assert "Perfect solve!" in output
    # Second attempt without notes should not show #3
    assert "#3" not in output
    # But #1, #2, #4, #5 should be present
    assert "#1" in output
    assert "#2" in output
    assert "#4" in output
    assert "#5" in output
