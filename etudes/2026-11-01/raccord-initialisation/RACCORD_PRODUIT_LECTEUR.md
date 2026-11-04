# Raccorder le produit compact au lecteur

**Branche exploratoire auxiliaire.** Après cette exploration, l'auteur
demande de conserver le raccord existant, sans nouvelle formule.
La reprise active est décrite dans `EXECUTION_RACCORD_EXISTANT.md`.

Cette reprise traite la demande de raccorder la source compacte et le
lecteur, depuis les entrées originales. Elle établit un raccord algébrique
général qui ne fournit plus les moments comme entrées. **Elle n'établit
pas encore une fermeture polynomiale en portes scalaires ordinaires.**
La distinction porte sur l'exécution du nouvel opérateur de fusion, pas
sur une initialisation laissée implicite dans les formules.

## 1. Entrées et paramètre de collision

Conserver les données du papier et le signe corrigé :

\[
B_{ij}=(1+a_{ij}^{2})z^{2^{in+j}},\qquad
t_j(f)=\omega^{fd_j},\qquad
\gamma_nq_{[n]}=\widetilde\Omega.
\]

Les indices vont de zéro à \(n-1\), \(n\ge1\). Le paramètre \(z\)
reste formel. Le symbole \(u\), distinct de \(z\), sert uniquement à
marquer le nombre de collisions. Partir des formes de lignes

\[
\ell_i(s)=\sum_j B_{ij}s_j,\qquad G_B(s)=\prod_i\ell_i(s).
\]

Pour une occupation \(m\in\mathbb N^n\), définir
\(\kappa(m)=\sum_j\binom{m_j}{2}\). Il s'agit d'une définition
utilisée dans la preuve, sans imposer une table d'occupations au circuit.

## 2. Un opérateur local qui raccorde les deux extrémités

Sur les polynômes en \(s\), poser

\[
(\mathsf S_{j,u}F)(s)=F(s_0,\ldots,u s_j,\ldots,s_{n-1}),
\qquad \mathsf U_{j,u}F=s_j\mathsf S_{j,u}F.
\]

L'opérateur de la ligne \(i\) est

\[
\boxed{\mathsf V_{i,u}=\sum_j B_{ij}\mathsf U_{j,u}.}
\]

Il vérifie sur chaque monôme

\[
\mathsf U_{j,u}s^m=u^{m_j}s^{m+e_j}.
\]

La valeur du produit d'opérateurs, initialisé par **le seul polynôme
constant 1**, est donc

\[
\boxed{\mathscr C_B(u;s)=
 (\mathsf V_{n-1,u}\cdots\mathsf V_{0,u})1.}
\]

À \(u=1\), \(\mathsf U_{j,1}\) est la multiplication ordinaire par
\(s_j\), donc \(\mathscr C_B(1;s)=G_B(s)\).
À \(u=0\), les opérateurs commutent et
\(\mathsf U_{j,0}^{2}=0\). Ils réalisent alors exactement l'annihilation
des répétitions de colonnes. La correction universelle transforme le
produit des orientations survivantes en \(\widetilde\Omega\).

Le choix d'une colonne à une étape ajoute \(m_j\) collisions aux
\(m_j\) occurrences déjà présentes. Ainsi, pour toute longueur de
composition, la puissance accumulée est \(\kappa(m)\). Si
\(G_B(s)=\sum_m g_m s^m\), on obtient l'identité générale

\[
\mathscr C_B(u;s)=\sum_m g_m u^{\kappa(m)}s^m.
\]

Cette dernière somme prouve la formule ; son développement n'est pas
l'architecture de circuit recherchée.

## 3. Fusion à tout ordre et raccord aux différences

La relation entière

\[
\kappa(m+r)=\kappa(m)+\kappa(r)+m\cdot r
\]

donne le produit bilinéaire

\[
s^m\star_u s^r=u^{m\cdot r}s^{m+r}.
\]

Il est associatif : les deux parenthésages de trois monômes ajoutent
le même exposant \(m\cdot r+m\cdot v+r\cdot v\). Il est également
commutatif et unitaire, y compris pour \(u=0\), avec \(0^0=1\).
Pour \(\mathcal D_u(s^m)=u^{\kappa(m)}s^m\),

\[
\mathcal D_u(FG)=\mathcal D_u(F)\star_u\mathcal D_u(G),
\qquad \mathcal D_u(\ell_i)=\ell_i.
\]

