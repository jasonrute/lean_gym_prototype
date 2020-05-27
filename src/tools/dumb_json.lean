import tools.json
import system.io

namespace dumb_json

/- β is the output type and α is the internal type passed between loops (such as a counter) 
If f returns sum.inl a it loops again using a.  
If f returns sum.inr b it exists the loop and returns b -/
meta def io.better_iterate {e α β : Type} (a : α) (f : α → io (α ⊕ β)) : io β :=
do
s <- monad_io.iterate io.error (α ⊕ β) (sum.inl a : α ⊕ β) $ 
    λ x : α ⊕ β, match x with
    | sum.inl a0 := do s <- f a0, return (some s)
    | sum.inr b := return (none : option (α ⊕ β))
    end,
match s with
| sum.inr b := return b
| sum.inl a := io.fail "Unreachable state"
end

/- repeatedly applies f until failure and returns the list of results-/
meta def io.repeat_until_failure {α : Type} (f : io α) : io (list α) :=
(do a <- f, as <- io.repeat_until_failure, return (a :: as)) <|> return []

meta def require (b : bool) (msg : thunk string): io unit :=
if b then return () else io.fail ("Assersion error: " ++ msg ())

meta def load_one_array_item (readline : io string) (load_json_after_first_line : string → io json) : io json := do
  line <- readline,
  require (line ≠ "</ARRAY>") "",
  load_json_after_first_line line

meta def load_array (readline : io string) (load_json_after_first_line : string → io json) : io json :=
do 
  l <- io.repeat_until_failure (load_one_array_item readline load_json_after_first_line),
  return (json.jarray l)

meta def load_raw_string (readline : io string) (end_marker : string) : io string := do
let load_one_key_line: io string := (do
  line <- readline,
  require (line ≠ end_marker) "",
  return line) in
do 
  lines <- io.repeat_until_failure load_one_key_line,
  return (string.intercalate "\n" lines)

meta def load_key (readline : io string) : io string := do
load_raw_string readline "</KEY>"

meta def load_object (readline : io string) (load_json_after_first_line : string → io json) : io json :=
let load_one_key_value: io (string × json) := (do
  line <- readline,
  require (line = "<KEY>") "Expecting <KEY>",
  k <- load_key readline,
  line <- readline,
  v <- load_json_after_first_line line,
  return (k, v)) in
do 
  kvs <- io.repeat_until_failure load_one_key_value,
  return (json.jobject kvs)

meta def load_string (readline : io string) : io json := do
  s <- load_raw_string readline "</STRING>",
  return (json.jstring s)

meta def load_int (readline : io string) : io json := do
  s <- readline,
  line <- readline,
  require (line = "</INT>") "Expecting </INT>",
  let i : int := if s.front = '-' then 
    -(s.backn (s.length-1)).to_nat
  else 
    s.to_nat,
  return (json.jint i)

meta def load_float (readline : io string) : io json := do
io.fail "JSON floats are not supported yet"

meta def load_bool (readline : io string) : io json := do
  s <- readline,
  line <- readline,
  require (line = "</BOOL>") "Expecting </BOOL>",
  require (s = "false" ∨ s = "true") "",
  let b := if s = "true" then tt else ff,
  return (json.jbool b)

meta def load_null (readline : io string) : io json := do
  line <- readline,
  require (line = "</NULL>") "Expecting </NULL>",
  return (json.jnull)

meta def load_json_after_first_line (readline : io string) : string → io json
| first :=
  if first = "<ARRAY>" then
    load_array readline load_json_after_first_line
  else if first = "<OBJECT>" then
    load_object readline load_json_after_first_line
  else if first = "<STRING>" then
    load_string readline
  else if first = "<INT>" then
    load_int readline
  else if first = "<FLOAT>" then
    load_float readline
  else if first = "<BOOL>" then
    load_bool readline
  else if first = "<NULL>" then
    load_null readline
  else
  -- TODO: Better error messages here and elsewhere
    io.fail "Expecting <ARRAY> | <OBJECT> | <STRING> | <INT> | <FLOAT> | <BOOL> | <NULL>"

meta def load_json (readline : io string) : io json := do
  line <- readline,
  load_json_after_first_line readline line

end dumb_json