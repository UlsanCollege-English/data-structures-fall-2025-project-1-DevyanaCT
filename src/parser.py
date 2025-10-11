from typing import List, Tuple, Optional

def parse_command(line: str) -> Optional[Tuple[str, List[str]]]:
    """
    Return (COMMAND, args) or None for blank/comment-only lines.

    Do NOT raise; leave semantic checks to the scheduler and tests.
    Keep whitespace handling predictable.
    """
    s = line.strip()
    if not s or s.startswith("#"):
        return None
    parts = s.split()
    cmd, args = parts[0], parts[1:]
    return cmd.upper(), args