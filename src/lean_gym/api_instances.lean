/- This file is autogenerated by a script -/
import lean_gym.api
import tools.json
open json

meta instance lean_tactic_has_to_json : has_to_json lean_tactic := 
has_to_json.mk $ λ s, match s with
| (lean_tactic.skip ) := json.jobject [("skip", json.jobject [])]
| (lean_tactic.apply sexp) := json.jobject [("apply", json.jobject [("sexp", to_json sexp)])]
| (lean_tactic.cases sexp) := json.jobject [("cases", json.jobject [("sexp", to_json sexp)])]
| (lean_tactic.intro ) := json.jobject [("intro", json.jobject [])]
| (lean_tactic.split ) := json.jobject [("split", json.jobject [])]
| (lean_tactic.left ) := json.jobject [("left", json.jobject [])]
| (lean_tactic.right ) := json.jobject [("right", json.jobject [])]
| (lean_tactic.exfalso ) := json.jobject [("exfalso", json.jobject [])]
end

private meta def decode_json_lean_tactic : json → exceptional lean_tactic
| (json.jobject [("skip", json.jobject kvs)]) := do
  decoder_check_empty kvs,
  return $ lean_tactic.skip 
| (json.jobject [("apply", json.jobject kvs)]) := do
  (sexp, kvs) <- decoder_get_field_value string "sexp" kvs,
  decoder_check_empty kvs,
  return $ lean_tactic.apply sexp
| (json.jobject [("cases", json.jobject kvs)]) := do
  (sexp, kvs) <- decoder_get_field_value string "sexp" kvs,
  decoder_check_empty kvs,
  return $ lean_tactic.cases sexp
| (json.jobject [("intro", json.jobject kvs)]) := do
  decoder_check_empty kvs,
  return $ lean_tactic.intro 
| (json.jobject [("split", json.jobject kvs)]) := do
  decoder_check_empty kvs,
  return $ lean_tactic.split 
| (json.jobject [("left", json.jobject kvs)]) := do
  decoder_check_empty kvs,
  return $ lean_tactic.left 
| (json.jobject [("right", json.jobject kvs)]) := do
  decoder_check_empty kvs,
  return $ lean_tactic.right 
| (json.jobject [("exfalso", json.jobject kvs)]) := do
  decoder_check_empty kvs,
  return $ lean_tactic.exfalso 
| j := exceptional.fail $ "Unexpected form for " ++ "lean_tactic" ++ ", found: " ++ (to_string j)

meta instance lean_tactic_has_from_json : has_from_json lean_tactic := 
⟨decode_json_lean_tactic⟩


meta instance lean_state_control_has_to_json : has_to_json lean_state_control := 
has_to_json.mk $ λ s, match s with
| (lean_state_control.jump_to_state state_index) := json.jobject [("jump_to_state", json.jobject [("state_index", to_json state_index)])]
| (lean_state_control.change_top_goal sexp) := json.jobject [("change_top_goal", json.jobject [("sexp", to_json sexp)])]
| (lean_state_control.change_top_goal_pp sexp) := json.jobject [("change_top_goal_pp", json.jobject [("sexp", to_json sexp)])]
end

private meta def decode_json_lean_state_control : json → exceptional lean_state_control
| (json.jobject [("jump_to_state", json.jobject kvs)]) := do
  (state_index, kvs) <- decoder_get_field_value nat "state_index" kvs,
  decoder_check_empty kvs,
  return $ lean_state_control.jump_to_state state_index
| (json.jobject [("change_top_goal", json.jobject kvs)]) := do
  (sexp, kvs) <- decoder_get_field_value string "sexp" kvs,
  decoder_check_empty kvs,
  return $ lean_state_control.change_top_goal sexp
| (json.jobject [("change_top_goal_pp", json.jobject kvs)]) := do
  (sexp, kvs) <- decoder_get_field_value string "sexp" kvs,
  decoder_check_empty kvs,
  return $ lean_state_control.change_top_goal_pp sexp
| j := exceptional.fail $ "Unexpected form for " ++ "lean_state_control" ++ ", found: " ++ (to_string j)

meta instance lean_state_control_has_from_json : has_from_json lean_state_control := 
⟨decode_json_lean_state_control⟩


meta instance lean_server_request_has_to_json : has_to_json lean_server_request := 
has_to_json.mk $ λ s, match s with
| (lean_server_request.apply_tactic tactic) := json.jobject [("apply_tactic", json.jobject [("tactic", to_json tactic)])]
| (lean_server_request.change_state control) := json.jobject [("change_state", json.jobject [("control", to_json control)])]
| (lean_server_request.exit msg) := json.jobject [("exit", json.jobject [("msg", to_json msg)])]
end

private meta def decode_json_lean_server_request : json → exceptional lean_server_request
| (json.jobject [("apply_tactic", json.jobject kvs)]) := do
  (tactic, kvs) <- decoder_get_field_value lean_tactic "tactic" kvs,
  decoder_check_empty kvs,
  return $ lean_server_request.apply_tactic tactic
