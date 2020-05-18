namespace interface.api

/- Some of the most commonly applied proof tactics in Lean. 
While an attempt has been made to keep the behavior the same
as Lean, there may be suptle differences. -/
meta inductive lean_tactic
| apply (sexp : string)
| cases (sexp : string)
| intro
| split
| left
| right
| skip

/- Set which information to return about the goal state. -/
meta structure information :=
(pp_goal_trace : string) 
(pp_all_goal_trace : string)
(target_exp : )
(lean_exp : bool)
(sexp : bool)


/- Set which goals to apply the tactic to -/
meta inductive goal_focus
/- Use the lean default behaviour for the tactic.
It may be to apply it to just the first goal (the target)
or to all the goals. -/
| default
/- Apply the tactic to one goal only.  The target goal has index zero. 
Unlike the `{ ... }` notation in Lean, this leaves all other goals 
visable in the tactic state.  (It is implemented via Lean's `focus1`
tactic combinator.) -/
| one_goal (goal_ix : nat)
/- Apply the tactic to all the goals. -/
| all_goals

/- The top level lean target. Used for reseting the target. -/
meta inductive new_target
/- Enter target as an s-expression. -/
| raw_expression (sexp : string)
/- Enter target as lean code which is then parsed into an expression.  
This requires the Lean server have access to the lean parser, which is not
always possible depending on the run configuration -/
| formatted (pretty_exp : string)
/- Enter a target by its declaration id.  The declaration must be theorem, etc. 
already in the environment. -/
| declaration (id : string)

/- Run configuration with information about the lean server -/
meta structure run_config
/- If the lean parser is available.  This can be used to enter top-level
targets via Lean code (instead of raw expressions). -/
(parser : bool)
/- Plain text field used for communication between the server and the agent. -/
(custom_config : string)

/- Get information from the environment about a declaration -/
meta inductive env_query
| lookup_decl (sexp : string)
| all_declarations

/- Request to the server -/
meta inductive server_request
/- Apply a tactic to a given state and choose which information to return -/
| apply_tactic (state_ix : nat) (focus : goal_focus) (tactic : lean_tactic) (info : information)
/- Change the top-level target. -/
| change_target (target : new_target) (reset_states : bool)
/- Ping lean server and get back configuration infomation -/
| get_config
/- Query information from the environment -/
| query_environment (query : env_query)
/- Submit a proof or partial proof to Lean -/
| submit (proof : tactic_proof) (score : int)
/- Exit -/
| exit








meta inductive lean_tactic_result
| success (basic_goal_information : string)
| failure (msg : string)
| server_error (msg : string)

meta inductive lean_state_result
| success (basic_state_information : string)
| server_error (msg : string)

meta inductive server_response
| apply_tactic (result : lean_tactic_result)
| change_state (result : lean_state_result)
| error (msg : string)

end interface.api