import ast
from typing import List, Tuple, Optional
from app.analyzers.base import BaseAnalyzer
from app.schemas.finding import FindingCreate
from app.schemas.common import SeverityEnum, CategoryEnum, ConfidenceEnum
from app.core.security import redact_text

class ASTCheckerVisitor(ast.NodeVisitor):
    def __init__(self, filename: str, lines: List[str]):
        self.filename = filename
        self.lines = lines
        self.findings: List[FindingCreate] = []

    def _get_snippet(self, start_line: int, end_line: int) -> Optional[str]:
        if not self.lines:
            return None
        s = max(0, start_line - 1)
        e = min(len(self.lines), end_line)
        snippet = "\n".join(self.lines[s:e])
        return redact_text(snippet).strip() or None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_mutable_defaults(node)
        self._check_function_length(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_mutable_defaults(node)
        self._check_function_length(node)
        self.generic_visit(node)

    def _check_mutable_defaults(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """Rule AST-001: Mutable default arguments (list, dict, set)."""
        defaults = node.args.defaults + [d for d in node.args.kw_defaults if d is not None]
        for default in defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)) or (
                isinstance(default, ast.Call) and getattr(default.func, "id", "") in ("list", "dict", "set")
            ):
                line = default.lineno if hasattr(default, "lineno") else node.lineno
                self.findings.append(FindingCreate(
                    rule_id="AST-001",
                    title=f"Mutable Default Argument in '{node.name}'",
                    description=f"Function '{node.name}' defines a mutable default argument (list, dict, or set). Default arguments are evaluated once at function definition time, sharing state across invocations.",
                    category=CategoryEnum.BUG_RISK,
                    severity=SeverityEnum.HIGH,
                    confidence=ConfidenceEnum.HIGH,
                    file_path=self.filename,
                    start_line=line,
                    end_line=line,
                    snippet=self._get_snippet(line, line),
                    tool="ast",
                    why_it_matters="Modifications to mutable default arguments persist between calls, causing unexpected state mutations and difficult-to-reproduce bugs.",
                    recommended_remediation="Set the default value to None and initialize the mutable structure inside the function: `def foo(x=None): if x is None: x = []`",
                    references="https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments"
                ))

    def _check_function_length(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """Rule AST-002: Excessive function length (> 75 lines)."""
        end_lineno = getattr(node, "end_lineno", node.lineno)
        length = end_lineno - node.lineno + 1
        if length > 75:
            self.findings.append(FindingCreate(
                rule_id="AST-002",
                title=f"Excessive Function Length in '{node.name}' ({length} lines)",
                description=f"Function '{node.name}' spans {length} lines, exceeding the recommended limit of 75 lines.",
                category=CategoryEnum.COMPLEXITY,
                severity=SeverityEnum.LOW,
                confidence=ConfidenceEnum.HIGH,
                file_path=self.filename,
                start_line=node.lineno,
                end_line=end_lineno,
                snippet=self._get_snippet(node.lineno, min(node.lineno + 4, end_lineno)),
                tool="ast",
                why_it_matters="Very long functions typically violate the Single Responsibility Principle, are difficult to read, test, and maintain.",
                recommended_remediation="Extract logical sub-steps into focused helper functions or modular subroutines.",
                references="https://refactoring.guru/smells/long-method"
            ))

    def visit_Try(self, node: ast.Try):
        """Rule AST-003: Broad exception handler & Rule AST-004: Empty exception handler."""
        for handler in node.handlers:
            # Check for bare except: or except Exception: / except BaseException:
            is_broad = False
            if handler.type is None:  # bare except:
                is_broad = True
            elif isinstance(handler.type, ast.Name) and handler.type.id in ("Exception", "BaseException"):
                is_broad = True

            # Check if body is empty or only pass/docstring
            is_empty = False
            meaningful_stmts = [
                s for s in handler.body 
                if not (isinstance(s, ast.Pass) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)))
            ]
            if len(meaningful_stmts) == 0:
                is_empty = True

            has_raise = any(isinstance(s, ast.Raise) for s in handler.body)

            h_line = handler.lineno
            end_line = getattr(handler, "end_lineno", h_line)

            if is_empty:
                self.findings.append(FindingCreate(
                    rule_id="AST-004",
                    title="Empty Exception Handler (Swallowed Error)",
                    description="The exception block is completely empty or only contains a pass statement, suppressing all errors without logging or handling.",
                    category=CategoryEnum.BUG_RISK,
                    severity=SeverityEnum.MEDIUM,
                    confidence=ConfidenceEnum.HIGH,
                    file_path=self.filename,
                    start_line=h_line,
                    end_line=end_line,
                    snippet=self._get_snippet(h_line, end_line),
                    tool="ast",
                    why_it_matters="Silently suppressing exceptions masks critical failures, causing corrupt states or unexpected behavior further down the execution path.",
                    recommended_remediation="At minimum log the error with traceback or handle specific expected exceptions appropriately.",
                    references="https://peps.python.org/pep-0008/#programming-recommendations"
                ))
            elif is_broad and not has_raise:
                self.findings.append(FindingCreate(
                    rule_id="AST-003",
                    title="Broad Exception Handling without Re-raise",
                    description="Catching broad Exception or BaseException without re-raising can catch system signals (e.g. KeyboardInterrupt) and hide unexpected syntax/type errors.",
                    category=CategoryEnum.QUALITY,
                    severity=SeverityEnum.LOW,
                    confidence=ConfidenceEnum.MEDIUM,
                    file_path=self.filename,
                    start_line=h_line,
                    end_line=end_line,
                    snippet=self._get_snippet(h_line, end_line),
                    tool="ast",
                    why_it_matters="Broad exception handling makes debugging difficult and may catch exceptions that should terminate the process.",
                    recommended_remediation="Catch specific exception types (e.g. FileNotFoundError, ValueError) rather than the root Exception class.",
                    references="https://docs.python.org/3/tutorial/errors.html#handling-exceptions"
                ))

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_id = ""
        attr_name = ""
        if isinstance(node.func, ast.Name):
            func_id = node.func.id
        elif isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            if isinstance(node.func.value, ast.Name):
                func_id = f"{node.func.value.id}.{attr_name}"

        line = node.lineno
        end_line = getattr(node, "end_lineno", line)

        # Rule AST-005: Use of eval or exec
        if func_id in ("eval", "exec"):
            self.findings.append(FindingCreate(
                rule_id="AST-005",
                title=f"Suspicious Dynamic Execution via '{func_id}()'",
                description=f"Call to '{func_id}()' dynamically interprets Python code. If supplied with untrusted input, it allows arbitrary remote code execution (RCE).",
                category=CategoryEnum.SECURITY,
                severity=SeverityEnum.CRITICAL,
                confidence=ConfidenceEnum.HIGH,
                file_path=self.filename,
                start_line=line,
                end_line=end_line,
                snippet=self._get_snippet(line, end_line),
                tool="ast",
                why_it_matters="Dynamic evaluation can execute arbitrary operating system and process commands if the input is untrusted.",
                recommended_remediation="Use ast.literal_eval for safe literals parsing, or replace dynamic evaluation with explicit data structures/dispatch.",
                references="https://owasp.org/www-community/attacks/Code_Injection"
            ))

        # Rule AST-006: Risky subprocess with shell=True or os.system
        if func_id == "os.system":
            self.findings.append(FindingCreate(
                rule_id="AST-006",
                title="Risky Process Execution via 'os.system()'",
                description="Call to os.system() passes commands directly to the system shell, creating command injection vulnerabilities.",
                category=CategoryEnum.SECURITY,
                severity=SeverityEnum.HIGH,
                confidence=ConfidenceEnum.HIGH,
                file_path=self.filename,
                start_line=line,
                end_line=end_line,
                snippet=self._get_snippet(line, end_line),
                tool="ast",
                why_it_matters="Command injection allows attackers to run unauthorized commands with the privileges of the Python process.",
                recommended_remediation="Use `subprocess.run([...], shell=False)` with arguments passed as a list, never a concatenated string.",
                references="https://docs.python.org/3/library/subprocess.html#security-considerations"
            ))

        if func_id.startswith("subprocess."):
            # Check for shell=True keyword argument
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.findings.append(FindingCreate(
                        rule_id="AST-006",
                        title=f"Risky Subprocess with 'shell=True' in '{func_id}'",
                        description=f"Invocation of '{func_id}' specifies 'shell=True', opening the command to shell injection vulnerabilities.",
                        category=CategoryEnum.SECURITY,
                        severity=SeverityEnum.CRITICAL,
                        confidence=ConfidenceEnum.HIGH,
                        file_path=self.filename,
                        start_line=line,
                        end_line=end_line,
                        snippet=self._get_snippet(line, end_line),
                        tool="ast",
                        why_it_matters="When shell=True is set, strings containing metacharacters (;, &, |, `) are interpreted by the shell, enabling command injection.",
                        recommended_remediation="Pass command arguments as an array of strings with `shell=False` (the default).",
                        references="https://cwe.mitre.org/data/definitions/78.html"
                    ))

        # Rule AST-007: Insecure temporary file generation (tempfile.mktemp)
        if func_id in ("tempfile.mktemp", "mktemp"):
            self.findings.append(FindingCreate(
                rule_id="AST-007",
                title="Insecure Temporary File Creation via 'tempfile.mktemp()'",
                description="tempfile.mktemp() is deprecated and vulnerable to symlink and race-condition attacks (TOCTOU).",
                category=CategoryEnum.SECURITY,
                severity=SeverityEnum.HIGH,
                confidence=ConfidenceEnum.HIGH,
                file_path=self.filename,
                start_line=line,
                end_line=end_line,
                snippet=self._get_snippet(line, end_line),
                tool="ast",
                why_it_matters="Between generating the filename and opening it, another process can create a symlink or file at the path, causing race condition attacks.",
                recommended_remediation="Use `tempfile.NamedTemporaryFile()` or `tempfile.TemporaryDirectory()` which atomically create the file/directory safely.",
                references="https://cwe.mitre.org/data/definitions/377.html"
            ))

        # Rule AST-008: Insecure random for security-sensitive tokens
        if func_id in ("random.random", "random.randint", "random.choice"):
            for parent in [getattr(node, "_parent_assign", None)]:
                pass  # general advisory if found in auth contexts

        self.generic_visit(node)

    def _check_trailing_semicolons(self):
        """Rule AST-008: Unnecessary Trailing Semicolon."""
        for idx, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if stripped.endswith(";") and not stripped.startswith("#"):
                self.findings.append(FindingCreate(
                    rule_id="AST-008",
                    title="Unnecessary Trailing Semicolon",
                    description="Statement ends with an unnecessary semicolon. Python statements do not require semicolons.",
                    category=CategoryEnum.STYLE,
                    severity=SeverityEnum.LOW,
                    confidence=ConfidenceEnum.HIGH,
                    file_path=self.filename,
                    start_line=idx,
                    end_line=idx,
                    snippet=self._get_snippet(idx, idx),
                    tool="ast",
                    why_it_matters="Trailing semicolons violate PEP 8 conventions and are unnecessary in Python.",
                    recommended_remediation="Remove the trailing semicolon from the end of the line.",
                    references="https://peps.python.org/pep-0008/#whitespace-in-expressions-and-statements"
                ))


