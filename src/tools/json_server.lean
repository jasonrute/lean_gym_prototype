import system.io
import tools.json
import tools.json_serialization
import tools.dumb_json

open json

meta structure json_server 
  /- The type of the message the external agent uses to request information from lean. -/
  (request_type : Type)
  /- The type of the response that Lean provides. -/
  (response_type : Type) 
  /- The request and response types must both be serializable as json. -/
  [has_to_json response_type]
  /- The request and response types must both be serializable as json. -/
  [has_from_json request_type] := 
/- The function which sends a block of text ending in a new line to the external agent -/
(get_line : io string)
/- The function which reads the next block of text ending in a new line from the external agent -/
(put_line : string → io unit)
/- The function which coverts get_line above into an intermediate json representation.
Depending on the encoding of the json being sent, it may require reading multiple lines. -/
(get_json : (io string) → io json)
/- The function which coverts put_line above into an intermediate json representation.
Depending on the encoding of the json being sent, it may require writing multiple lines. -/
(put_json : (string → io unit) → (json → io unit))

namespace json_server

-- does this already exist?
meta def exceptional_to_io {α : Type} : exceptional α → io α
| (exceptional.success a) := return a
| (exceptional.exception e) := io.fail $ "Exception: " ++ to_string (e options.mk)

/- Reads one line, and converts it into JSON. (Unfortionately this is VERY slow in Lean 3.) -/
meta def get_standard_json (get_line : io string) : io json := do
s <- get_line, 
exceptional_to_io (json.of_string s)

/- Reads a custom data format of json sent via multiple lines of text.) -/
meta def get_custom_json (get_line : io string) : io json := do
dumb_json.load_json get_line

/- Writes one line of standard JSON encoding.-/
meta def put_standard_json (put_line : string → io unit) (j : json): io unit :=
put_line (to_string j)

meta def send_response {α β : Type} [has_from_json α] [has_to_json β] (server : json_server α β) (response : β) : io unit :=
server.put_json server.put_line (to_json response)

meta def get_request {α β : Type} [has_from_json α] [has_to_json β] (server : json_server α β) : io α := do
j <- server.get_json server.get_line,
a <- exceptional_to_io (from_json α j),
return a

end json_server