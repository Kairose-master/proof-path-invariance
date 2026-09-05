namespace PPI

variable {A B C R : Prop}

/-- Positive transitivity target. -/
theorem positiveTarget (hAB : A → B) (hBC : B → C) : A → C :=
  fun hA => hBC (hAB hA)

/-- Adding an arbitrary extra premise R cannot invalidate an already valid target.
    This certifies preservation, not semantic 'irrelevance' in every possible sense. -/
theorem positiveWithExtra
    (hAB : A → B) (hBC : B → C) (_hR : R) : A → C :=
  fun hA => hBC (hAB hA)

/-- A concrete countermodel schema for the reversed target.

    A=true, B=true, C=false satisfies A→B but falsifies B→C, so for the negative
    family below we instead use premises A→B and C→B; these do not entail A→C.
    The Boolean witness is represented propositionally by assumptions A, B, ¬C. -/
theorem negativeCountermodel
    (hA : A) (hAB : A → B) (_hCB : C → B) (hNotC : ¬ C) : ¬ (A → C) := by
  intro hAC
  exact hNotC (hAC hA)

/-- The same countermodel remains a countermodel after adding an arbitrary
    proposition R, provided R is satisfiable in the chosen witness. -/
theorem negativeCountermodelWithExtra
    (hA : A) (hAB : A → B) (_hCB : C → B) (hNotC : ¬ C) (_hR : R) : ¬ (A → C) := by
  intro hAC
  exact hNotC (hAC hA)

end PPI
