import os
import py_compile
import subprocess
import sys
import tempfile

from openjarvis.tools import tool


@tool()
def run_python(code: str, timeout: int = 10) -> str:
    """Execute Python code in an isolated subprocess.

    Args:
        code: Python code to execute.
        timeout: Execution timeout in seconds.

    Returns:
        stdout + stderr combined, truncated to 4000 characters.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = result.stdout + result.stderr

        if len(output) > 4000:
            output = output[:4000] + "\n... [truncated at 4000 chars]"

        return output if output.strip() else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: Code execution timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing code: {e}"

@tool()
def run_shell(command: str, timeout: int = 15) -> str:
    """Execute a shell command.

    Args:
        command: Shell command to execute.
        timeout: Execution timeout in seconds.

    Returns:
        stdout + stderr combined, truncated to 4000 characters.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
        )

        output = result.stdout + result.stderr

        if len(output) > 4000:
            output = output[:4000] + "\n... [truncated at 4000 chars]"

        return output if output.strip() else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {e}"

@tool()
def lint_python(code: str) -> str:
    """Check Python code for syntax errors without executing it.

    Args:
        code: Python code to check.

    Returns:
        "OK" if syntax is valid, or error message with line number.
    """
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            py_compile.compile(temp_path, doraise=True)
            return "Syntax OK"
        finally:
            os.remove(temp_path)
    except py_compile.PyCompileError as e:
        return f"Syntax Error: {e}"
    except Exception as e:
        return f"Error: {e}"


@tool()
def run_pytest(test_path: str = "", args: str = "") -> str:
    """Run pytest on the test suite and return structured test counts and failures.

    Args:
        test_path: Optional path to specific test file or directory.
        args: Optional additional pytest arguments (e.g. "-k test_editor -v").

    Returns:
        Execution summary with pass/fail counts and error tracebacks.
    """
    cmd = ["pytest", "-q"]
    if test_path:
        cmd.append(test_path)
    if args:
        cmd.extend(args.split())

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = res.stdout + res.stderr
        if len(output) > 5000:
            output = output[:5000] + "\n... [output truncated at 5000 chars]"
        return f"Exit code: {res.returncode}\n{output.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: pytest execution timed out after 60 seconds."
    except Exception as exc:
        return f"Error running pytest: {exc}"

