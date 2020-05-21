import tactic.core  -- TODO: Remove this but need derive handler for monad
import tools.json_server
import lean_gym.api
import lean_gym.api_instances

/-
The interface monad is made of three parts
- A read-only configuration structure having  
  information on how to communicate with io and the parser as
  well as other read-only information.
- A "mutable" search-state datastructure which is used for keeping
  track of all the tactic states visited.  (When this monad calls a tactic
  it will do so explicitly by specifying the tactic_state to use.)
- An except output with many types of exceptions indicating various types
  of failures, which can be handled differently.
-/  

/- A read-only configuration structure having information on how to 
  communicate with io and the parser as well as other read-only information. -/
meta structure interface_config :=
/- Specifies how to communicate with an external process and what protocal to
use to pass json-like information. -/
(server : json_server lean_server_request lean_server_response)
/- An optional parser state.  This can only be gotten from running the 
interface through a parser, but it allows the external process to communicate
goals via lean syntax instead of more combersome methods. -/
(ps : option lean.parser_state := none)
/- The initial tactic state, used to seed the search_state. -/
(initial_ts : tactic_state)

/- A persistant search state data structure which is used for keeping
  track of all the tactic states visited.  (When this monad calls a tactic
  it will do so explicitly by specifying the tactic_state to use.) -/
meta structure interface_state :=
(tactic_states : list tactic_state)  -- if not fast enough, use a better lookup data structure
(current_ts_ix : nat) -- TODO: Remove after new API

meta def interface_state.initialize (ts : tactic_state) : interface_state := 
{ tactic_states := [ts], current_ts_ix := 0 }

meta def interface_state.size (state : interface_state) : nat := 
state.tactic_states.length

meta def interface_state.get (ix : nat) (state : interface_state) : option tactic_state :=
if ix < state.tactic_states.length then 
  state.tactic_states.nth (state.tactic_states.length - ix - 1) 
else 
  none

meta def interface_state.put (state : interface_state) (ts : tactic_state) : interface_state × nat :=
({ tactic_states := ts :: state.tactic_states, current_ts_ix := state.size }, state.size)

-- TODO: Remove after new API
meta def interface_state.set_current (state : interface_state) (ix : nat) : option interface_state :=
if ix < state.tactic_states.length then 
  some { tactic_states := state.tactic_states, current_ts_ix := ix }
else 
  none

/- Many types of exceptions indicating various types of failures, which can be 
handled differently. -/
meta inductive interface_ex
| tactic_exception (error : option (unit → format))
| parser_exception (error : option (unit → format))
| io_exception (error : option (unit → format))
| apply_tactic_exception (error : option (unit → format))
| user_input_exception (msg : string)
| unexpected_error (msg : string)
| other -- TODO: This is a placeholder.  Don't use
-- TODO: Add more as needed.



-- need to put the except inside the state_t for the desired backtracking properties
@[derive [monad]]
meta def interface_m (α : Type) : Type := reader_t interface_config (state_t interface_state (except interface_ex)) α 

-- show that interface_m is monad_except.  Don't know why this can't be done automatically.
meta def interface_m.throw {α : Type} (e : interface_ex) : interface_m α := do
reader_t.lift $ state_t.lift $ except.error e

meta def interface_m.catch {α : Type} (ma : interface_m α) (handle : interface_ex → interface_m α) : interface_m α :=
reader_t.mk $ λ config, state_t.mk $ λ state,
match (ma.run config).run state with
| except.error e := ((handle e).run config).run state
| e := e
end

meta instance interface_m_monad_except : monad_except interface_ex interface_m :=
{ throw := @interface_m.throw, catch := @interface_m.catch }

-- reader/state monad stuff
meta def interface_m.read_config : interface_m interface_config := reader_t.read
meta def interface_m.get_state : interface_m interface_state := reader_t.lift state_t.get
meta def interface_m.put_state (s : interface_state) : interface_m unit := reader_t.lift (state_t.put s)

-- running tactic, parser, and io monads

