# The synchronized selection that remains

Provenance: the following read-only algebraic construction was supplied by
the collaborating `/root/arbor_constraints` agent during n64. It is recorded
as an informal derivation; n64's finite development score does not certify
it, and no new numerical test or Lean compiler run for it was performed.
It identifies a constructive missing projection, without an impossibility
claim or a lower-bound experiment.

Write m=n^2, gamma_n=(-1)^(n(n-1)/2), and B=(b_ij) for the generic formal
marked entries. Order the 2n core indices as u_1..u_n,v_1..v_n and the
2m edge ports as a_e,b_e interleaved. Let

    A0 = [[0,B],[-B^T,0]],
    T_(u_i,a_e)=delta_(row(e),i) b_e,
    T_(v_j,b_e)=delta_(col(e),j),
    Z = [[A0,T],[-T^T,0]].

The exact intended synchronized sum uses ports(S) for compatible matchings S.
Its Z principal Pfaffian is

    Pf Z[core,ports(S)] = gamma_n (-1)^|S| Q_S,
    Q_S = (-1)^(sum I+sum J) sign(tau_S) b_S det B[I^c,J^c].

Split the fixed K into real ports and the two dummy ports. The Okada master,
ordered as [core,Zports,dummy,Kports], is

    M = [[A0, T,       0,    0],
         [-T^T,0,     0,    I],
         [0,   0,     Kgg, Kgp],
         [0,  -I,     Kpg, Kpp]].

Its dimension is 2n+4m+2. In the Pfaffian expansion the synchronized term S
has shuffle sign (-1)^(m-|S|). Multiplying its whole paired-subset sum by
gamma_n (-1)^m therefore gives the required P(B). This supplies the correct
term-level sign bookkeeping. The full Pfaffian also includes selections
where only one port of an edge is retained.

The ordinary full contraction can be evaluated constructively. The block

    D = [[0,I],[-I,Kpp]],
    D^-1 = [[Kpp,-I],[I,0]]

is explicit, without a variable matrix inverse. Pfaffian elimination leaves
the core-plus-dummy matrix with core A0+T Kpp T^T and dummy couplings T Kpg.
Set r_i=sum_j b_ij and let J_n have upper entries one. Then its blocks are

    u,v: B-B=0,
    u,u: diag(r) J_n diag(r),
    v,v: -n^2 J_n,
    u,a_g: r; v,b_g: -n*1; Kgg=J_2.

Both parities of n give the full normalized master value

    gamma_n (-1)^m Pf(M) = n^n product_i r_i.

Consequently the still-unremoved nonsynchronized contribution is

    n^n product_i(sum_j b_ij) - P(B).

The incidence structure already eliminates incompatible synchronized
matchings, but it does not yet give a scalar compiler for the synchronized
projection. Counting the entire Pfaffian as that projection would omit this
specific contribution. This statement is a constructive identity about the
given expression, not a lower bound for another gadget or factorization.

## Sign averaging preserves exactly the earlier character route

Introduce edge signs eps_ij with eps_ij^2=1, multiply both ports' incidence
weights by eps_ij, and keep A0 fixed. Define

    R_i=sum_j eps_ij b_ij; C_j=sum_i eps_ij.

The effective u,v block again vanishes because eps^2=1; the two internal
blocks become diag(R)J_n diag(R) and -diag(C)J_n diag(C), with dummy
couplings R and -C. Its normalized full master is

    product_i R_i product_j C_j.

Averaging over independent edge signs retains exactly the synchronized
selections and hence yields P(B). This describes an exact projection, but
does not make its scalar implementation cheap. Under the correlated choice
eps_ij=delta_j,

    C_j=n delta_j,
    normalized master=n^n(product_j delta_j)
                      product_i(sum_j b_ij delta_j).

Its average divided by n^n is the already established n15 character formula,
with the delta->-delta symmetry reducing explicit signs to 2^(n-1). This is
recorded as a preserved earlier reduction, not as a new resolution or a new
development experiment.

The unclosed positive obligation is an explicit scalar synchronization
gadget or exact aggregate recurrence with a polynomial bound, constructed
from the original formal entries, the fixed port matrix and incidence data.
The coefficient-wise Pfaffians alone have not supplied that gadget.
