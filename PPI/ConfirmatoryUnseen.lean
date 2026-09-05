namespace PPI

variable {A B C D : Prop}

/-- Confirmatory unseen family P1: the target implication is present directly,
    while the other two premises form an unrelated cycle. -/
theorem confirmDirectAnchor
    (hAD : A → D) (_hBC : B → C) (_hCB : C → B) : A → D :=
  hAD

/-- Confirmatory unseen family P2: two branches from A must be joined. -/
theorem confirmForkJoin
    (hAB : A → B) (hAC : A → C) (hBCD : B ∧ C → D) : A → D := by
  intro hA
  exact hBCD ⟨hAB hA, hAC hA⟩

/-- Confirmatory unseen family P3: an intermediate conjunction uses A itself. -/
theorem confirmConjunctionSource
    (hAB : A → B) (hABC : A ∧ B → C) (hCD : C → D) : A → D := by
  intro hA
  have hB : B := hAB hA
  have hC : C := hABC ⟨hA, hB⟩
  exact hCD hC

/-- Confirmatory unseen family P4: one premise produces a conjunction. -/
theorem confirmBranchToConjunction
    (hABC : A → B ∧ C) (hBD : B → D) (_hCD : C → D) : A → D := by
  intro hA
  exact hBD (hABC hA).1

/-- Countermodel for unseen family N1.
    Witness: A=true, B=true, C=true, D=false. -/
theorem confirmForkMissingJoinCountermodel
    (hA : A) (_hAB : A → B) (_hAC : A → C)
    (_hBDC : B ∧ D → C) (hNotD : ¬ D) : ¬ (A → D) := by
  intro hAD
  exact hNotD (hAD hA)

/-- Countermodel for unseen family N2.
    Witness: A=true, B=false, C=false, D=false. -/
theorem confirmReverseJoinCountermodel
    (hA : A) (_hBA : B → A) (_hCB : C → B)
    (_hBCD : B ∧ C → D) (hNotD : ¬ D) : ¬ (A → D) := by
  intro hAD
  exact hNotD (hAD hA)

/-- Countermodel for unseen family N3.
    Witness: A=true, B=true, C=false, D=false. -/
theorem confirmConjunctionGateCountermodel
    (hA : A) (_hAB : A → B) (_hBCD : B ∧ C → D)
    (_hDC : D → C) (hNotD : ¬ D) : ¬ (A → D) := by
  intro hAD
  exact hNotD (hAD hA)

/-- Countermodel for unseen family N4.
    Witness: A=true, B=true, C=true, D=false. -/
theorem confirmDownstreamCycleCountermodel
    (hA : A) (_hAB : A → B) (_hBC : B → C)
    (_hCDB : C ∧ D → B) (hNotD : ¬ D) : ¬ (A → D) := by
  intro hAD
  exact hNotD (hAD hA)

end PPI
