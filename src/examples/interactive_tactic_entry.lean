import lean_gym.server

-- set up server
meta def  json_config : json_server lean_server_request lean_server_response := {
  read_write := io_streams.stdin_stdout_streams,
  get_json := json_server.get_custom_json,   -- use custom format since faster
  put_json := json_server.put_standard_json, -- use standard format  
}

theorem foo : 1=1 := begin
lean_gym.run_server_from_tactic json_config,
refl
end