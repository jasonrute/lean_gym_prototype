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

meta def pp_sexpr (ts : tactic_state) (sexpr : string) : interface_m string := do
exp <- deserialize_expr sexpr,
interface_m.run_tactic1 ts (do fmt <- tactic.pp exp, return fmt.to_string)

meta def inner_tactic_str (ts : tactic_state) : lean_tactic -> interface_m string
| (lean_tactic.skip) := return "skip"
| (lean_tactic.apply sexpr) := do
  h_str <- pp_sexpr ts sexpr,
  return $ "apply " ++ h_str
| (lean_tactic.cases sexpr) := do
  h_str <- pp_sexpr ts sexpr,
  return $ "cases " ++ h_str
| lean_tactic.intro := return "intro"
| lean_tactic.split := return "split"
| lean_tactic.left := return "left"
| lean_tactic.right := return "right"
| lean_tactic.exfalso := return "exfalso"

meta def tactic_str (ts : tactic_state) : tactic_focus -> lean_tactic -> interface_m string
| tactic_focus.default tac := inner_tactic_str ts tac
| (tactic_focus.focus1) tac := do
  inner_str <- inner_tactic_str ts tac,
  return ("focus { " ++ inner_str ++ " }")
| tactic_focus.all_goals tac := do
  inner_str <- inner_tactic_str ts tac,
  return ("all_goals { " ++ inner_str ++ " }")
| tactic_focus.any_goals tac := do
  inner_str <- inner_tactic_str ts tac,
  return ("any_goals { " ++ inner_str ++ " }")

-- TODO: Do I need the tactic state here?
meta def build_inner_tactic (ts : tactic_state) : lean_tactic -> interface_m (tactic unit)
| (lean_tactic.skip) := do
  return (tactic.interactive.skip)
| (lean_tactic.apply sexpr) := do
  h <- deserialize_expr sexpr,
  return (tactic.interactive.concat_tags (tactic.apply h))
| (lean_tactic.cases sexpr) := do
  h <- deserialize_expr sexpr,
  return (tactic.interactive.cases_core h [])
| lean_tactic.intro := return (tactic.interactive.propagate_tags (tactic.intro1 >> tactic.skip))
| lean_tactic.split := return (tactic.interactive.split)
| lean_tactic.left := return (tactic.interactive.left)
| lean_tactic.right := return (tactic.interactive.right)
| lean_tactic.exfalso := return (tactic.interactive.exfalso)

-- TODO: Do I need the tactic state here?
meta def build_tactic (ts : tactic_state) : tactic_focus -> lean_tactic -> interface_m (tactic unit)
| tactic_focus.default tac := build_inner_tactic ts tac
| (tactic_focus.focus1) tac := do
  t <- build_inner_tactic ts tac,
  return (tactic.focus1 t)
