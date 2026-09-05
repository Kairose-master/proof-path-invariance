namespace PPI

variable {A B C : Prop}

/-- Conjunction introduction: a second certified logical family for later experiments. -/
theorem andIntro (hA : A) (hB : B) : A ∧ B := ⟨hA, hB⟩

/-- Left projection. -/
theorem andLeft (h : A ∧ B) : A := h.1

/-- A certified decomposition through a conjunction. -/
theorem throughConjunction
    (hAB : A → B) (hAC : A → C) : A → (B ∧ C) := by
  intro hA
  exact ⟨hAB hA, hAC hA⟩

end PPI
