"""Test a finite transport law for the quartic counterterm (no conjectural claim)."""
from collections import defaultdict
from pathlib import Path
import json
import sympy as sp
from derive_quintic import derive,canonical,partitions


def transform(p, action):
    out=defaultdict(sp.Rational)
    # defaultdict(Rational) cannot create a no-argument Rational.
    out=defaultdict(lambda:sp.S.Zero)
    for w,c in p.items():
        out[canonical(action(w))]+=sp.Rational(c.numerator,c.denominator)
    return dict(out)


def main():
    _,cs=derive(5)
    basis=[]
    for k in range(5):
        basis.append((f'insert_P_{k}',transform(cs[4],lambda w:w[:k]+(max(w)+1,)+w[k:])))
    for k in range(4):
        basis.append((f'duplicate_position_{k}',transform(cs[4],lambda w:w[:k]+(w[k],)+w[k:])))
    words=partitions(5)
    matrix=sp.Matrix([[p.get(w,0) for name,p in basis] for w in words])
    target=sp.Matrix([sp.Rational(cs[5].get(w,0)) for w in words])
    report={'basis':[name for name,p in basis],'rank':matrix.rank(),'augmented_rank':matrix.row_join(target).rank()}
    if report['rank']==report['augmented_rank']:
        report['solutions']=str(sp.linsolve((matrix,target)))
    here=Path(__file__).resolve().parent
    (here/'transport.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