| tactic_focus.all_goals tac := do
  t <- build_inner_tactic ts tac,
  return (tactic.all_goals' t)
| tactic_focus.any_goals tac := do
  t <- build_inner_tactic ts tac,
  return (tactic.any_goals' t)

meta def execute_lean_tactic (ts : tactic_state) (focus : tactic_focus) (tac : lean_tactic) : interface_m tactic_state := do
t <- build_tactic ts focus tac,
catch (interface_m.run_tactic2 ts t) $ λ e, match e with
| interface_ex.tactic_exception error := throw (interface_ex.execute_tactic_exception error)
| e := throw e
end

def join (sep : string) : list string → string
| [x]     := x
| []      := ""
| (x::xs) := x ++ sep ++ join xs

meta def expr_to_string (e : expr bool.tt) : tactic string :=
do
  o ← tactic.get_options,
  tactic.set_options (options.mk.set_bool `pp.all tt),
  f ← tactic.pp e,
  tactic.set_options o,  -- set back to before
  return $ to_string f
  
meta def local_cxt_to_string (v : expr bool.tt) : tactic string := 
do 
  tp ← tactic.infer_type v,
  v_str ← expr_to_string v,
  tp_str ← expr_to_string tp,
  return $ v_str ++ "\n\n" ++ tp_str

meta def goal_to_string (g : expr) : tactic string :=
do 
  tactic.set_goals [g],
  goal ← tactic.target,
  local_cxt ← tactic.local_context,
  let local_cxt_len := list.length local_cxt,
  goal_str ← expr_to_string goal,
  local_cxt_strs ← (list.mmap local_cxt_to_string local_cxt),
  let s1 := goal_str ++ "\n\n",
  let s2 := "Local Context Vars: " ++ (to_string local_cxt_len) ++ "\n\n",
  let s3 := join "\n\n" local_cxt_strs,
  return $ s1 ++ s2 ++ s3

meta def pp_state (pp_all : bool) : tactic string := do 
  -- set the pretty printer settings
  -- must do before retrieving the state since they 
  -- change the way that the state prints itself!
  opt ← tactic.get_options,
  tactic.set_options (opt.set_bool `pp.all pp_all),
  -- read state and format it
  state <- tactic.read,
  fmt <- tactic.pp state,
  -- set pp settings back to normal
  tactic.set_options (opt.set_bool `pp.all ff),
  return $ to_string fmt

meta def pp_expr (pp_all : bool) (exp : expr): tactic string := do 
  -- set the pretty printer settings
  opt ← tactic.get_options,
  tactic.set_options (opt.set_bool `pp.all pp_all),
  -- format exp
  fmt <- tactic.pp exp,
  -- set pp settings back to normal
  tactic.set_options (opt.set_bool `pp.all ff),
  return $ to_string fmt
  
meta def local_info_tac (cfg : local_info_config) (local_var : expr) : tactic local_report := do
  -- local variable name
  local_var_name <- if cfg.local_var_name then 
    do pp_str <- pp_expr ff local_var, return (some pp_str)
  else
    return none,

  -- local variable s-expression
  let local_var_sexp := if cfg.local_type_sexp then 
    some (expr.representation.form_of_expr local_var)
  else
    none,
  
  -- local variable type
  local_type <- tactic.infer_type local_var,

  -- local variable type pp
  local_type_pp <- if cfg.local_type_pp then 
    do pp_str <- pp_expr ff local_type, return (some pp_str)
  else
    return none,
  
  -- local variable type pp_all
  local_type_pp_all <- if cfg.local_type_pp then 
    do pp_str <- pp_expr tt local_type, return (some pp_str)
  else
    return none,

  -- local variable type s-expression
  let local_type_sexp := if cfg.local_type_sexp then 
    some (expr.representation.form_of_expr local_type)
  else
    none,

  return { local_report .
    local_var_hash := if cfg.local_var_hash then some local_var.hash else none,
    local_var_name := local_var_name,
    local_var_sexp := local_var_sexp,
    local_type_hash := if cfg.local_type_hash then some local_type.hash else none,
    local_type_pp := local_type_pp,
    local_type_pp_all := local_type_pp_all,
    local_type_sexp := local_type_sexp
  }

meta def goal_info_tac (cfg : goal_info_config) (goal : expr) : tactic goal_report := do
  -- set goal and get target
  tactic.set_goals [goal],
  target <- tactic.target,
  
  -- pretty printed target
  target_pp <- if cfg.target_pp then do 
    pp_str <- pp_expr ff target, 
    return (some pp_str)
  else
    return none,

  -- pretty printed target with pp_all
  target_pp_all <- if cfg.target_pp_all then do 
    pp_str <- pp_expr tt target, 
    return (some pp_str)
  else
    return none,

  -- target as s-expression
  let target_sexp := if cfg.target_sexp then do
    some (expr.representation.form_of_expr target)
  else
    none,

  -- local context
  local_cxt ← tactic.local_context,
  local_reports <- match cfg.locals with
  | some local_cfg := do
    reports <- local_cxt.mmap (local_info_tac local_cfg),
    return (some reports)
  | none := return none
  end,

  return $ { goal_report . 
    target_hash := if cfg.target_hash then some target.hash else none,
    target_pp := target_pp,
    target_pp_all := target_pp_all,
    target_sexp := target_sexp,
    local_cnt := if cfg.local_cnt then some local_cxt.length else none,
    locals := local_reports
  }

meta def state_info_tac (cfg : state_info_config) : tactic state_report := do  
  state <- tactic.read,
  
  -- pretty printed state
  state_pp <- if cfg.state_pp then 
    do pp_str <- pp_state ff, return (some pp_str)
  else
    return none,

  -- pretty printed state with pp_all
  state_pp_all <- if cfg.state_pp then 
    do pp_str <- pp_state tt, return (some pp_str)
  else
    return none,

  -- goal information
  goals ← tactic.get_goals,
  goal_reports <- match cfg.goals with
  | some goal_cfg := do
    reports <- goals.mmap (goal_info_tac goal_cfg),
    return (some reports)
  | none := return none
  end,

  return $ { state_report .
    is_solved := goals.empty,
    proof_path_ixs := none, -- filled in later
    proof_string := none, -- filled in later
    state_pp := state_pp,
    state_pp_all := state_pp_all,
    goal_cnt := if cfg.goal_cnt then some goals.length else none,
    goals := goal_reports
  }

meta def get_state_info (ts : tactic_state) (ix : nat) (cfg : state_info_config) : interface_m state_report := do
  -- retrieve information from tactic state 
  report <- interface_m.run_tactic1 ts (state_info_tac cfg),

  -- get proof information which is stored in the interface_m state
  proof_path_ixs <- if cfg.proof_path_ixs then do
    proof <- interface_m.get_proof_path ix,
    return (some proof)
  else return none,
  proof_string <- if cfg.proof_string then do
    proof <- interface_m.get_pp_proof ix,
    return (some proof)
  else return none,

  return { 
    proof_path_ixs := proof_path_ixs, 
    proof_string := proof_string, 
    ..report }



meta def handle_execute_tactic (ix : nat) (focus : tactic_focus) (tac : lean_tactic) (cfg : state_info_config) : interface_m lean_server_response :=
catch (do  
  ts <- interface_m.get_tactic_state ix,
  tac_str <- tactic_str ts focus tac,
  ts2 <- execute_lean_tactic ts focus tac,
  ix2 <- interface_m.register_tactic_state ts2 ix tac_str,
  state_info <- get_state_info ts ix cfg,
  let result := lean_tactic_result.success ix2 state_info,
  return (lean_server_response.execute_tactic result)
) $ λ e, match e with
| (interface_ex.execute_tactic_exception _) := do
  let result := lean_tactic_result.failure e.to_string,
  return (lean_server_response.execute_tactic result)
| e := do
  let msg := "execute_tactic failed:\n" ++ e.to_string,
  return (lean_server_response.error msg)
end
  

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

meta def mk_goal_sexp (sexp : string) : interface_m tactic_state := do
  goal_expr <- deserialize_expr sexp,
  ts0 <- interface_m.get_initial_tactic_state,
  mk_new_goal ts0 goal_expr

meta def mk_goal_pp (goal : string) : interface_m tactic_state := do
  config <- interface_m.read_config,
  match config.ps with
  | some ps := do
    pexp <- interface_m.parse_string ps goal,
    ts0 <- interface_m.get_initial_tactic_state,
    mk_new_goal2 ts0 pexp
  | none := throw $ interface_ex.user_input_exception 
    "In this configuration, the Lean parser is not available to enter goals as Lean expressions.  Use an s-expression or run in a different way."
  end

meta def mk_goal : lean_goal -> interface_m tactic_state
| (lean_goal.target_sexp sexp) := mk_goal_sexp sexp
| (lean_goal.target_pp pp_goal) := mk_goal_pp pp_goal

meta def change_goal (goal : lean_goal) : interface_m (tactic_state × nat) := do
ts <- mk_goal goal,
ix <- interface_m.reset_all_tactic_states ts,
return (ts, ix)

meta def handle_change_goal (goal : lean_goal) (cfg : state_info_config) : interface_m lean_server_response :=
catch (do
  (ts, ix) <- change_goal goal,
  state_info <- get_state_info ts ix cfg,
  return (lean_server_response.change_goal state_info)
) $ λ e, do
  let msg := "change_goal failed:\n" ++ e.to_string,
  return (lean_server_response.error msg)

meta def handle_get_state_info (ix : nat) (cfg : state_info_config) : interface_m lean_server_response :=
catch (do
  ts <- interface_m.get_tactic_state ix,
  state_info <- get_state_info ts ix cfg,
  return (lean_server_response.get_state_info state_info)
) $ λ e, do
  let msg := "get_local_info failed:\n" ++ e.to_string,
  return (lean_server_response.error msg)

meta def eval_user_request : lean_server_request → interface_m lean_server_response
| (lean_server_request.execute_tactic state_ix focus tac cfg) := 
  handle_execute_tactic state_ix focus tac cfg
| (lean_server_request.change_goal goal cfg) := 
  handle_change_goal goal cfg
| (lean_server_request.get_state_info state_ix cfg) := 
  handle_get_state_info state_ix cfg
| (lean_server_request.exit msg state_ix) := 
  return (lean_server_response.exit msg state_ix)

meta def server_loop : interface_m ((option string) × (option tactic_state)) := do
response <- catch (do 
  -- TODO: Might want to split into errors that are parsing errors (json type things) and ones that are bugs on my end
  request <- interface_m.read_io_request,
  eval_user_request request
) (λ e, do
  let msg := "error reading and/or processing request:\n" ++ e.to_string,
  return (lean_server_response.error msg)
),
interface_m.write_io_response response,
match response with
| lean_server_response.exit msg (some state_ix) := do
  ts <- interface_m.get_tactic_state state_ix,
  return (msg, some ts)
| lean_server_response.exit msg none := return (msg, none)
| e := server_loop
end

-- commands for running the interface
-- TODO: maybe it is better not to have the initial tactic state inside the config
--       so that the config can be made ahead of time
meta def run_server_from_tactic (server : json_server lean_server_request lean_server_response) : tactic (except interface_ex (option string)) := do
  ts <- get_state,
  let config : interface_config := {
    server := server,
    ps := none,
    initial_ts := ts
  },
  -- it is very important that we do something with `server_loop.run config`
  -- (like return it) otherwise it won't be executed
  match server_loop.run config with
  | except.ok (msg, some ts) := do set_state ts, return (except.ok msg)
  | except.ok (msg, none) := return (except.ok msg)
  | except.error e := return (except.error e)
  end
  
meta def get_parser_state : lean.parser lean.parser_state :=
λ ps, interaction_monad.result.success ps ps

meta def tactic_state_at_goal (goal : pexpr) : lean.parser tactic_state :=
lean.parser.of_tactic $ do
  e <- tactic.to_expr goal,
  v <- tactic.mk_meta_var e,
  tactic.set_goals [v],
  ts <- get_state,
  return ts

meta def run_server_from_parser (server : json_server lean_server_request lean_server_response) (goal : pexpr) : lean.parser (except interface_ex (option string)) := do
  ps <- get_parser_state,
  ts <- tactic_state_at_goal goal,
  let config : interface_config := {
    server := server,
    ps := ps,
    initial_ts := ts
  },
  -- it is very important that we do something with `server_loop.run config`
  -- (like return it) otherwise it won't be executed
  return $ (server_loop.run config).map prod.fst

meta def run_server_from_io (server : json_server lean_server_request lean_server_response): io unit := do
  io.run_tactic (run_server_from_tactic server),
  return ()

end lean_gym