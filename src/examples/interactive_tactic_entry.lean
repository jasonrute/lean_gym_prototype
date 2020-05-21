import interface
open lean.parser
open interactive

-- set up server
meta def server : json_server lean_server_request lean_server_response := {
  get_line := io.get_line,    -- communicate via stdin
  put_line := io.put_str_ln,  -- communicate via stdout
  get_json := json_server.get_custom_json,   -- use custom format since faster
  put_json := json_server.put_standard_json, -- use standard format  
}

theorem foo : 1=1 := begin
run_interface_from_tactic server
end