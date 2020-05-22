/- Tactic grammer -/
meta inductive lean_tactic
| skip
| apply (sexp : string)
| cases (sexp : string)
| intro
| split
| left
| right
| exfalso

/- Manually change the state -/
meta inductive lean_state_control
/-  -/
| jump_to_state (state_index : nat)
| change_top_goal (sexp : string)
| change_top_goal_pp (sexp : string)

/- Request to the server -/
meta inductive lean_server_request
/-  -/
| apply_tactic (tactic : lean_tactic)
| change_state (control : lean_state_control)

meta inductive lean_tactic_result
| success (basic_goal_information : string)
| failure (msg : string)
| server_error (msg : string)

meta inductive lean_state_result
| success (basic_state_information : string)
| server_error (msg : string)

meta inductive lean_server_response
| apply_tactic (result : lean_tactic_result)
| change_state (result : lean_state_result)
| error (msg : string)