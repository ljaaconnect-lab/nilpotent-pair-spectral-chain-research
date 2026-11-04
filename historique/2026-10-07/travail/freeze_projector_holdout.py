"""Freeze coordinator-owned positive rational cases before n61 is selected."""
import hashlib
import json
import random
from fractions import Fraction
from pathlib import Path

target = Path(__file__).resolve().parent/'test-boundary/projector-positive-holdout.json'
assert not target.exists(), 'Never overwrite a frozen test boundary'
rng = random.Random(105061027)
cases = []
for n in (2,3,4,5):
    for trial in range(2):
        A = [[str(Fraction(rng.randint(-4,5),rng.randint(1,4))) for j in range(n)] for i in range(n)]
        cases.append({'name':f'n{n}-projector-holdout-{trial}','A':A})
data = {'seed':105061027,'scope':'Positive correctness boundary; symbolic z, no asymptotic inference.',
        'cases':cases}
target.write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps({'case_count':len(cases),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
