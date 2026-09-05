namespace PPI

variable {A B C D : Prop}

/-- Phase 2 positive family 1: a three-edge implication chain. -/
theorem phase2Chain3
    (hAB : A → B) (hBC : B → C) (hCD : C → D) : A → D := by
  intro hA
  exact hCD (hBC (hAB hA))

/-- Phase 2 positive family 2: a two-edge route plus a third premise that does
    not participate in the certified derivation. -/
theorem phase2Shortcut
    (hAB : A → B) (hBD : B → D) (_hCD : C → D) : A → D := by
  intro hA
  exact hBD (hAB hA)

/-- Countermodel witness for Phase 2 negative family 1.

    Witness: A=true, B=true, C=false, D=false. Then A→B, C→B, C→D hold,
    while A→D fails. -/
theorem phase2ColliderCountermodel
    (hA : A) (_hAB : A → B) (_hCB : C → B) (_hCD : C → D)
    (hNotD : ¬ D) : ¬ (A → D) := by
  intro hAD
  exact hNotD (hAD hA)

/-- Countermodel witness for Phase 2 negative family 2.

    Witness: A=true, B=false, C=false, D=false. Then B→A, B→C, C→D hold,
    while A→D fails. -/
theorem phase2ReverseStartCountermodel
    (hA : A) (_hBA : B → A) (_hBC : B → C) (_hCD : C → D)
    (hNotD : ¬ D) : ¬ (A → D) := by
  intro hAD
  exact hNotD (hAD hA)

end PPI
