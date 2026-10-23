"""Check publishable files without echoing detected secret values."""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'staticfiles', '.pytest_cache'}
PRIVATE = {'_private', '_review', 'review', '.playwright-cli', 'media'}
TEXT = {'.py', '.js', '.mjs', '.vue', '.scss', '.css', '.json', '.html', '.md', '.txt', '.example', '.yml', '.yaml', '.svg'}
PATTERNS = [
    ('private key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('GitHub token', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b')),
    ('cloud access key', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('hardcoded Django key', re.compile(r"(?m)^SECRET_KEY\s*=\s*['\"][^'\"]{12,}['\"]")),
    ('personal Windows path', re.compile(r'(?i)[A-Z]:[\\/](?:Users|Documents and Settings)[\\/][^\\/\s]+')),
]

def source_files():
    for p in ROOT.rglob('*'):
        relative = p.relative_to(ROOT)
        if set(relative.parts) & (SKIP | PRIVATE): continue
        if not p.is_file(): continue
        if p.name.startswith('.env') and p.name != '.env.example': continue
        if p.suffix in {'.pyc', '.log', '.zip', '.sqlite3', '.db'} or '.sqlite3-' in p.name: continue
        yield p

def check():
    issues = []
    files = list(source_files())
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        if p.suffix in {'.pem', '.key', '.pfx', '.p12'}:
            issues.append((rel, 'credential file'))
        if p.suffix not in TEXT and p.name not in {'.gitignore', '.gitattributes', 'LICENSE'}: continue
        text = p.read_text(encoding='utf-8-sig')
        for label, rx in PATTERNS:
            if rx.search(text): issues.append((rel, label))
    for rel, reason in issues: print(f'FAIL {rel}: {reason}')
    if not issues: print(f'PASS: {len(files)} publishable files checked. Runtime/private paths excluded.')
    if not (ROOT / 'LICENSE').is_file(): print('PENDING: project license has not been selected.')
    notices = ROOT / 'THIRD_PARTY_NOTICES.md'
    if notices.is_file() and '## 动效来源核对中' in notices.read_text(encoding='utf8'):
        print('PENDING: third-party redistribution review remains open; the project license does not override it.')
    return issues

if __name__ == '__main__': sys.exit(bool(check()))
