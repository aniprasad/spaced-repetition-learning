from srl.commands import list_, add, nextup
from types import SimpleNamespace


def test_list_with_due_problem(console, monkeypatch, backdate_problem):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Due Problem"
    # Add problem with rating=1, then backdate it so it's due
    args = SimpleNamespace(name=problem, rating=1)
    add.handle(args=args, console=console)
    backdate_problem(problem, 2)

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "Problems to Practice" in output
    assert "(1)" in output
    assert problem in output


def test_list_with_limit(console, monkeypatch, backdate_problem):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    for i in range(10):
        problem = f"problem {i}"
        args = SimpleNamespace(name=problem, rating=1)
        add.handle(args=args, console=console)
        backdate_problem(problem, 2)

    console.clear()
    args = SimpleNamespace(n=3)
    list_.handle(args=args, console=console)

    output = console.export_text()
    for i in range(3):
        assert f"problem {i}" in output
    for i in range(3, 10):
        assert f"problem {i}" not in output


def test_list_with_next_up_fallback(console, monkeypatch):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Next Up Problem"
    args = SimpleNamespace(action="add", name=problem)
    nextup.handle(args=args, console=console)

    args = SimpleNamespace(n=None)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert problem in output
    assert "Problems to Practice" in output
    assert "No problems due" not in output


def test_list_empty(console, monkeypatch):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "No problems due today or in Next Up" in output


def test_should_audit_probability(monkeypatch):
    monkeypatch.setattr(list_, "load_json", lambda _: {"audit_probability": 1.0})
    monkeypatch.setattr(list_.random, "random", lambda: 0.0)  # force audit
    assert list_.should_audit() is True

    monkeypatch.setattr(list_, "load_json", lambda _: {"audit_probability": 0.0})
    monkeypatch.setattr(list_.random, "random", lambda: 1.0)  # force no audit
    assert list_.should_audit() is False


def test_list_triggers_audit(console, monkeypatch):
    problem = "Audit Problem"
    args = SimpleNamespace(name=problem, rating=5)
    add.handle(args=args, console=console)
    add.handle(args=args, console=console)  # move to mastered

    monkeypatch.setattr(list_, "should_audit", lambda: True)

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "You have been randomly audited!" in output
    assert "Audit problem:" in output
    assert problem in output


def test_list_indicate_mastered(console, backdate_problem, monkeypatch):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Mastered attempt"
    args = SimpleNamespace(name=problem, rating=5)
    add.handle(args=args, console=console)
    backdate_problem(problem, 7)

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert f"1. {problem} *" in output


def test_list_overdue_indicators(console, monkeypatch, backdate_problem):
    """Test overdue indicators for problems"""
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    # Problem 1: 3 days overdue (should show 🟡)
    problem1 = "Yellow Problem"
    args1 = SimpleNamespace(name=problem1, rating=1)
    add.handle(args=args1, console=console)
    backdate_problem(problem1, 4)  # 1 day rating + 3 days = 4 days ago

    # Problem 2: 7 days overdue (should show 🔴)
    problem2 = "Red Problem"
    args2 = SimpleNamespace(name=problem2, rating=2)
    add.handle(args=args2, console=console)
    backdate_problem(problem2, 9)  # 2 day rating + 7 days = 9 days ago

    # Problem 3: 1 day overdue (no indicator)
    problem3 = "Normal Problem"
    args3 = SimpleNamespace(name=problem3, rating=1)
    add.handle(args=args3, console=console)
    backdate_problem(problem3, 2)  # 1 day rating + 1 day = 2 days ago

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "🔴" in output  # Red indicator should be present
    assert "🟡" in output  # Yellow indicator should be present
    assert "3-6 days overdue" in output  # Legend should be present
    assert "7+ days overdue" in output  # Legend should be present
    assert problem1 in output
    assert problem2 in output
    assert problem3 in output


def test_list_overdue_sorting(console, monkeypatch, backdate_problem):
    """Test that problems are sorted by overdue amount"""
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    # Add problems with different overdue amounts
    problem1 = "Less Overdue"
    args1 = SimpleNamespace(name=problem1, rating=1)
    add.handle(args=args1, console=console)
    backdate_problem(problem1, 3)  # 2 days overdue

    problem2 = "More Overdue"
    args2 = SimpleNamespace(name=problem2, rating=1)
    add.handle(args=args2, console=console)
    backdate_problem(problem2, 5)  # 4 days overdue

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    lines = output.split('\n')
    
    # Find lines containing the problems
    problem1_line = None
    problem2_line = None
    for i, line in enumerate(lines):
        if problem1 in line:
            problem1_line = i
        if problem2 in line:
            problem2_line = i
    
    # More overdue problem should appear first
    assert problem2_line is not None
    assert problem1_line is not None
    assert problem2_line < problem1_line


def test_get_overdue_info(console, backdate_problem):
    """Test the get_overdue_info function"""
    # Add a problem and backdate it
    problem = "Overdue Test"
    args = SimpleNamespace(name=problem, rating=2)
    add.handle(args=args, console=console)
    backdate_problem(problem, 5)  # 2 day rating + 3 days overdue = 5 days ago

    overdue_info = list_.get_overdue_info()
    assert problem in overdue_info
    assert overdue_info[problem] == 3  # 3 days overdue


def test_list_no_legend_when_no_overdue(console, monkeypatch, backdate_problem):
    """Test that legend doesn't appear when no overdue indicators are present"""
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    # Add a problem that's only 1 day overdue (no indicator)
    problem = "Recent Problem"
    args = SimpleNamespace(name=problem, rating=1)
    add.handle(args=args, console=console)
    backdate_problem(problem, 2)  # 1 day rating + 1 day = 2 days ago

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "days overdue" not in output  # Legend should not be present
    assert "🟡" not in output  # No yellow indicators
    assert "🔴" not in output  # No red indicators
    assert problem in output
