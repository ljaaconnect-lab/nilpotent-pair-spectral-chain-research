"""Reproducible exact checks for nonlinear pivot and connected-jet closure.

The modular ranks below certify rational rank lower bounds for the displayed
integer instances: all denominators are powers of a nonzero permanent.
They are not lower bounds against arbitrary scalar arithmetic circuits.
"""

import itertools
import json
import random
import sympy as s


def permanent(a):
    if not a:
        return 1
    return sum(a[0][j] * permanent([row[:j] + row[j+1:] for row in a[1:]])
               for j in range(len(a)))


def symbolic_checks():
    a, b, c, d, e, f, g, h, i, t = s.symbols('a b c d e f g h i t')
    matrix = [[a, b, c], [d, e, f], [g, h, i]]
    phi = s.Poly(permanent([[e+t*d*b, f+t*d*c], [h+t*g*b, i+t*g*c]]), t)
    assert s.expand(permanent(matrix) - a*phi.nth(0) - phi.nth(1)) == 0
    assert s.expand(phi.nth(2) - 2*b*c*d*g) == 0
    symbols4 = s.symbols('b0:16')
    matrix4 = [list(symbols4[4*ii:4*ii+4]) for ii in range(4)]
    phi4 = s.Poly(permanent([[matrix4[ii][jj]+t*matrix4[ii][0]*matrix4[0][jj]
                             for jj in range(1,4)] for ii in range(1,4)]),t)
    assert s.expand(permanent(matrix4)-matrix4[0][0]*phi4.nth(0)-phi4.nth(1)) == 0
    pair_sum = 0
    for rows in itertools.combinations(range(1,4),2):
        for cols in itertools.combinations(range(1,4),2):
            left = next(ii for ii in range(1,4) if ii not in rows)
            right = next(jj for jj in range(1,4) if jj not in cols)
            pair_sum += (s.prod(matrix4[ii][0] for ii in rows)
                         *s.prod(matrix4[0][jj] for jj in cols)*matrix4[left][right])
    assert s.expand(phi4.nth(2)-2*pair_sum) == 0
    assert s.expand(phi4.nth(3)-6*s.prod(matrix4[ii][0]*matrix4[0][ii]
                                      for ii in range(1,4))) == 0
    x, y, u, alpha, beta, cc, rr, ee = s.symbols('x y u alpha beta cc rr ee')
    lhs = ee+t*x*y+u*(cc+t*beta*x)*(rr+t*alpha*y)
    rhs = ee+u*cc*rr+t*(x+u*alpha*cc)*(y+u*beta*rr)
    rem = s.Poly(s.expand(lhs-rhs), t, u)
    assert all(tpower >= 2 or upower >= 2 for (tpower, upower), coeff in rem.terms())
    one = [[s.Integer(1)]*3 for _ in range(3)]
    two = [[s.Rational(1,3),1,1], [1,s.Rational(1,3),1], [1,1,3]]
    # Equal value and two separate first jets; unequal mixed second jet.
    vals = []
    for mat in (one, two):
        aa = [row[:] for row in mat]
        aa[0][0] += t
        aa[1][1] += u
        pp = s.Poly(permanent(aa), t, u)
        vals.append([str(pp.coeff_monomial(term)) for term in (1,t,u,t*u)])
    assert vals == [['6','2','2','1'], ['6','2','2','3']]
    # This complete rank-three interaction witness uses only allowed p=1,2,
    # at z=1; hence it lies inside the contract's actual input family.
    cc = s.Matrix([[1,2],[2,1],[1,1]])
    rr = cc.T
    kk = cc*s.Matrix([[2,1],[1,1]])*rr
    pairs = list(itertools.combinations(range(3),2))
    quartic = s.Matrix([
        [s.Rational(permanent([[cc[ii,jj] for jj in range(2)] for ii in ii_pair])
                    *permanent([[rr[ii,jj] for jj in jj_pair] for ii in range(2)]),3)
         -s.Rational(permanent([[kk[ii,jj] for jj in jj_pair] for ii in ii_pair]),9)
         for jj_pair in pairs] for ii_pair in pairs])
    assert quartic.det() == s.Rational(32,81)
    return {'three_by_three_pivot': True, 'four_by_four_all_rank_one_jets': True,
            'rank_one_exchange_mod_squares': True,
            'first_jets_do_not_determine_mixed_jet': vals,
            'allowed_input_quartic_rank_three': {'matrix':str(quartic),
                                                'determinant':str(quartic.det())}}


