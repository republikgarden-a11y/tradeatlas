"""À lancer après toute mise à jour des éditions ou fichiers de l’application."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parent
files = ['./'] + sorted(
    p.relative_to(root).as_posix() for p in root.rglob('*')
    if p.is_file() and p.name != 'sw.js'
    and p.suffix in {'.html','.css','.js','.json','.webmanifest','.png','.jpg','.jpeg','.webp','.ttf','.woff2'}
    and not any(part.startswith('.') or part=='__pycache__' for part in p.relative_to(root).parts)
)
version = hashlib.sha256(b''.join((root / p).read_bytes() for p in files if p != './')).hexdigest()[:12]
worker = root / 'sw.js'
text = worker.read_text()
text = re.sub(r"const CACHE='gardenz-actuz-[^']+';", f"const CACHE='gardenz-actuz-{version}';", text)
text = re.sub(r'const FILES=\[.*?\];', 'const FILES=' + json.dumps(files) + ';', text)
worker.write_text(text)
print(f'Cache actualisé : {version} · {len(files)} ressources')
