import interface
open lean.parser
open interactive

meta def main_tactic : tactic unit := do
  ts <- get_state,
  let init_search_state := search_state.new ts,
  server_loop.run init_search_state,
  return ()

theorem foo : 1=1 := begin
main_tactic
end