def submatrix(a, rows, cols):
    return [[a[i][j] for j in cols] for i in rows]


def ring_mul(x, y, prime):
    out = {}
    for (ix,jx), ax in x.items():
        for (iy,jy), ay in y.items():
            if ix & iy or jx & jy:
                continue
            key = ix | iy, jx | jy
            out[key] = (out.get(key, 0) + ax*ay) % prime
    return {key: value for key, value in out.items() if value}


def rank_mod(a, prime):
    a = [row[:] for row in a]
    rank = 0
    for col in range(len(a[0]) if a else 0):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inv = pow(a[rank][col], -1, prime)
        a[rank] = [v*inv % prime for v in a[rank]]
        for i in range(rank+1, len(a)):
            ratio = a[i][col]
            a[i] = [(v-ratio*w) % prime for v,w in zip(a[i],a[rank])]
        rank += 1
    return rank


def connected_ranks(k, m, rng, prime=1000003):
    # Eliminated block A, external-to-eliminated C, eliminated-to-external R.
    a = [[1+rng.randrange(8)**2 for _ in range(k)] for _ in range(k)]
    c = [[1+rng.randrange(8)**2 for _ in range(k)] for _ in range(m)]
    r = [[1+rng.randrange(8)**2 for _ in range(m)] for _ in range(k)]
    const = permanent(a) % prime
    assert const
    coeffs = {(0,0): const}
    small = tuple(range(k))
    large = tuple(range(m))
    for q in range(1, min(k,m)+1):
        inside = list(itertools.combinations(small,q))
        outside = list(itertools.combinations(large,q))
        rowparts = {(ii,ss): permanent(submatrix(c,ii,ss)) % prime
                    for ii in outside for ss in inside}
        colparts = {(tt,jj): permanent(submatrix(r,tt,jj)) % prime
                    for tt in inside for jj in outside}
        middles = {(ss,tt): permanent(submatrix(a,[v for v in small if v not in tt],
                                                      [v for v in small if v not in ss])) % prime
                   for ss in inside for tt in inside}
        for ii in outside:
            for jj in outside:
                val = sum(rowparts[ii,ss]*middles[ss,tt]*colparts[tt,jj]
                          for ss in inside for tt in inside) % prime
                coeffs[sum(1<<v for v in ii), sum(1<<v for v in jj)] = val
    inv_const = pow(const,-1,prime)
    h = {key: val*inv_const % prime for key,val in coeffs.items() if key != (0,0)}
    log = {}
    power = {(0,0):1}
    for q in range(1,m+1):
        power = ring_mul(power,h,prime)
        scale = (-1 if q % 2 == 0 else 1) * pow(q,-1,prime)
        for key,val in power.items():
            log[key] = (log.get(key,0)+scale*val) % prime
    ranks = {}
    for q in range(1,m+1):
        masks = [sum(1<<v for v in subset) for subset in itertools.combinations(large,q)]
        matrix = [[log.get((ii,jj),0) for jj in masks] for ii in masks]
        ranks[q] = {'rank':rank_mod(matrix,prime), 'dimension':len(masks)}
    return {'k':k,'m':m,'prime':prime,'A':a,'C':c,'R':r,'ranks':ranks}


if __name__ == '__main__':
    rng = random.Random(2026102417)
    out = {'symbolic': symbolic_checks(),
           'connected_boundary_jet_ranks':[connected_ranks(k,k+1,rng) for k in range(1,5)]}
    print(json.dumps(out,indent=2))