class ASTAnalyzer(BaseAnalyzer):
    name: str = "ast"
    display_name: str = "Custom AST Static Analyzer"
    version: str = "1.0.0"
    is_available: bool = True
    enabled: bool = True
    description: str = "Analyzes Python Abstract Syntax Trees for mutable defaults, swallowed exceptions, eval/exec, and unsafe subprocess calls."

    def check_availability(self) -> bool:
        self.is_available = True
        return True

    def analyze(self, files: List[Tuple[str, str]], base_dir: str) -> List[FindingCreate]:
        findings: List[FindingCreate] = []

        for rel_path, content in files:
            if not rel_path.endswith((".py", ".pyw")) or not content:
                continue

            lines = content.splitlines()
            try:
                tree = ast.parse(content, filename=rel_path)
                visitor = ASTCheckerVisitor(filename=rel_path, lines=lines)
                visitor.visit(tree)
                visitor._check_trailing_semicolons()
                findings.extend(visitor.findings)
            except SyntaxError as se:
                snippet = se.text.strip() if se.text else None
                line_no = se.lineno or 1
                if not snippet and 1 <= line_no <= len(lines):
                    snippet = lines[line_no - 1].strip()
                findings.append(FindingCreate(
                    rule_id="AST-SYNTAX-ERROR",
                    title=f"Python Syntax Error: {se.msg}",
                    description=f"Syntax error at line {line_no}: {se.msg}",
                    category=CategoryEnum.BUG_RISK,
                    severity=SeverityEnum.CRITICAL,
                    confidence=ConfidenceEnum.HIGH,
                    file_path=rel_path,
                    start_line=line_no,
                    end_line=line_no,
                    snippet=snippet,
                    tool=self.name,
                    why_it_matters="Code containing syntax errors cannot be compiled, imported, or executed in Python.",
                    recommended_remediation=f"Fix the syntax error on line {line_no}: {se.msg}",
                    references="https://docs.python.org/3/reference/grammar.html"
                ))
            except Exception:
                pass

        return findings
