from srl.commands import add, list_, inprogress, mastered
from types import SimpleNamespace


def test_add_problem_with_leetcode_id(mock_data, console, load_json):
    """Test adding a new problem with a LeetCode ID"""
    problem = "Concatenation of Array"
    rating = 5
    leetcode_id = 1929
    args = SimpleNamespace(name=problem, rating=rating, id=leetcode_id, number=None, leetcode_id=None)

    add.handle(args=args, console=console)

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert problem in progress
    assert progress[problem]["history"][0]["rating"] == rating
    assert progress[problem]["leetcode_id"] == leetcode_id

    output = console.export_text()
    assert f"Added rating {rating} for '{problem}'" in output


def test_add_problem_without_leetcode_id(mock_data, console, load_json):
    """Test adding a problem without a LeetCode ID (backward compatibility)"""
    problem = "Some Problem"
    rating = 3
    args = SimpleNamespace(name=problem, rating=rating, id=None, number=None, leetcode_id=None)

    add.handle(args=args, console=console)

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert problem in progress
    assert "leetcode_id" not in progress[problem]


def test_add_leetcode_id_to_existing_problem(mock_data, console, load_json, dump_json):
    """Test adding a LeetCode ID to an existing problem"""
    problem = "Existing Problem"
    rating = 4
    leetcode_id = 217
    
    # First add without ID
    args = SimpleNamespace(name=problem, rating=3, id=None, number=None, leetcode_id=None)
    add.handle(args=args, console=console)
    
    console.clear()
    
    # Then add with ID
    args = SimpleNamespace(name=problem, rating=rating, id=leetcode_id, number=None, leetcode_id=None)
    add.handle(args=args, console=console)

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert problem in progress
    assert progress[problem]["leetcode_id"] == leetcode_id
    assert len(progress[problem]["history"]) == 2


def test_add_by_leetcode_id_existing(mock_data, console, load_json, dump_json):
    """Test adding a rating using --leetcode-id for an existing problem"""
    problem = "Contains Duplicate"
    leetcode_id = 217
    
    # First add the problem with an ID
    args = SimpleNamespace(name=problem, rating=3, id=leetcode_id, number=None, leetcode_id=None)
    add.handle(args=args, console=console)
    
    console.clear()
    
    # Now add by leetcode_id
    args = SimpleNamespace(name=None, rating=4, id=None, number=None, leetcode_id=leetcode_id)
    add.handle(args=args, console=console)

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert problem in progress
    assert len(progress[problem]["history"]) == 2
    assert progress[problem]["history"][-1]["rating"] == 4


def test_add_by_leetcode_id_not_found(mock_data, console, load_json):
    """Test adding by LeetCode ID when the problem doesn't exist"""
    leetcode_id = 9999
    
    args = SimpleNamespace(name=None, rating=4, id=None, number=None, leetcode_id=leetcode_id)
    add.handle(args=args, console=console)

    output = console.export_text()
    assert f"No problem found with LeetCode ID {leetcode_id}" in output


def test_add_by_leetcode_id_already_mastered(mock_data, console, load_json, dump_json):
    """Test adding by LeetCode ID when problem is already mastered"""
    problem = "Mastered Problem"
    leetcode_id = 100
    
    # Add to mastered file
    mastered_file = mock_data.MASTERED_FILE
    dump_json(mastered_file, {problem: {"leetcode_id": leetcode_id, "history": [{"rating": 5, "date": "2025-12-01"}]}})
    
    args = SimpleNamespace(name=None, rating=4, id=None, number=None, leetcode_id=leetcode_id)
    add.handle(args=args, console=console)

    output = console.export_text()
    assert f"Problem with LeetCode ID {leetcode_id} is already mastered" in output


def test_mastery_preserves_leetcode_id(mock_data, console, load_json):
    """Test that LeetCode ID is preserved when a problem is moved to mastered"""
    problem = "Two Sum"
    leetcode_id = 1
    rating = 5
    
    args = SimpleNamespace(name=problem, rating=rating, id=leetcode_id, number=None, leetcode_id=None)
    # Call twice with rating 5 to trigger mastery
    add.handle(args=args, console=console)
    add.handle(args=args, console=console)

    mastered_file = mock_data.MASTERED_FILE
    mastered_data = load_json(mastered_file)
    assert problem in mastered_data
    assert mastered_data[problem]["leetcode_id"] == leetcode_id


def test_list_displays_leetcode_id(mock_data, console, load_json, backdate_problem):
    """Test that srl list displays LeetCode IDs"""
    problem = "Valid Parentheses"
    leetcode_id = 20
    
    # Add problem with ID and make it due
    args = SimpleNamespace(name=problem, rating=3, id=leetcode_id, number=None, leetcode_id=None)
    add.handle(args=args, console=console)
    backdate_problem(problem, 5)
    
    console.clear()
    
    # Run list command
    list_.handle(SimpleNamespace(n=None), console)
    
    output = console.export_text()
    assert f"#{leetcode_id}" in output
    assert problem in output


def test_inprogress_displays_leetcode_id(mock_data, console, load_json):
    """Test that srl inprogress displays LeetCode IDs"""
    problem = "Merge Two Lists"
    leetcode_id = 21
    
    # Add problem with ID
    args = SimpleNamespace(name=problem, rating=3, id=leetcode_id, number=None, leetcode_id=None)
    add.handle(args=args, console=console)
    
    console.clear()
    
    # Run inprogress command
    inprogress.handle(SimpleNamespace(), console)
    
    output = console.export_text()
    assert f"#{leetcode_id}" in output
    assert problem in output


def test_mastered_displays_leetcode_id(mock_data, console, load_json):
    """Test that srl mastered displays LeetCode IDs"""
    problem = "Best Time to Buy and Sell Stock"
    leetcode_id = 121
    rating = 5
    
    # Add problem with ID and master it
    args = SimpleNamespace(name=problem, rating=rating, id=leetcode_id, number=None, leetcode_id=None)
    add.handle(args=args, console=console)
    add.handle(args=args, console=console)
    
    console.clear()
    
    # Run mastered command
    mastered.handle(SimpleNamespace(c=False), console)
    
    output = console.export_text()
    assert f"#{leetcode_id}" in output
    assert problem in output
