import lean_gym.server

-- set up server
meta def  json_config : json_server lean_server_request lean_server_response := {
  read_write := io_streams.stdin_stdout_streams,
  get_json := json_server.get_custom_json,   -- use custom format since faster
  put_json := json_server.put_standard_json, -- use standard format  
}

meta def my_tactic : tactic unit := do
child ← tactic.unsafe_run_io $ io.proc.spawn {
  cmd := "python3",
  args := ["lean_gym/gym/example_app.py", "--app"],
  stdout := io.process.stdio.piped,
  stdin := io.process.stdio.piped,
},
let json_config : json_server lean_server_request lean_server_response := {
  read_write := io_streams.child_process_streams child,
  get_json := json_server.get_custom_json,   -- use custom format since faster
  put_json := json_server.put_standard_json, -- use standard format  
},
out <- lean_gym.run_server_from_tactic json_config,
match out with
| except.error e := tactic.trace "There was an error"
| except.ok (some s) := tactic.trace s
| except.ok none := return ()
end,
return ()

example : (∀ p q : Prop, q → p → q) := 
begin
--my_tactic,
intro, intro, intro, intro, apply a
end