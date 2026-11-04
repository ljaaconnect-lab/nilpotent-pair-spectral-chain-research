"""Exact positive local identity, before the Lean bridge is constructed."""
import json
from pathlib import Path
import sympy as sp

x,y,a,b,c,d = sp.symbols('x y a b c d')
F = a+b*x+c*y+d*x*y

def cofactor(P):
    return sp.expand(P.subs({x:1,y:1})-P.subs({x:1,y:0})-
                     P.subs({x:0,y:1})+P.subs({x:0,y:0}))

def correct(P):
    return sp.expand(P-2*x*y*cofactor(P))

checks = {'cofactor':cofactor(F)==d,
          'local_sign_flip':correct(F)==a+b*x+c*y-d*x*y,
          'local_involution':correct(correct(F))==F}
report = {'sympy_version':sp.__version__,'checks':checks,
          'cofactor':str(cofactor(F)),'corrected':str(correct(F)),
          'scope':'Algebraic local invariant; symbolic computation is not a Lean proof or scalar complexity bound.'}
assert all(checks.values())
Path(__file__).with_name('n62-local-sympy-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
