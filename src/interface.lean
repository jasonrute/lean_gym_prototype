import system.io
import tactic.core  -- for get_state, set_state
import tools.serialization -- TODO: Serialize Lean's standard raw expression format
import tools.json
import tools.json_server
import tools.json_serialization
import api
import api_classes

open io

/-
meta def tactic.to_ex {α : Type} (t : tactic α) : tactic (exceptional α) :=
λ s, match t s with
| (interaction_monad.result.exception (some fmt) ref s') := interaction_monad.result.success (exceptional.exception (λ _, fmt ())) s
| (interaction_monad.result.exception none ref s') := interaction_monad.result.success (exceptional.fail "") s
| (interaction_monad.result.success a s) := interaction_monad.result.success (exceptional.success a) s
end
-/

-- Data structures
meta structure search_state :=
(tactic_states : list tactic_state)
(current_state_ix : nat)

meta def search_state.size (state : search_state) : nat := state.tactic_states.length

meta def search_state.get (n : nat) (state : search_state) : option tactic_state :=
if n < state.tactic_states.length then 
  state.tactic_states.nth (state.tactic_states.length - n - 1) 
else 
  none

meta def search_state.put (state : search_state) (s : tactic_state) : search_state :=
⟨s :: state.tactic_states, state.size⟩ 

meta def search_state.new (initial_state : tactic_state) : search_state :=
⟨[initial_state], 0⟩

meta inductive interface_ex
| tactic_exception (error : option (unit → format))
| apply_tactic_exception (error : option (unit → format))
| user_input_exception (msg : string)
| other
-- add more as needed


-- TODO: Add server stuff as part of the interface monad as a reader
-- TODO: Add parser state as a reader as well
-- TODO: Don't extend tactic state (pass state to run_tactic explicitly)

-- need to put the except_t inside the state_t for the desired backtracking properties
@[derive [monad]]
meta def interface_m (α : Type) : Type := state_t search_state (except_t interface_ex tactic) α 

meta def interface_m.run {α : Type} (m : interface_m α) (s : search_state) : tactic (except interface_ex (α × search_state)) := 
(state_t.run m s).run

meta def get_search_state : interface_m search_state := state_t.get

meta def put_search_state (s : search_state) : interface_m unit := state_t.put s


/- Catch the error inside a tactic and convert to an except exception -/
private meta def catch_errors {α : Type} (t : tactic α) : tactic (except interface_ex α) :=
λ s, match t s with
| (interaction_monad.result.exception error ref s') := interaction_monad.result.success (except.error (interface_ex.tactic_exception error)) s
| (interaction_monad.result.success a s)  := interaction_monad.result.success (except.ok a) s
end

private meta def lift_to_ex {α : Type} (t : tactic α) : except_t interface_ex tactic α := do
e_a <- except_t.lift (catch_errors t),
match e_a with
| except.ok a := return a
| except.error e := throw e
end

/- Lift tactic to interface_m and convert tactic failures to except.error (tactic_exception _) -/
meta def interface_m.run_tactic {α : Type} (t : tactic α) : interface_m α :=
state_t.lift (lift_to_ex t)

-- for some reason this is only automatically derived if I use the raw combinators
meta def interface_m.throw {α : Type} (e : interface_ex) : state_t search_state (except_t interface_ex tactic) α := do
throw e

-- for some reason this is only automatically derived if I use the raw combinators
meta def interface_m.catch {α : Type} (ma : state_t search_state (except_t interface_ex tactic) α) (handle : interface_ex → state_t search_state (except_t interface_ex tactic) α) : state_t search_state (except_t interface_ex tactic) α := do
catch ma handle

meta instance interface_m_monad_except : monad_except interface_ex interface_m :=
{ throw := @interface_m.throw, catch := @interface_m.catch }



-- set up server
meta def server : json_server lean_server_request lean_server_response := {
  get_line := io.get_line,    -- communicate via stdin
  put_line := io.put_str_ln,  -- communicate via stdout
  get_json := json_server.get_custom_json,   -- use custom format since faster
  put_json := json_server.put_standard_json, -- use standard format  
}

-- manipulating the tactic state and the search state

meta def deserialize_expr (sexpr : string) : interface_m expr :=
match (expr.deserialize sexpr) with
| (sum.inl error_msg) := throw (interface_ex.user_input_exception ("Error parsing s-expression: " ++ error_msg))
| (sum.inr h) := return h
end

meta def set_new_goal (goal : expr) : interface_m unit :=
interface_m.run_tactic $ do
  v <- tactic.mk_meta_var goal,
  tactic.set_goals [v],
  return ()

meta def set_tactic_state (tactic_state_index : nat) : interface_m unit := do
states <- get_search_state,
match states.get tactic_state_index with
| some s := interface_m.run_tactic (set_state s)
| none := throw (interface_ex.user_input_exception "State index out of bounds")
end,
put_search_state { 
  tactic_states := states.tactic_states, 
  current_state_ix := tactic_state_index 
}

meta def register_tactic_state : interface_m unit := do
s <- interface_m.run_tactic get_state,
states <- get_search_state,
put_search_state (states.put s)

meta def get_tactic_state_ix : interface_m nat := do
states <- get_search_state,
return states.current_state_ix

meta def reset_all_tactic_states : interface_m unit := do
s <- interface_m.run_tactic get_state,
put_search_state (search_state.new s)




-- read eval print

meta def read_user_request : interface_m lean_server_request :=
interface_m.run_tactic (tactic.unsafe_run_io server.get_request)



meta def apply_tactic (t : tactic unit): interface_m unit := 
catch (interface_m.run_tactic t) $ λ e, match e with
| interface_ex.tactic_exception error := throw (interface_ex.apply_tactic_exception error)
| e := throw e
end

meta def apply_tactic_request : lean_tactic -> interface_m unit
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

meta def change_goal (sexp : string) : interface_m unit := do
  goal_expr <- deserialize_expr sexp,
  set_new_goal goal_expr,
  reset_all_tactic_states,
  register_tactic_state

meta def jump_to_tactic_state (state_index : nat) : interface_m unit := do
  set_tactic_state state_index

meta def change_state : lean_state_control -> interface_m unit
| (lean_state_control.jump_to_state state_index) := 
  set_tactic_state state_index
| (lean_state_control.change_top_goal sexp) := 
  change_goal sexp

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

meta def get_state_info : interface_m string := do
current_state_ix <- get_tactic_state_ix,
interface_m.run_tactic (state_info_str current_state_ix)

meta def eval_user_request : lean_server_request → interface_m lean_server_response
| (lean_server_request.apply_tactic tac) := catch (do
    apply_tactic_request tac,
    register_tactic_state,
    state_info <- get_state_info,
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
    register_tactic_state,
    state_info <- get_state_info,
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

meta def write_response (response: lean_server_response) : interface_m unit :=
interface_m.run_tactic $ tactic.unsafe_run_io (server.send_response response)

meta def server_loop : interface_m unit := do
response <- catch (do 
  -- TODO: Might want to split into errors that are parsing errors (json type things) and ones that are bugs on my end
  request <- read_user_request,
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
write_response response,
server_loop