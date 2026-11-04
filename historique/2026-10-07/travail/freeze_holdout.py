"""Coordinator-only holdout construction. Seeds fixed before candidate evaluation."""
import json, random, hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
dst=root/'test-boundary'; dst.mkdir(exist_ok=True)
rng=random.Random(150526255)
simulation=[]
for n in (2,3,4):
    for rep in range(2):
        simulation.append({'name':f'n{n}-heldout-{rep}', 'A':[[f'{rng.randint(-4,4)}/{rng.randint(1,5)}' for j in range(n)] for i in range(n)]})
rng=random.Random(105014010)
structural=[]
for n in (2,3,4):
    for rep in range(3):
        structural.append({'name':f'n{n}-boolean-heldout-{rep}', 'B':[[rng.randrange(2) for j in range(n)] for i in range(n)]})
for name,data in [('simulation.json',simulation),('structural.json',structural)]:
    p=dst/name
    if p.exists(): raise RuntimeError(f'Boundary already frozen: {p}')
    p.write_text(json.dumps(data,indent=2))
    print(name,hashlib.sha256(p.read_bytes()).hexdigest(),len(data))
