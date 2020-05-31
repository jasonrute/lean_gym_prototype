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

/- Specify a top-level lean goal -/
meta inductive lean_goal
/- Goal target given as an s-expression -/
| target_sexp (sexp : string)
/- Goal target given as a pretty-printed lean code string, 
e.g. "∀ p : Prop, p → p". 
Only available in certain run configurations since it requires 
access to the Lean parser. -/
| target_pp (ppexpr : string)


meta inductive tactic_focus
/- Apply Lean's default focus for that tactic.  Many tactics only apply to 
the first goal, but some try to change all the goals. -/
| default
/- Focus on the first goal only. For many theorem proving gyms, this is the 
right approach. It mimicks Lean's `focus` tactic combinator. -/
| focus1
/- Apply the tactic to all goals and fail if any goal fails. 
This is for advanced use. It mimicks Lean's `all_goals` tactic combinator. -/
| all_goals
/- Apply the tactic to all goals and succeed if at least one goal changes. 
This is for advanced use.  It mimicks Lean's `any_goals` tactic combinator. -/
| any_goals

meta structure local_info_config :=
/- Lean-generated hash of the local variable. -/
(local_var_hash : bool)
/- Local variable name as a string -/
(local_var_name : bool)
/- Local variable as an s-expression -/
(local_var_sexp : bool)
/- Lean-generated hash of the local type. -/
(local_type_hash : bool)
/- Local type in standard pp form -/
(local_type_pp : bool)
/- Local type in pp_all form -/
(local_type_pp_all : bool)
/- Local type as an s-expression -/
(local_type_sexp : bool)

meta structure goal_info_config :=
(target_hash : bool)
(target_pp : bool)
(target_pp_all : bool)
(target_sexp : bool)
(local_cnt : bool)
(locals : option local_info_config)

meta structure state_info_config :=
(proof_path_ixs : bool)
(proof_string : bool)
(state_pp : bool)
(state_pp_all : bool)
(goal_cnt : bool)
(goals : option goal_info_config)

/- Request to the server -/
meta inductive lean_server_request
/- Apply a tactic to a tactic state and return information about the new state. -/
| execute_tactic (state_ix : nat) (focus : tactic_focus) (tactic : lean_tactic) (cfg : state_info_config)
/- Create a new goal, reset all the states, and return information about the new state. -/
| change_goal (goal : lean_goal) (cfg : state_info_config)
/- Return information about the new state. -/
| get_state_info (state_ix : nat) (cfg : state_info_config)
/- Exit the interface.  The message is mention and state will be passed to a lean
tactic.  If run inside an interactive tactic, the state_ix can be used to set 
what the state is after the tactic is run.  The message can be traced to the
user.  Pro tip: Any message with one or more lines of the form "Try it: <proof>" 
will be suggested for the user. -/
| exit (msg : option string) (state_ix : option nat)

meta structure local_report :=
/- Lean-generated hash of the local variable. -/
(local_var_hash : option nat)
/- Local variable name as a string -/
(local_var_name : option string)
/- Local variable as an s-expression -/
(local_var_sexp : option string)
/- Lean-generated hash of the local type. -/
(local_type_hash : option nat)
/- Local type in standard pp form -/
(local_type_pp : option string)
/- Local type in pp_all form -/
(local_type_pp_all : option string)
/- Local type as an s-expression -/
(local_type_sexp : option string)

meta structure goal_report :=
(target_hash : option nat)
(target_pp : option string)
(target_pp_all : option string)
(target_sexp : option string)
(local_cnt : option nat)
(locals : option (list local_report))

meta structure state_report :=
(is_solved : bool)
(proof_path_ixs : option (list nat))
(proof_string : option string)
(state_pp : option string)
(state_pp_all : option string)
(goal_cnt : option nat)
(goals : option (list goal_report))

meta inductive lean_tactic_result
| success (tactic_ix : nat) (state_info : state_report)
| failure (msg : string)

meta inductive lean_server_response
| execute_tactic (tactic_result : lean_tactic_result) 
| change_goal (state_info : state_report)
| get_state_info (state_info : state_report)
| exit (msg : option string) (state_ix : option nat)
| error (msg : string)
