from pathlib import Path
import html
import json
import re

root = Path(__file__).resolve().parents[1]
catalogue = json.loads((root / 'catalogue.json').read_text(encoding='utf-8'))
entry = next(e for e in catalogue if e['id'] == 'nov01:raccord-initialisation')
entry['documents'] = [p.relative_to(root).as_posix()
                      for p in sorted((root / entry['dossier']).rglob('*'))
                      if p.is_file() and '__pycache__' not in p.parts]
(root / 'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
details = '<details class="essai" data-search="' + html.escape(entry['id'] + ' ' + entry['campagne'].lower()) + '"><summary><span>' + entry['id'] + '</span> ' + html.escape(entry['campagne']) + '</summary>'
details += '<p>' + html.escape(entry['resultat']) + '</p><p>' + html.escape(entry['enseignement']) + '</p><p>'
details += ' · '.join('<a href="' + name + '">' + name.rsplit('/', 1)[1] + '</a>' for name in entry['documents'])
details += '</p></details>'
page = (root / 'index.html').read_text(encoding='utf-8')
page, replaced = re.subn(r'<details class="essai"[^>]*><summary><span>nov01:raccord-initialisation</span>.*?</details>', lambda _: details, page, count=1, flags=re.S)
assert replaced == 1
(root / 'index.html').write_text(page, encoding='utf-8')
print(json.dumps({'studies': len(catalogue), 'documents': len(entry['documents'])}))
