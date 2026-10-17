"""Expose the actual failed CI assertion without requiring private log access."""
import os
from pathlib import Path

log = Path(os.environ['RUNNER_TEMP']) / 'getmacros-validation.log'
if log.is_file():
    tail = '\n'.join(log.read_text(encoding='utf-8', errors='replace').splitlines()[-45:])[-9000:]
    escaped = tail.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    print('::error title=Validation failure details::' + escaped)
