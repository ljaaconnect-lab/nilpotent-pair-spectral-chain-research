import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Fintype.BigOperators

/-!
Compatibility of a finite spectral linear map with semantic interpretation.
The interpretation is a ring homomorphism, not an emitted scalar gate.
Fourier orthogonality, where used, is an explicit hypothesis on the kernel.
No extraction of an oriented coordinate is asserted here.
-/

namespace NativeSpectralInduction

open scoped BigOperators

variable {I J R S : Type*} [Fintype I] [Semiring R] [Semiring S]

def readout (coeff : J → I → R) (values : I → R) (k : J) : R :=
  ∑ f, coeff k f * values f

theorem map_readout (rho : R →+* S) (coeff : J → I → R)
    (values : I → R) (k : J) :
    rho (readout coeff values k) =
      readout (fun j f => rho (coeff j f)) (fun f => rho (values f)) k := by
  simp [readout]

theorem shared_phase_readout (coeff : J → I → R) (phase : I → R)
    (value : R) (k : J) :
    readout coeff (fun f => phase f * value) k =
      (∑ f, coeff k f * phase f) * value := by
  simp only [readout, Finset.sum_mul, mul_assoc]

theorem readout_of_kernel [DecidableEq J] (coeff : J → I → R)
    (phase : I → R) (target : J)
    (hkernel : ∀ k, (∑ f, coeff k f * phase f) = if k = target then 1 else 0)
    (value : R) (k : J) :
    readout coeff (fun f => phase f * value) k =
      if k = target then value else 0 := by
  rw [shared_phase_readout, hkernel]
  simp only [ite_mul, one_mul, zero_mul]

end NativeSpectralInduction

#print axioms NativeSpectralInduction.map_readout
#print axioms NativeSpectralInduction.shared_phase_readout
#print axioms NativeSpectralInduction.readout_of_kernel