/- Run tactic and convert tactic failures to except.error (tactic_exception _) -/
meta def interface_m.run_tactic {α : Type} (ts : tactic_state) (t : tactic α) : interface_m (α × tactic_state) :=
match t ts with
| (interaction_monad.result.exception error ref ts') := throw (interface_ex.tactic_exception error)
| (interaction_monad.result.success a ts')  := return (a, ts')
end

/- Run tactic and throw away the new tactic state -/
meta def interface_m.run_tactic1 {α : Type} (ts : tactic_state) (t : tactic α) : interface_m α :=
do (a, _) <- interface_m.run_tactic ts t, return a

/- Run tactic and return only the tactic state -/
meta def interface_m.run_tactic2 {α : Type} (ts : tactic_state) (t : tactic α) : interface_m tactic_state :=
do (_, ts) <- interface_m.run_tactic ts t, return ts

/- Run the parser on a string -/
meta def interface_m.parse_string (ps : lean.parser_state) (s : string) : interface_m pexpr :=
match (lean.parser.with_input interactive.types.texpr s) ps with
| (interaction_monad.result.exception error ref s') := throw (interface_ex.parser_exception error)
| (interaction_monad.result.success a s) := return a.1
end

/- Run io monad
(Need a tactic state as an entry point.  I don't think it matters which one.) -/
meta def interface_m.run_io {α : Type} (ts : tactic_state) (i : io α) : interface_m α :=
match (tactic.unsafe_run_io i) ts with
| (interaction_monad.result.exception error ref ts') := throw (interface_ex.io_exception error)
| (interaction_monad.result.success a ts') := return a
end

/- Run this monad and return an except object.
It doesn't take an interface_state, which is instead seeded by the config.initial_ts. 
We don't return the final state, just the value of type α. -/
meta def interface_m.run {α : Type} (m : interface_m α) (config : interface_config) : except interface_ex α := 
let state := interface_state.initialize config.initial_ts in
((reader_t.run m config).run state).map(λ as, as.1)


namespace interface_m

-- abstractions for accessing config and state and modifying state

meta def get_tactic_state (ix : nat): interface_m tactic_state := do
state <- get_state,
match state.get(ix) with
| some ts := return ts
| none := throw $ interface_ex.user_input_exception $ "No state index " ++ repr(ix)
end

/- This is tactic state from the config used to initialize the monad -/
meta def get_inital_tactic_state : interface_m tactic_state := do
config <- read_config,
return config.initial_ts

-- TODO: Remove after new API
meta def get_current_tactic_state : interface_m tactic_state := do
state <- get_state,
match state.get(state.current_ts_ix) with
| some ts := return ts
| none := throw $ interface_ex.unexpected_error $ "BUG: Current state index " ++ repr(state.current_ts_ix) ++ " has not corresponding state."
end

-- TODO: Remove after new API
meta def set_tactic_state (ix : nat): interface_m unit := do
state <- get_state,
match state.set_current ix with
| some s := put_state s
| none := throw $ interface_ex.user_input_exception $ "No state index " ++ repr(ix)
end

-- TODO: Remove after new API
meta def get_current_tactic_state_ix : interface_m nat := do
state <- get_state,
return state.current_ts_ix

meta def register_tactic_state (ts : tactic_state) : interface_m nat := do
state <- get_state,
let (state, ix) := state.put ts,
put_state state,
return ix

meta def reset_all_tactic_states (ts0 : tactic_state) : interface_m unit := do
put_state (interface_state.initialize ts0)

meta def read_io_request : interface_m lean_server_request := do
config <- read_config,
let server := config.server,
let ts0 := config.initial_ts, -- run io from initial tactic_state.  I don't think it matters which one I use.
interface_m.run_io ts0 server.get_request

meta def write_io_response (response: lean_server_response) : interface_m unit := do
config <- read_config,
let server := config.server,
let ts0 := config.initial_ts,
interface_m.run_io ts0 (server.send_response response)

meta def debug (msg : string) : interface_m unit := do
config <- read_config,
let ts0 := config.initial_ts,
interface_m.run_tactic1 ts0 (tactic.trace msg)

end interface_m