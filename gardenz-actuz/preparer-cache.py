"""Version the small application shell; images and daily archives are cached on read."""
from pathlib import Path
import hashlib
import json
import re
root = Path(__file__).resolve().parent
files = ['./', 'index.html', 'app.css', 'app.js', 'journal.css', 'install.css', 'live.css',
         'live.js', 'manifest.webmanifest', 'assets/fraktur.ttf', 'assets/icon-192.png',
         'assets/icon-512.png', 'editions.json', 'data/latest.json', 'data/index.json']
worker = root / 'sw.js'
source = worker.read_text()
# The SW implementation itself is part of its version; generated fields are stable placeholders.
stable = re.sub(r"const CACHE='gardenz-actuz-[^']+';", "const CACHE='gardenz-actuz-version';", source)
stable = re.sub(r'const FILES=\[.*?\];', 'const FILES=[];', stable)
version = hashlib.sha256(stable.encode() + b''.join((root / p).read_bytes() for p in files if p != './' and not p.endswith('.json'))).hexdigest()[:12]
source = re.sub(r"const CACHE='gardenz-actuz-[^']+';", f"const CACHE='gardenz-actuz-v3-{version}';", source)
source = re.sub(r'const FILES=\[.*?\];', 'const FILES=' + json.dumps(files) + ';', source)
worker.write_text(source)
print(f'Cache : {version} · {len(files)} ressources essentielles')