La fusion par \(\star_u\) et la composition des \(\mathsf V_{i,u}\)
décrivent donc exactement le même raccord. Aucun moment de \(G_B\)
n'intervient parmi leurs entrées.

Le raccord antérieur de \(T_yT_z=T_{y+z}\) aux différences donne,
pour le produit complet de degré \(n\),

\[
\boxed{
 (\delta_{t_{n-1}e_{n-1}}\cdots\delta_{t_0e_0}G_B)(0)
 =\mathscr C_B(0;t)=(\pi_n(L)G_B)(t).
}
\]

En effet, le premier membre annule les monômes auxquels manque une
variable, et le membre central annule ceux qui répètent une variable.
Au degré total \(n\) avec \(n\) variables, ils conservent exactement
\(s_0\cdots s_{n-1}\), avec la même valeur \(\prod_jt_j\).
Il s'agit d'une équivalence du produit entier et de son observation.

## 4. Le lecteur spectral directement raccordé

Poser \(h=\binom n2\). Le degré en \(u\) de
\(C_B(u;t):=\mathscr C_B(u;t)\) est au plus \(h\). Prendre
\(M>h\), puissance de deux, et un premier \(Q\) tel que
\(M\mid Q-1\) et \(N\mid Q-1\). Choisir \(\eta\) et \(\omega\)
d'ordres exacts \(M\) et \(N\), respectivement.
Comme dans le raccord du papier, \(N\) est une puissance de deux et
on peut prendre \(n<N\le2n\). Ces conditions impliquent
\(Q>\max(2,h)\). Le corps et ses racines sont ici des paramètres
admissibles fournis ; leur recherche déterministe générale n'est pas
comprise dans la borne.

L'orthogonalité des caractères, sans repliement puisque \(h<M\), donne

\[
\boxed{C_B(0;t)=\frac1M\sum_{\ell=0}^{M-1}C_B(\eta^\ell;t).}
\]

La chaîne entière s'écrit donc directement

\[
\boxed{
\mathcal Z_Q[k]=\widetilde\Omega\,
\operatorname{INTT}_N\left[
 \left(\frac1M\sum_{\ell=0}^{M-1}
   [\mathsf V_{n-1,\eta^\ell}\cdots
      \mathsf V_{0,\eta^\ell}1]_{s=t(f)}\right)_{f=0}^{N-1}
\right][k].
}
\]

Le premier axe spectral filtre les collisions ; le second conserve les
labels du papier. Le lecteur ne reçoit ni \(P_A\), ni une table de
moments déjà calculés. Les seules données sont \(a,z\), les labels et
les constantes de champ autorisées.

## 5. Portée exacte du résultat

Les \(B_{ij}\) se préparent en \(4n^2-1\) portes scalaires. Une fois
les valeurs de la table \(C_B(\eta^\ell;t(f))\) disponibles, ses
\(N\) moyennes coûtent \(NM\) portes, puis l'INTT coûte
\(2N\log_2N+N\) portes selon la convention du projet.

Si \(J(n,M,N)\) désigne le coût **depuis les \(B_{ij}\)** de la
préparation conjointe de cette table, le coût de cette réalisation est
donc au plus

\[
4n^2-1+J(n,M,N)+NM+2N\log_2N+N,
\]

hors génération des constantes indépendantes des données. Une compilation
globale pourrait aussi fusionner cette table avec ses moyennes.

La description des \(\mathsf V_{i,u}\) comporte polynomialement de
symboles. **Aucune borne polynomiale de leur action scalaire composée
n'est démontrée ici.** En particulier, remplacer \(\star_u\) ou une
substitution dans un polynôme intermédiaire par une porte de coût un
ne serait pas un compte en portes scalaires. Le raccord algébrique est
obtenu ; le raccord scalaire polynomial demandé reste à construire.

## 6. Preuves, contrôles et variantes

- `spectral/RACCORD_PAR_COLLISIONS.md` : preuve du produit déformé,
  raccord spectral et vérification avec \(z\) formel.
- `dualite/RACCORD_DUAL.md` : passage du lecteur à travers chaque forme
  de ligne, sans moments initiaux, pour un polynôme de lecture arbitraire.
- `moments/CONTRACTIONS_COLLISIONS.md` : contraction directe par graphes
  de collisions, lien exact avec les moments et formules des ordres 0 à 3.

Les programmes de vérification développent de petits cas pour comparer
les identités. Ces développements sont des oracles de test ; ils ne
constituent pas le circuit polynomial recherché. Les preuves écrites
sont générales ; la portée précise des preuves Lean est enregistrée
dans leurs rapports séparés.
