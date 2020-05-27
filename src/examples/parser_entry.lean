import lean_gym.server
open lean.parser
open interactive

-- set up server
meta def json_config : json_server lean_server_request lean_server_response := {
  read_write := io_streams.stdin_stdout_streams,
  get_json := json_server.get_custom_json,   -- use custom format since faster
  put_json := json_server.put_standard_json, -- use standard format  
}

@[user_command]
meta def run_lean_gym_server_with_goal_cmd (meta_info : interactive.decl_meta_info) (_ : interactive.parse (tk "run_lean_gym_server_with_goal")) : lean.parser unit :=
do 
  goal <- interactive.types.texpr,
  result <- lean_gym.run_server_from_parser json_config goal,
  match result with
  | except.ok (some p) := lean.parser.of_tactic (tactic.trace p)
  | _ := return ()
  end,
  return ()
.

run_lean_gym_server_with_goal 1 + 1 = 2 . -- will succeed