inductive json
| jarray : list json → json
| jobject : list (string × json) → json
| jint : int → json
--| number_float : int → json  -- not handling float yet
| jstring : string → json
| jbool : bool → json
| jnull : json

namespace json

/- Using json as a dictionary -/

private meta def get_value_by_key (key : string): list (string × json) → option json
| [] := none
| (⟨k, v⟩ :: kvs) := if k = key then some v else get_value_by_key kvs

meta def get (key : string): json → option json
| (json.jobject kvs) := get_value_by_key key kvs
| _ := none

/- Serialization of json -/

meta def serialize : json → string
| (json.jarray js) := "[" ++ (string.intercalate ", " (js.map serialize)) ++ "]"
| (json.jobject kvs) := 
  let pair_strings := kvs.map (λ ⟨k, v⟩ , (repr k) ++ ": " ++ (serialize v)) in
  "{" ++ (string.intercalate ", " (pair_strings)) ++ "}"
| (json.jint i) := repr i
| (json.jstring s) := repr s
| (json.jbool tt) := "true"
| (json.jbool ff) := "false"
| json.jnull := "null"

meta instance json_has_to_string : has_to_string json := ⟨serialize⟩ 


/- Encoding objects to JSON for later serialization -/

class has_to_json (α : Type) :=
(to_json : α → json)

instance : has_to_json json :=
⟨id⟩

def to_json {α : Type} [has_to_json α] : α → json :=
has_to_json.to_json

-- json encoding for some basic lean types
instance int_has_to_json : has_to_json int := ⟨json.jint⟩
instance bool_has_to_json : has_to_json bool := ⟨json.jbool⟩
instance string_has_to_json : has_to_json string := ⟨json.jstring⟩
meta instance format_has_to_json : has_to_json format := 
⟨λ fmt, json.jstring $ to_string fmt⟩
instance list_has_to_json {α : Type} [has_to_json α] : has_to_json (list α) := 
⟨λ lst, json.jarray (lst.map to_json)⟩

-- these aren't basic json types but have natural maps to json

instance nat_has_to_json : has_to_json nat := ⟨λ n, to_json (int.of_nat n)⟩

-- algebraic datatypes (this is a pretty standard json encoding)

instance option_has_to_json (α : Type) [has_to_json α] : has_to_json (option α) := 
has_to_json.mk $ λ o, match o with 
| none := json.jobject [("none", json.jnull)]  -- could use null or empty object
| (some v) := json.jobject [("some", json.jobject [("val", to_json v)])]
end

instance sum_has_to_json (α β : Type) [has_to_json α] [has_to_json β] : has_to_json (α ⊕ β) := 
has_to_json.mk $ λ s, match s with 
| (sum.inl v) := json.jobject [("inl", json.jobject [("val", to_json v)])]  -- could use null or empty object
| (sum.inr v) := json.jobject [("inr", json.jobject [("val", to_json v)])]
end

instance prod_has_to_json (α β : Type) [has_to_json α] [has_to_json β] : has_to_json (α × β) := 
has_to_json.mk $ λ s, match s with 
| ⟨a, b⟩ := json.jobject [("fst", to_json a), ("snd", to_json b)]
end


/- Decoding objects to JSON for later serialization -/

meta class has_from_json (α : Type) :=
(from_json : json → exceptional α)

meta def from_json (α : Type) [has_from_json α] : json → exceptional α :=
has_from_json.from_json

-- decoding standard types

private meta def decode_json_int : json → exceptional int
| (json.jint i) := exceptional.success i
| j := exceptional.fail $ "Expecting integer, but found: " ++ (to_string j) 

meta instance int_has_from_json : has_from_json int := ⟨decode_json_int⟩  

private meta def decode_json_bool : json → exceptional bool
| (json.jbool b) := exceptional.success b
| j := exceptional.fail $ "Expecting bool, but found: " ++ (to_string j) 

meta instance bool_has_from_json : has_from_json bool := ⟨decode_json_bool⟩

private meta def decode_json_string : json → exceptional string
| (json.jstring i) := exceptional.success i
| j := exceptional.fail $ "Expecting string, but found: " ++ (to_string j) 

meta instance string_has_from_json : has_from_json string := ⟨decode_json_string⟩

private meta def decode_list_json {α : Type} [has_from_json α] : (list json) → exceptional (list α)
| [] := exceptional.success []
| (j :: js) := do
  a <- from_json α j,
  as <- decode_list_json js,
  return (a :: as)

