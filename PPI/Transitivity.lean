namespace PPI

variable {A B C D : Prop}

/-- The target entailment certified directly from two implications. -/
theorem direct₂ (hAB : A → B) (hBC : B → C) : A → C :=
  fun hA => hBC (hAB hA)

/-- The same target entailment written with an explicit valid intermediate proposition. -/
theorem factored₂ (hAB : A → B) (hBC : B → C) : A → C := by
  intro hA
  have hB : B := hAB hA
  exact hBC hB

/-- Three-step extension for a later robustness phase. -/
theorem factored₃
    (hAB : A → B) (hBC : B → C) (hCD : C → D) : A → D := by
  intro hA
  have hB : B := hAB hA
  have hC : C := hBC hB
  exact hCD hC

end PPI
