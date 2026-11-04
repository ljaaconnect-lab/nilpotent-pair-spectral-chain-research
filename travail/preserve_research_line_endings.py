from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
name = 'documents/CADRE_ACTUEL.md'
before = subprocess.run(['git', 'show', 'HEAD:'+name], cwd=root,
                        capture_output=True, check=True).stdout
old_text = before.decode('utf-8').replace('\r\n', '\n')
current = (root/name).read_text(encoding='utf-8')
assert current.startswith(old_text)
(root/name).write_bytes(before + current[len(old_text):].encode('utf-8'))
result = root/'etudes/2026-11-01/borne-chaine-generale/RESULTAT.md'
result.write_bytes(result.read_text(encoding='utf-8').encode('utf-8'))
