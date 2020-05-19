import interface
open lean.parser
open interactive

meta def main_tactic : tactic unit := do
  ts <- get_state,
  let init_search_state := search_state.new ts,
  server_loop.run init_search_state,
  return ()

meta def parse_string (ps : lean.parser_state) (s : string) : tactic pexpr :=
match (lean.parser.with_input interactive.types.texpr s) ps with
| (interaction_monad.result.exception error ref s') := tactic.failed
| (interaction_monad.result.success a s) := return a.1
end

meta def set_new_goal1 (goal : pexpr) : tactic unit :=
do
  e <- tactic.to_expr goal,
  v <- tactic.mk_meta_var e,
  tactic.set_goals [v],
  return ()

meta def get_parser_state : lean.parser lean.parser_state :=
λ ps, interaction_monad.result.success ps ps

@[user_command]
meta def parse_for_me_cmd (meta_info : interactive.decl_meta_info) (_ : interactive.parse (tk "parse_for_me")) : lean.parser unit :=
do e <- interactive.types.texpr,
   ps <- get_parser_state,
   lean.parser.of_tactic $ do
     let s := "foo + 10 = 20",
     pexp <- parse_string ps s,
     set_new_goal1 pexp,
     tactic.trace_state,
     main_tactic
.

--parse_for_me true .  -- will fail since can't access foo

def foo := 1

parse_for_me true . -- will succeed