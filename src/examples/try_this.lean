import tactic.suggest

meta def try_this (s : string) : tactic unit :=
tactic.trace $ "Try this: " ++ s

example (m n : ℕ) : m + n = n + m :=
by try_this "induction m,\ninduction m"

example (m n : ℕ) : m + n = n + m :=
by library_search