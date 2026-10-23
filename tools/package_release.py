"""Build a local review archive. Never uploads or includes Git history."""
from pathlib import Path
import zipfile
from check_release import ROOT, check, source_files

if check(): raise SystemExit('Fix detected issues before packaging.')
target = ROOT.parent / 'Eclipse-template-review.zip'
if target.exists(): raise SystemExit(f'Review archive already exists: {target.name}. Rename it before generating another copy.')
with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(source_files()):
        archive.write(path, 'Eclipse-template/' + path.relative_to(ROOT).as_posix())
print(f'Local review archive created: {target}')