| (json.jobject [("change_state", json.jobject kvs)]) := do
  (control, kvs) <- decoder_get_field_value lean_state_control "control" kvs,
  decoder_check_empty kvs,
  return $ lean_server_request.change_state control
| (json.jobject [("exit", json.jobject kvs)]) := do
  (msg, kvs) <- decoder_get_field_value string "msg" kvs,
  decoder_check_empty kvs,
  return $ lean_server_request.exit msg
| j := exceptional.fail $ "Unexpected form for " ++ "lean_server_request" ++ ", found: " ++ (to_string j)

meta instance lean_server_request_has_from_json : has_from_json lean_server_request := 
⟨decode_json_lean_server_request⟩


meta instance lean_tactic_result_has_to_json : has_to_json lean_tactic_result := 
has_to_json.mk $ λ s, match s with
| (lean_tactic_result.success basic_goal_information) := json.jobject [("success", json.jobject [("basic_goal_information", to_json basic_goal_information)])]
| (lean_tactic_result.failure msg) := json.jobject [("failure", json.jobject [("msg", to_json msg)])]
| (lean_tactic_result.server_error msg) := json.jobject [("server_error", json.jobject [("msg", to_json msg)])]
end

private meta def decode_json_lean_tactic_result : json → exceptional lean_tactic_result
| (json.jobject [("success", json.jobject kvs)]) := do
  (basic_goal_information, kvs) <- decoder_get_field_value string "basic_goal_information" kvs,
  decoder_check_empty kvs,
  return $ lean_tactic_result.success basic_goal_information
| (json.jobject [("failure", json.jobject kvs)]) := do
  (msg, kvs) <- decoder_get_field_value string "msg" kvs,
  decoder_check_empty kvs,
  return $ lean_tactic_result.failure msg
| (json.jobject [("server_error", json.jobject kvs)]) := do
  (msg, kvs) <- decoder_get_field_value string "msg" kvs,
  decoder_check_empty kvs,
  return $ lean_tactic_result.server_error msg
| j := exceptional.fail $ "Unexpected form for " ++ "lean_tactic_result" ++ ", found: " ++ (to_string j)

meta instance lean_tactic_result_has_from_json : has_from_json lean_tactic_result := 
⟨decode_json_lean_tactic_result⟩


meta instance lean_state_result_has_to_json : has_to_json lean_state_result := 
has_to_json.mk $ λ s, match s with
| (lean_state_result.success basic_state_information) := json.jobject [("success", json.jobject [("basic_state_information", to_json basic_state_information)])]
| (lean_state_result.server_error msg) := json.jobject [("server_error", json.jobject [("msg", to_json msg)])]
end

private meta def decode_json_lean_state_result : json → exceptional lean_state_result
| (json.jobject [("success", json.jobject kvs)]) := do
  (basic_state_information, kvs) <- decoder_get_field_value string "basic_state_information" kvs,
  decoder_check_empty kvs,
  return $ lean_state_result.success basic_state_information
| (json.jobject [("server_error", json.jobject kvs)]) := do
  (msg, kvs) <- decoder_get_field_value string "msg" kvs,
  decoder_check_empty kvs,
  return $ lean_state_result.server_error msg
| j := exceptional.fail $ "Unexpected form for " ++ "lean_state_result" ++ ", found: " ++ (to_string j)

meta instance lean_state_result_has_from_json : has_from_json lean_state_result := 
⟨decode_json_lean_state_result⟩


meta instance lean_server_response_has_to_json : has_to_json lean_server_response := 
has_to_json.mk $ λ s, match s with
| (lean_server_response.apply_tactic result) := json.jobject [("apply_tactic", json.jobject [("result", to_json result)])]
| (lean_server_response.change_state result) := json.jobject [("change_state", json.jobject [("result", to_json result)])]
| (lean_server_response.exit msg) := json.jobject [("exit", json.jobject [("msg", to_json msg)])]
| (lean_server_response.error msg) := json.jobject [("error", json.jobject [("msg", to_json msg)])]
end

private meta def decode_json_lean_server_response : json → exceptional lean_server_response
| (json.jobject [("apply_tactic", json.jobject kvs)]) := do
  (result, kvs) <- decoder_get_field_value lean_tactic_result "result" kvs,
  decoder_check_empty kvs,
  return $ lean_server_response.apply_tactic result
| (json.jobject [("change_state", json.jobject kvs)]) := do
  (result, kvs) <- decoder_get_field_value lean_state_result "result" kvs,
  decoder_check_empty kvs,
  return $ lean_server_response.change_state result
| (json.jobject [("exit", json.jobject kvs)]) := do
  (msg, kvs) <- decoder_get_field_value string "msg" kvs,
  decoder_check_empty kvs,
  return $ lean_server_response.exit msg
| (json.jobject [("error", json.jobject kvs)]) := do
  (msg, kvs) <- decoder_get_field_value string "msg" kvs,
  decoder_check_empty kvs,
  return $ lean_server_response.error msg
| j := exceptional.fail $ "Unexpected form for " ++ "lean_server_response" ++ ", found: " ++ (to_string j)

meta instance lean_server_response_has_from_json : has_from_json lean_server_response := 
⟨decode_json_lean_server_response⟩
