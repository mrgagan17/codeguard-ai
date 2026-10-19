from app.analyzers.radon_analyzer import RadonAnalyzer
from app.schemas.common import CategoryEnum

def test_radon_complexity_detection():
    analyzer = RadonAnalyzer()
    # Complex nested code
    code = """
def complex_dispatcher(a, b, c, d, e):
    if a:
        if b:
            return 1
        elif c:
            return 2
        else:
            return 3
    elif d:
        if e:
            return 4
        else:
            return 5
    elif c and d:
        return 6
    elif a and e:
        return 7
    elif b and d:
        return 8
    elif c and e:
        return 9
    return 0
"""
    findings = analyzer.analyze([("router.py", code)], "/tmp")
    assert any(f.category == CategoryEnum.COMPLEXITY for f in findings)
    assert any("radon-cc" in f.rule_id for f in findings)

def test_radon_simple_function_no_alert():
    analyzer = RadonAnalyzer()
    code = """
def simple_add(x, y):
    return x + y
"""
    findings = analyzer.analyze([("simple.py", code)], "/tmp")
    assert len(findings) == 0
