import lean_gym.interface_m
import tools.serialization -- TODO: Serialize Lean's standard raw expression format
import system.io

-- read eval print loop
namespace lean_gym

meta def deserialize_expr (sexpr : string) : interface_m expr :=
match (expr.deserialize sexpr) with
| (sum.inl error_msg) := throw (interface_ex.user_input_exception ("Error parsing s-expression: " ++ error_msg))
| (sum.inr h) := return h
end

meta def apply_tactic (t : tactic unit): interface_m tactic_state := do
ts <- interface_m.get_current_tactic_state,
catch (interface_m.run_tactic2 ts t) $ λ e, match e with
| interface_ex.tactic_exception error := throw (interface_ex.apply_tactic_exception error)
| e := throw e
end

meta def apply_tactic_request (ts : tactic_state) : lean_tactic -> interface_m tactic_state
| (lean_tactic.apply sexpr) := do
  h <- deserialize_expr sexpr,
  apply_tactic (tactic.interactive.concat_tags (tactic.apply h))
| (lean_tactic.cases sexpr) := do
  h <- deserialize_expr sexpr,
  apply_tactic (tactic.interactive.cases_core h [])
| lean_tactic.intro := apply_tactic (tactic.interactive.propagate_tags (tactic.intro1 >> tactic.skip))
| lean_tactic.split := apply_tactic (tactic.interactive.split)
| lean_tactic.left := apply_tactic (tactic.interactive.left)
| lean_tactic.right := apply_tactic (tactic.interactive.right)

meta def mk_new_goal (ts0 : tactic_state) (goal : expr) : interface_m tactic_state := do
interface_m.run_tactic2 ts0 $ (do
  v <- tactic.mk_meta_var goal,
  tactic.set_goals [v],
  return ()
)

meta def mk_new_goal2 (ts0 : tactic_state) (goal : pexpr) : interface_m tactic_state := do
interface_m.run_tactic2 ts0 $ (do
  exp <- tactic.to_expr goal,
  v <- tactic.mk_meta_var exp,
  tactic.set_goals [v],
  return ()
)

meta def change_goal (sexp : string) : interface_m unit := do
  goal_expr <- deserialize_expr sexp,
  ts0 <- interface_m.get_inital_tactic_state,
  ts <- mk_new_goal ts0 goal_expr,
  interface_m.reset_all_tactic_states ts

meta def change_goal_pp (goal : string) : interface_m unit := do
  config <- interface_m.read_config,
  match config.ps with
  | some ps := do
    pexp <- interface_m.parse_string ps goal,
    ts0 <- interface_m.get_inital_tactic_state,
    ts <- mk_new_goal2 ts0 pexp,
    interface_m.reset_all_tactic_states ts
  | none := throw $ interface_ex.user_input_exception 
    "In this configuration, the Lean parser is not available to enter goals as Lean expressions.  Use an s-expression or run in a different way."
  end

meta def change_state : lean_state_control -> interface_m unit
| (lean_state_control.jump_to_state state_index) := 
  interface_m.set_tactic_state state_index
| (lean_state_control.change_top_goal sexp) := 
  change_goal sexp
| (lean_state_control.change_top_goal_pp goal) :=
  change_goal_pp goal

meta def state_info_str (st_ix : nat) : tactic string := do
let s :=  "Proof state:",
st ← tactic.read,
let fmt := to_fmt st,
fmt <- tactic.pp fmt,
let s := s ++ "\n" ++ (to_string fmt),
let s := s ++ "\n",
let s := s ++ "\n" ++ "Current state index:",
let s := s ++ "\n" ++ (to_string st_ix),
let s := s ++ "\n",
s1 <- (do 
  let s1 := s ++ "\n" ++ "Local names:",
  lctx ← tactic.local_context,
  let ls := lctx.map (λ e, expr.representation.form_of_expr e),
  let s1 :=  s1 ++ "\n" ++ (string.intercalate "\n" ls),
  return s1
) <|> (return s),
return s1

meta def get_state_info (ts : tactic_state) (ix : nat): interface_m string := do
interface_m.run_tactic1 ts (state_info_str ix)

