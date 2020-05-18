import data.buffer.parser
import init.data.unsigned
import tools.json

open parser

def Ws : parser unit :=
decorate_error "<whitespace>" $
many' $ one_of' " \t\x0d\n".to_list

def tok (s : string) := str s >> Ws

def StringChar : parser char :=
sat (λc, c ≠ '\"' ∧ c ≠ '\\' ∧ c.val > 0x1f)
 <|> (do str "\\",
         (str "t" >> return '\t') <|>
         (str "n" >> return '\n') <|>
         (str "\\" >> return '\\') <|>
         (str "\"" >> return '\"'))

def BasicString : parser string :=
str "\"" *> (many_char StringChar) <* str "\"" <* Ws

def String := BasicString

def PosInt : parser int :=
do s ← many_char1 (one_of "0123456789".to_list),
   Ws,
   return s.to_nat

def NegInt : parser int :=
do str "-",
   n <- PosInt,
   return (-n)

def Int : parser int := NegInt <|> PosInt

def Boolean : parser bool :=
(tok "true" >> return tt) <|>
(tok "false" >> return ff)

section json
parameter Json : parser json

def JsonNull : parser json := 
do
  tok "null",
  return json.jnull

def JsonBool : parser json := 
do
  b <- Boolean,
  return (json.jbool b)

def JsonInt : parser json := 
do
  i <- Int,
  return (json.jint i)

def JsonString : parser json := 
do
  s <- String,
  return (json.jstring s)
  
def JsonKeyValue : parser (string × json) := 
do
  k <- String,
  tok ":",
  v <- Json,
  return (k, v)

def JsonArray : parser json := 
do
  tok "[",
  js <- sep_by (tok ",") Json,
  Ws,
  tok "]",
  return (json.jarray js)

def JsonObject : parser json := 
do
  tok "{",
  Ws,
  kvs <- sep_by (tok ",") JsonKeyValue,
  Ws,
  tok "}",
  return (json.jobject kvs)

end json

-- TODO: This approach gives bad error messages since it tries all approachs 
-- even though you know by the first character which approach to try.
def Json : parser json :=
fix $ λ Json, 
  let inner := JsonArray Json <|> JsonObject Json <|> JsonInt <|> JsonNull <|> JsonBool <|> JsonString in
  Ws *> inner <* Ws

meta def json.of_string (s : string) : exceptional json := 
match run_string Json s with
| sum.inl msg := exceptional.fail msg
| sum.inr j := exceptional.success j
end

/-
meta def get_right {α β : Type} (s: α ⊕ β) : β :=
match s with
| (sum.inl a) := sorry
| (sum.inr b) := b
end

#eval to_string $ get_right $ run_string Json $ "true"
#eval to_string $ get_right $ run_string Json $ "false"
#eval to_string $ get_right $ run_string Json $ "0"
#eval to_string $ get_right $ run_string Json $ "1234124"
#eval to_string $ get_right $ run_string Json $ "-1231"
#eval to_string $ get_right $ run_string Json $ repr "abc"
#eval to_string $ get_right $ run_string Json $ "[0,1, [] ]"
#eval to_string $ get_right $ run_string Json $ "[0, true, -1, false, null, [] ]"
#eval to_string $ get_right $ run_string Json $ "{\"a\":0, \"v\" : true, \"b\": -1, \" a\\\\ \": false, \"a\":null, \"a\":[] }"
-/