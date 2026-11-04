"""Regenerate the two integer tables embedded in the Lean certificate."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
MARKER = '-- GENERATED COUNTERTERM TABLES'


def main():
    tables = json.loads((HERE/'correcteurs.json').read_text(encoding='utf-8'))['orders']
    file = HERE/'PartitionCertificate.lean'
    text = file.read_text(encoding='utf-8')
    text = text.split(MARKER)[0].split('end OrientedOperators.PartitionCertificate')[0]
    text += MARKER+'\n'
    for r, table in tables.items():
        terms = ',\n    '.join('('+str(t['pattern'])+', '+str(t['coefficient'])+')'
                               for t in table['terms'])
        text += f'def c{r} : Poly := [\n    {terms}]\n\n'
    text += '''def h4 : Poly := moment 1 h3 ++ scale (-3) (moment 2 h2) ++
  scale 6 (moment 3 h1) ++ scale (-6) (moment 4 h0) ++ scale 4 c4

def h5 : Poly := moment 1 h4 ++ scale (-4) (moment 2 h3) ++
  scale 12 (moment 3 h2) ++ scale (-24) (moment 4 h1) ++ scale 24 (moment 5 h0) ++
  scale 8 (multiply c4 h1 ++ multiply h1 c4) ++ scale 16 c5

def normalForm (r : Nat) (p : Poly) : Poly :=
  (partitions r).map fun w => (w, coeff w p)

def supported (r : Nat) (p : Poly) : Bool :=
  p.all fun t => (partitions r).contains t.1

theorem order4_certificate : normalForm 4 h4 = normalForm 4 (exact 4) := by
  decide

theorem order5_certificate : normalForm 5 h5 = normalForm 5 (exact 5) := by
  decide

theorem certificates_have_complete_support :
    supported 4 h4 && supported 5 h5 = true := by
  decide

theorem lower_orders_certificate :
    normalForm 0 h0 = normalForm 0 (exact 0) ∧
    normalForm 1 h1 = normalForm 1 (exact 1) ∧
    normalForm 2 h2 = normalForm 2 (exact 2) ∧
    normalForm 3 h3 = normalForm 3 (exact 3) := by
  decide

def repeatedBlocks (w : Pattern) : Nat :=
  ((List.range (arity w)).filter fun j => 2 ≤ blockSize w j).length

theorem quintic_contraction_bound :
    c5.length = 44 ∧ (c5.all fun t => repeatedBlocks t.1 ≤ 2) = true := by
  decide

#print axioms order4_certificate
#print axioms order5_certificate
#print axioms certificates_have_complete_support
#print axioms lower_orders_certificate
#print axioms quintic_contraction_bound

end OrientedOperators.PartitionCertificate
'''
    file.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