meta def eval_user_request : lean_server_request → interface_m lean_server_response
| (lean_server_request.apply_tactic tac) := catch (do
    ts <- interface_m.get_current_tactic_state,
    ts <- apply_tactic_request ts tac,
    ix <- interface_m.register_tactic_state ts,
    state_info <- get_state_info ts ix,
    let msg := "Tactic succeeded:" ++ "\n" ++ state_info,
    let result := lean_tactic_result.success msg,
    let response := lean_server_response.apply_tactic result,
    return response
  ) $ λ e, match e with
  | interface_ex.apply_tactic_exception fmt_opt := do
    let msg := match fmt_opt with
    | some fmt := "Tactic failed: " ++ (to_string (fmt ()))
    | none := "Tactic failed: <no message>"
    end,
    let result := lean_tactic_result.failure msg,
    let response := lean_server_response.apply_tactic result,
    return response
  | interface_ex.tactic_exception fmt_opt := do
    let msg := match fmt_opt with
    | some fmt := "Unable to apply tactic: " ++ (to_string (fmt ()))
    | none := "Unable to apply tactic: <no message>"
    end,
    let result := lean_tactic_result.server_error msg,
    let response := lean_server_response.apply_tactic result,
    return response
  | interface_ex.user_input_exception msg := do
    let msg := "Unable to apply tactic: " ++ msg,
    let result := lean_tactic_result.server_error msg,
    let response := lean_server_response.apply_tactic result,
    return response
  | e := throw e
  end
| (lean_server_request.change_state state_control) := catch (do
    change_state state_control,
    ts <- interface_m.get_current_tactic_state,
    ix <- interface_m.get_current_tactic_state_ix,
    state_info <- get_state_info ts ix,
    let msg := "state change succeeded:" ++ "\n" ++ state_info,
    let result := lean_state_result.success msg,
    let response := lean_server_response.change_state result,
    return response
  ) $ λ e, match e with
  | interface_ex.tactic_exception fmt_opt := do
    let msg := match fmt_opt with
    | some fmt := "State change failed: " ++ (to_string (fmt ()))
    | none := "State change failed: <no message>"
    end,
    let result := lean_state_result.server_error msg,
    let response := lean_server_response.change_state result,
    return response
  | interface_ex.user_input_exception msg := do
    let msg := "State change failed: " ++ msg,
    let result := lean_state_result.server_error msg,
    let response := lean_server_response.change_state result,
    return response
  | e := throw e
  end

meta def server_loop : interface_m unit := do
response <- catch (do 
  -- TODO: Might want to split into errors that are parsing errors (json type things) and ones that are bugs on my end
  request <- interface_m.read_io_request,
  eval_user_request request
) (λ e, 
  match e with
  | interface_ex.tactic_exception fmt_opt := do
    let msg := match fmt_opt with
    | some fmt := "Unexpected error processing request: " ++ (to_string (fmt ()))
    | none := "Unexpected error processing request: <no message>"
    end,
    let response := lean_server_response.error msg,
    return response
  | e := throw e 
  end
),
interface_m.write_io_response response,
server_loop

-- commands for running the interface
-- TODO: maybe it is better not to have the initial tactic state inside the config
--       so that the config can be made ahead of time
meta def run_server_from_tactic (server : json_server lean_server_request lean_server_response) : tactic (except interface_ex unit) := do
  ts <- get_state,
  let config : interface_config := {
    server := server,
    ps := none,
    initial_ts := ts
  },
  -- it is very important that we do something with `server_loop.run config`
  -- (like return it) otherwise it won't be executed
  return $ server_loop.run config
  
meta def get_parser_state : lean.parser lean.parser_state :=
λ ps, interaction_monad.result.success ps ps

meta def tactic_state_at_goal (goal : pexpr) : lean.parser tactic_state :=
lean.parser.of_tactic $ do
  e <- tactic.to_expr goal,
  v <- tactic.mk_meta_var e,
  tactic.set_goals [v],
  ts <- get_state,
  return ts

meta def run_server_from_parser (server : json_server lean_server_request lean_server_response) (goal : pexpr) : lean.parser (except interface_ex unit) := do
  ps <- get_parser_state,
  ts <- tactic_state_at_goal goal,
  let config : interface_config := {
    server := server,
    ps := ps,
    initial_ts := ts
  },
  -- it is very important that we do something with `server_loop.run config`
  -- (like return it) otherwise it won't be executed
  return $ server_loop.run config

meta def run_server_from_io (server : json_server lean_server_request lean_server_response): io unit := do
  io.run_tactic (run_server_from_tactic server),
  return ()

end lean_gym