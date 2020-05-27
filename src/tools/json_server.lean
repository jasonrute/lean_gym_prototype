import system.io
import tools.json
import tools.json_serialization
import tools.dumb_json

open json

/- A way to get data and put data (one line at a time), 
such as stdin/stdout, files, or a child process. -/
meta structure io_streams :=
-- get one line of text  It does not have a new line at the end.
(get_line : io string)
-- put one line of text  The input string will not have a new line at the end.
(put_str_ln : string → io unit)


/- Since io.fs.get_line both returns a char_buffer and ends
with a new line, this is a slight modification. -/
meta def io.fs.get_line_str (handle : io.handle) : io string := do
cb <- io.fs.get_line handle,
return (cb.take (cb.size - 1)).to_string  -- drop new_line at end


-- examples of streams

namespace io_streams

/- Built-in stdin and stdout streams.  Use these instead of
io.stdin and io.stdout as the latter two will interfere with 
the Lean language server if run in vscode/emacs. -/
meta def stdin_stdout_streams : io_streams := { 
  get_line := io.get_line,
  put_str_ln := io.put_str_ln
}

/- Read from a file handle (e.g. for testing) and write to stdout -/
meta def file_stdout_streams (read_handle : io.handle) : io_streams := { 
  get_line := io.fs.get_line_str read_handle,
  put_str_ln := io.put_str_ln
}

/- Read from a file handle and write to another file handle -/
meta def file_streams (read_handle : io.handle) (write_handle : io.handle): io_streams := { 
  get_line := io.fs.get_line_str read_handle,
  put_str_ln := λ s, io.fs.put_str_ln write_handle s >> io.fs.flush write_handle
}

/- Spawn a child process and pipe stdin and stdout -/
meta def child_process_streams (proc : io.proc.child) : io_streams := { 
  get_line := io.fs.get_line_str proc.stdout,
  put_str_ln := λ s, io.fs.put_str_ln proc.stdin s >> io.fs.flush proc.stdin
}

end io_streams


/- An implementation of a server with fixed request and response types.
It uses JSON as the intermediate format but one can specify the exact
protocal for reading and writing the JSON.  (One motivation is that reading
standard )  -/
meta structure json_server 
  /- The type of the message the external agent uses to request information from lean. -/
  (request_type : Type)
  /- The type of the response that Lean provides. -/
  (response_type : Type) 
  /- The request and response types must both be serializable as json. -/
  [has_to_json response_type]
  /- The request and response types must both be serializable as json. -/
  [has_from_json request_type] := 
/- Streams to read from and write to -/
(read_write : io_streams)
/- The protocol used to deserialize `json` type objects. -/
(get_json : io_streams → io json)
/- The protocol used to serialize `json` type objects. -/
(put_json : io_streams → (json → io unit))

namespace json_server

-- does this already exist?
meta def exceptional_to_io {α : Type} : exceptional α → io α
| (exceptional.success a) := return a
| (exceptional.exception e) := io.fail $ "Exception: " ++ to_string (e options.mk)

/- Reads one line, and converts it into JSON. (Unfortionately this is VERY slow in Lean 3.) -/
meta def get_standard_json (read_write : io_streams) : io json := do
s <- read_write.get_line,
exceptional_to_io (json.of_string s)

/- Reads a custom data format of json sent via multiple lines of text.) -/
meta def get_custom_json (read_write : io_streams) : io json := do
dumb_json.load_json read_write.get_line

/- Writes one line of standard JSON encoding.-/
meta def put_standard_json (read_write : io_streams) (j : json): io unit :=
read_write.put_str_ln (to_string j)

meta def send_response {α β : Type} [has_from_json α] [has_to_json β] (server : json_server α β) (response : β) : io unit := do
server.put_json server.read_write (to_json response)

meta def get_request {α β : Type} [has_from_json α] [has_to_json β] (server : json_server α β) : io α := do
j <- server.get_json server.read_write,
-- uncomment to debug json
--stderr <- io.stderr,
--io.fs.put_str_ln stderr (to_string j),
a <- exceptional_to_io (from_json α j),
return a

end json_server