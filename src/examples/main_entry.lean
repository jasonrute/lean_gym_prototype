import interface

meta def main_tactic : tactic unit := do
  ts <- get_state,
  let init_search_state := search_state.new ts,
  server_loop.run init_search_state,
  return ()

meta def main : io unit :=
  io.run_tactic $ main_tactic