private meta def decode_json_list {α : Type} [has_from_json α] : json → exceptional (list α)
| (json.jarray js) := decode_list_json js
| j := exceptional.fail $ "Expecting list, but found: " ++ (to_string j) 

meta instance list_has_from_json {α : Type} [has_from_json α] : has_from_json (list α) := 
⟨decode_json_list⟩

private meta def decode_json_nat (j : json) : exceptional nat :=
do
  i <- from_json int j,
  if i < 0 then 
    exceptional.fail $ "Expecting nonnegative integer, but found: " ++ (repr i)
  else
    exceptional.success i.to_nat

meta instance nat_has_from_json : has_from_json nat := ⟨decode_json_nat⟩


-- Look up in JSON objects

private meta def get_value_aux (key : string) : (list (string × json)) → exceptional (json × list (string × json))
| [] := exceptional.fail $ "Expecting key: " ++ (repr key)
| ((k, v) :: kvs) := 
  if k = key then
    exceptional.success (v, kvs)
  else do
    (v', kvs') <- get_value_aux kvs,
    return (v', (k, v) :: kvs)

meta def get_value (key : string) : json → exceptional json
| (json.jobject kvs) := do (v, _) <- get_value_aux key kvs, return v
| j := exceptional.fail $ "Expecting object, but found: " ++ (to_string j) 

private meta def get_values_aux : (list string) → (list (string × json)) → exceptional (list json)
| [] [] := exceptional.success []
| [] kvs := exceptional.fail $ "Object has extra keys: " ++ (to_string (json.jobject kvs))
| (k :: ks) kvs := do
  (v, kvs) <- get_value_aux k kvs,
  vs <- get_values_aux ks kvs,
  return (v :: vs)

meta def get_values (keys : list string) : json → exceptional (list json)
| (json.jobject kvs) := get_values_aux keys kvs
| j := exceptional.fail $ "Expecting object, but found: " ++ (to_string j) 

-- decode inductive types

meta def decoder_get_field_value (α : Type) [has_from_json α] (key : string) (kvs : list (string × json)) 
: exceptional (α × list (string × json)) := do
  (v, kvs) <- get_value_aux key kvs,
  a <- from_json α v,
  return (a, kvs)

meta def decoder_check_empty : list (string × json) →  exceptional unit
| [] := exceptional.success ()
| kvs := exceptional.fail $ "Object has extra keys: " ++ (to_string (json.jobject kvs))

private meta def decode_json_option {α : Type} [has_from_json α] : json → exceptional (option α)
| (json.jobject [("none", json.jobject kvs)]) := do
  decoder_check_empty kvs,
  return $ option.none
| (json.jobject [("some", json.jobject kvs)]) := do
  (val, kvs) <- decoder_get_field_value α "val" kvs,
  decoder_check_empty kvs,
  return $ option.some val
| j := exceptional.fail $ "Unexpected form for " ++ "option" ++ ", found: " ++ (to_string j)

meta instance option_has_from_json {α : Type} [has_from_json α] : has_from_json (option α) := 
⟨decode_json_option⟩

private meta def decode_json_sum {α : Type} {β : Type} [has_from_json α] [has_from_json β] : json → exceptional (α ⊕ β)
| (json.jobject [("inl", json.jobject kvs)]) := do
  (val, kvs) <- decoder_get_field_value α "val" kvs,
  decoder_check_empty kvs,
  return $ sum.inl val
| (json.jobject [("some", json.jobject kvs)]) := do
  (val, kvs) <- decoder_get_field_value β "val" kvs,
  decoder_check_empty kvs,
  return $ sum.inr val
| j := exceptional.fail $ "Unexpected form for " ++ "sum" ++ ", found: " ++ (to_string j)

meta instance sum_has_from_json {α : Type} {β : Type} [has_from_json α] [has_from_json β] : has_from_json (α ⊕ β) := 
⟨decode_json_sum⟩

-- decode structures

private meta def decode_json_prod {α : Type} {β : Type} [has_from_json α] [has_from_json β] : json → exceptional (α × β)
| (json.jobject kvs) := do
  (fst, kvs) <- decoder_get_field_value α "fst" kvs,
  (snd, kvs) <- decoder_get_field_value β "snd" kvs,
  decoder_check_empty kvs,
  return $ prod.mk fst snd
| j := exceptional.fail $ "Unexpected form for " ++ "prod" ++ ", found: " ++ (to_string j)

meta instance prod_has_from_json {α : Type} {β : Type} [has_from_json α] [has_from_json β] : has_from_json (α × β) := 
⟨decode_json_prod⟩


end json