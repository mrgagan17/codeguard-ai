import pytest
from app.analyzers.ast_analyzer import ASTAnalyzer
from app.schemas.common import SeverityEnum, CategoryEnum

def test_ast_mutable_defaults():
    analyzer = ASTAnalyzer()
    code = "def bad_fn(items=[]):\n    items.append(1)\n    return items\n"
    findings = analyzer.analyze([("test.py", code)], "/tmp")
    rule_ids = [f.rule_id for f in findings]
    assert "AST-001" in rule_ids
    f = next(f for f in findings if f.rule_id == "AST-001")
    assert f.severity == SeverityEnum.HIGH
    assert f.category == CategoryEnum.BUG_RISK

def test_ast_eval_and_exec():
    analyzer = ASTAnalyzer()
    code = "def calc(user_in):\n    return eval(user_in)\n"
    findings = analyzer.analyze([("test.py", code)], "/tmp")
    rule_ids = [f.rule_id for f in findings]
    assert "AST-005" in rule_ids
    f = next(f for f in findings if f.rule_id == "AST-005")
    assert f.severity == SeverityEnum.CRITICAL
    assert f.category == CategoryEnum.SECURITY

def test_ast_risky_subprocess_and_os_system():
    analyzer = ASTAnalyzer()
    code = "import os\nimport subprocess\ndef run_cmd(arg):\n    os.system('ls ' + arg)\n    subprocess.run('echo ' + arg, shell=True)\n"
    findings = analyzer.analyze([("test.py", code)], "/tmp")
    rule_ids = [f.rule_id for f in findings]
    assert "AST-006" in rule_ids

def test_ast_empty_exception_handler():
    analyzer = ASTAnalyzer()
    code = "def do_work():\n    try:\n        x = 1 / 0\n    except:\n        pass\n"
    findings = analyzer.analyze([("test.py", code)], "/tmp")
    rule_ids = [f.rule_id for f in findings]
    assert "AST-004" in rule_ids

def test_ast_insecure_tempfile():
    analyzer = ASTAnalyzer()
    code = "import tempfile\ndef create_file():\n    return tempfile.mktemp()\n"
    findings = analyzer.analyze([("test.py", code)], "/tmp")
    rule_ids = [f.rule_id for f in findings]
    assert "AST-007" in rule_ids

def test_ast_safe_code_no_false_positives():
    analyzer = ASTAnalyzer()
    code = (
        "def safe_calc(val: int = 0):\n"
        "    try:\n"
        "        return val * 2\n"
        "    except TypeError:\n"
        "        raise\n"
    )
    findings = analyzer.analyze([("safe.py", code)], "/tmp")
    assert len(findings) == 0

def test_ast_trailing_semicolon():
    analyzer = ASTAnalyzer()
    code = 'print("Hello");\n'
    findings = analyzer.analyze([("hello.py", code)], "/tmp")
    rule_ids = [f.rule_id for f in findings]
    assert "AST-008" in rule_ids
    f = next(f for f in findings if f.rule_id == "AST-008")
    assert f.severity == SeverityEnum.LOW
    assert f.category == CategoryEnum.STYLE
    assert f.start_line == 1

def test_ast_syntax_error():
    analyzer = ASTAnalyzer()
    code = 'def broken_function(:\n    return 42\n'
    findings = analyzer.analyze([("broken.py", code)], "/tmp")
    rule_ids = [f.rule_id for f in findings]
    assert "AST-SYNTAX-ERROR" in rule_ids
    f = next(f for f in findings if f.rule_id == "AST-SYNTAX-ERROR")
    assert f.severity == SeverityEnum.CRITICAL
    assert "Syntax Error" in f.title
    assert f.start_line == 1

