import lean_gym.server

-- set up server
meta def json_config : json_server lean_server_request lean_server_response := {
  get_line := io.get_line,    -- communicate via stdin
  put_line := io.put_str_ln,  -- communicate via stdout
  get_json := json_server.get_custom_json,   -- use custom format since faster
  put_json := json_server.put_standard_json, -- use standard format  
}

meta def main : io unit :=
  lean_gym.run_server_from_io json_config
  