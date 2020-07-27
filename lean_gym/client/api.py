from typing import Generic, Any, TypeVar, List


class JSONHelper:
    @staticmethod
    def to_pre_json(x: Any):
        if isinstance(x, (int, bool, str, float)):
            return x
        if isinstance(x, list):
            return [JSONHelper.to_pre_json(y) for y in x]
        return x.to_dict()


A = TypeVar('A')


class Option(Generic[A]):
    @staticmethod
    def none() -> "Option[A]":
        return NoneOption()

    @staticmethod
    def some(a: A) -> "Option[A]":
        return SomeOption(a)

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> "Option[A]":
        """Build LeanTactic from dictionary which was deserialized from JSON"""
        if "none" in d:
            return NoneOption.from_dict(d)
        if "some" in d:
            return SomeOption.from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class NoneOption(Option[A]):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"none": {}}

    @staticmethod
    def from_dict(d: dict) -> "NoneOption[A]":
        """Build SkipLeanTactic from dictionary which was deserialized from JSON"""
        return NoneOption()

    def __repr__(self):
        return "NoneOption(" + ")"


class SomeOption(Option[A]):
    def __init__(self, val: A):
        self.val = val
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"apply": {"sexp": JSONHelper.to_pre_json(self.val)}}

    @staticmethod
    def from_dict(d: dict) -> "SomeOption[A]":
        """Build ApplyLeanTactic from dictionary which was deserialized from JSON"""
        return SomeOption(d["some"]["val"])

    def __repr__(self):
        return "SomeOption(" + "val = " + repr(self.val) + ")"


class LeanTactic:
    """Tactic grammer"""
    @staticmethod
    def skip() -> "SkipLeanTactic":
        return SkipLeanTactic()

    @staticmethod
    def apply(sexp: str) -> "ApplyLeanTactic":
        return ApplyLeanTactic(sexp)

    @staticmethod
    def cases(sexp: str) -> "CasesLeanTactic":
        return CasesLeanTactic(sexp)

    @staticmethod
    def intro() -> "IntroLeanTactic":
        return IntroLeanTactic()

    @staticmethod
    def split() -> "SplitLeanTactic":
        return SplitLeanTactic()

    @staticmethod
    def left() -> "LeftLeanTactic":
        return LeftLeanTactic()

    @staticmethod
    def right() -> "RightLeanTactic":
        return RightLeanTactic()

    @staticmethod
    def exfalso() -> "ExfalsoLeanTactic":
        return ExfalsoLeanTactic()

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> "LeanTactic":
        """Build LeanTactic from dictionary which was deserialized from JSON"""
        if "skip" in d:
            return SkipLeanTactic.from_dict(d)
        if "apply" in d:
            return ApplyLeanTactic.from_dict(d)
        if "cases" in d:
            return CasesLeanTactic.from_dict(d)
        if "intro" in d:
            return IntroLeanTactic.from_dict(d)
        if "split" in d:
            return SplitLeanTactic.from_dict(d)
        if "left" in d:
            return LeftLeanTactic.from_dict(d)
        if "right" in d:
            return RightLeanTactic.from_dict(d)
        if "exfalso" in d:
            return ExfalsoLeanTactic.from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class SkipLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"skip": {}}

    @staticmethod
    def from_dict(d: dict) -> "SkipLeanTactic":
        """Build SkipLeanTactic from dictionary which was deserialized from JSON"""
        return SkipLeanTactic()

    def __repr__(self):
        return "SkipLeanTactic(" + ")"


class ApplyLeanTactic(LeanTactic):
    def __init__(self, sexp: str):
        self.sexp = sexp
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"apply": {"sexp": self.sexp}}

    @staticmethod
    def from_dict(d: dict) -> "ApplyLeanTactic":
        """Build ApplyLeanTactic from dictionary which was deserialized from JSON"""
        return ApplyLeanTactic(d["apply"]["sexp"])

    def __repr__(self):
        return "ApplyLeanTactic(" + "sexp = " + repr(self.sexp) + ")"


class CasesLeanTactic(LeanTactic):
    def __init__(self, sexp: str):
        self.sexp = sexp
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"cases": {"sexp": self.sexp}}

    @staticmethod
    def from_dict(d: dict) -> "CasesLeanTactic":
        """Build CasesLeanTactic from dictionary which was deserialized from JSON"""
        return CasesLeanTactic(d["cases"]["sexp"])

    def __repr__(self):
        return "CasesLeanTactic(" + "sexp = " + repr(self.sexp) + ")"


class IntroLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"intro": {}}

    @staticmethod
    def from_dict(d: dict) -> "IntroLeanTactic":
        """Build IntroLeanTactic from dictionary which was deserialized from JSON"""
        return IntroLeanTactic()

    def __repr__(self):
        return "IntroLeanTactic(" + ")"


class SplitLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"split": {}}

    @staticmethod
    def from_dict(d: dict) -> "SplitLeanTactic":
        """Build SplitLeanTactic from dictionary which was deserialized from JSON"""
        return SplitLeanTactic()

    def __repr__(self):
        return "SplitLeanTactic(" + ")"


class LeftLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"left": {}}

    @staticmethod
    def from_dict(d: dict) -> "LeftLeanTactic":
        """Build LeftLeanTactic from dictionary which was deserialized from JSON"""
        return LeftLeanTactic()

    def __repr__(self):
        return "LeftLeanTactic(" + ")"


class RightLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"right": {}}

    @staticmethod
    def from_dict(d: dict) -> "RightLeanTactic":
        """Build RightLeanTactic from dictionary which was deserialized from JSON"""
        return RightLeanTactic()

    def __repr__(self):
        return "RightLeanTactic(" + ")"


class ExfalsoLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"exfalso": {}}

    @staticmethod
    def from_dict(d: dict) -> "ExfalsoLeanTactic":
        """Build ExfalsoLeanTactic from dictionary which was deserialized from JSON"""
        return ExfalsoLeanTactic()

    def __repr__(self):
        return "ExfalsoLeanTactic(" + ")"


class LeanGoal:
    """Specify a top-level lean goal"""
    @staticmethod
    def target_sexp(sexp: str) -> "TargetSexpLeanGoal":
        return TargetSexpLeanGoal(sexp)

    @staticmethod
    def target_pp(ppexpr: str) -> "TargetPpLeanGoal":
        return TargetPpLeanGoal(ppexpr)

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> "LeanGoal":
        """Build LeanGoal from dictionary which was deserialized from JSON"""
        if "target_sexp" in d:
            return TargetSexpLeanGoal.from_dict(d)
        if "target_pp" in d:
            return TargetPpLeanGoal.from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class TargetSexpLeanGoal(LeanGoal):
    """Goal target given as an s-expression"""
    def __init__(self, sexp: str):
        self.sexp = sexp
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"target_sexp": {"sexp": self.sexp}}

    @staticmethod
    def from_dict(d: dict) -> "TargetSexpLeanGoal":
        """Build TargetSexpLeanGoal from dictionary which was deserialized from JSON"""
        return TargetSexpLeanGoal(d["target_sexp"]["sexp"])

    def __repr__(self):
        return "TargetSexpLeanGoal(" + "sexp = " + repr(self.sexp) + ")"


class TargetPpLeanGoal(LeanGoal):
    """Goal target given as a pretty-printed lean code string, e.g. "∀ p : Prop, p → p". Only available in certain run configurations since it requires access to the Lean parser."""
    def __init__(self, ppexpr: str):
        self.ppexpr = ppexpr
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"target_pp": {"ppexpr": self.ppexpr}}

    @staticmethod
    def from_dict(d: dict) -> "TargetPpLeanGoal":
        """Build TargetPpLeanGoal from dictionary which was deserialized from JSON"""
        return TargetPpLeanGoal(d["target_pp"]["ppexpr"])

    def __repr__(self):
        return "TargetPpLeanGoal(" + "ppexpr = " + repr(self.ppexpr) + ")"


class TacticFocus:
    @staticmethod
    def default() -> "DefaultTacticFocus":
        return DefaultTacticFocus()

    @staticmethod
    def focus1() -> "Focus1TacticFocus":
        return Focus1TacticFocus()

    @staticmethod
    def all_goals() -> "AllGoalsTacticFocus":
        return AllGoalsTacticFocus()

    @staticmethod
    def any_goals() -> "AnyGoalsTacticFocus":
        return AnyGoalsTacticFocus()

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> "TacticFocus":
        """Build TacticFocus from dictionary which was deserialized from JSON"""
        if "default" in d:
            return DefaultTacticFocus.from_dict(d)
        if "focus1" in d:
            return Focus1TacticFocus.from_dict(d)
        if "all_goals" in d:
            return AllGoalsTacticFocus.from_dict(d)
        if "any_goals" in d:
            return AnyGoalsTacticFocus.from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class DefaultTacticFocus(TacticFocus):
    """Apply Lean's default focus for that tactic.  Many tactics only apply to the first goal, but some try to change all the goals."""
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"default": {}}

    @staticmethod
    def from_dict(d: dict) -> "DefaultTacticFocus":
        """Build DefaultTacticFocus from dictionary which was deserialized from JSON"""
        return DefaultTacticFocus()

    def __repr__(self):
        return "DefaultTacticFocus(" + ")"


class Focus1TacticFocus(TacticFocus):
    """Focus on the first goal only. For many theorem proving gyms, this is the right approach. It mimicks Lean's `focus` tactic combinator."""
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"focus1": {}}

    @staticmethod
    def from_dict(d: dict) -> "Focus1TacticFocus":
        """Build Focus1TacticFocus from dictionary which was deserialized from JSON"""
        return Focus1TacticFocus()

    def __repr__(self):
        return "Focus1TacticFocus(" + ")"


class AllGoalsTacticFocus(TacticFocus):
    """Apply the tactic to all goals and fail if any goal fails. This is for advanced use. It mimicks Lean's `all_goals` tactic combinator."""
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"all_goals": {}}

    @staticmethod
    def from_dict(d: dict) -> "AllGoalsTacticFocus":
        """Build AllGoalsTacticFocus from dictionary which was deserialized from JSON"""
        return AllGoalsTacticFocus()

    def __repr__(self):
        return "AllGoalsTacticFocus(" + ")"


class AnyGoalsTacticFocus(TacticFocus):
    """Apply the tactic to all goals and succeed if at least one goal changes. This is for advanced use.  It mimicks Lean's `any_goals` tactic combinator."""
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"any_goals": {}}

    @staticmethod
    def from_dict(d: dict) -> "AnyGoalsTacticFocus":
        """Build AnyGoalsTacticFocus from dictionary which was deserialized from JSON"""
        return AnyGoalsTacticFocus()

    def __repr__(self):
        return "AnyGoalsTacticFocus(" + ")"


class LocalInfoConfig:
    def __init__(self, local_var_hash: bool, local_var_name: bool, local_var_sexp: bool, local_type_hash: bool, local_type_pp: bool, local_type_pp_all: bool, local_type_sexp: bool):
        self.local_var_hash = local_var_hash
        self.local_var_name = local_var_name
        self.local_var_sexp = local_var_sexp
        self.local_type_hash = local_type_hash
        self.local_type_pp = local_type_pp
        self.local_type_pp_all = local_type_pp_all
        self.local_type_sexp = local_type_sexp
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"local_info_config": {"local_var_hash": self.local_var_hash, "local_var_name": self.local_var_name, "local_var_sexp": self.local_var_sexp, "local_type_hash": self.local_type_hash, "local_type_pp": self.local_type_pp, "local_type_pp_all": self.local_type_pp_all, "local_type_sexp": self.local_type_sexp}}

    @staticmethod
    def from_dict(d: dict) -> "LocalInfoConfig":
        """Build LocalInfoConfig from dictionary which was deserialized from JSON"""
        return LocalInfoConfig(d["local_info_config"]["local_var_hash"], d["local_info_config"]["local_var_name"], d["local_info_config"]["local_var_sexp"], d["local_info_config"]["local_type_hash"], d["local_info_config"]["local_type_pp"], d["local_info_config"]["local_type_pp_all"], d["local_info_config"]["local_type_sexp"])

    def __repr__(self):
        return "LocalInfoConfig(" + "local_var_hash = " + repr(self.local_var_hash) + ", " + "local_var_name = " + repr(self.local_var_name) + ", " + "local_var_sexp = " + repr(self.local_var_sexp) + ", " + "local_type_hash = " + repr(self.local_type_hash) + ", " + "local_type_pp = " + repr(self.local_type_pp) + ", " + "local_type_pp_all = " + repr(self.local_type_pp_all) + ", " + "local_type_sexp = " + repr(self.local_type_sexp) + ")"


class GoalInfoConfig:
    def __init__(self, target_hash: bool, target_pp: bool, target_pp_all: bool, target_sexp: bool, local_cnt: bool, locals: Option[LocalInfoConfig]):
        self.target_hash = target_hash
        self.target_pp = target_pp
        self.target_pp_all = target_pp_all
        self.target_sexp = target_sexp
        self.local_cnt = local_cnt
        self.locals = locals
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"goal_info_config": {"target_hash": self.target_hash, "target_pp": self.target_pp, "target_pp_all": self.target_pp_all, "target_sexp": self.target_sexp, "local_cnt": self.local_cnt, "locals": self.locals.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "GoalInfoConfig":
        """Build GoalInfoConfig from dictionary which was deserialized from JSON"""
        return GoalInfoConfig(d["goal_info_config"]["target_hash"], d["goal_info_config"]["target_pp"], d["goal_info_config"]["target_pp_all"], d["goal_info_config"]["target_sexp"], d["goal_info_config"]["local_cnt"], Option.from_dict(d["goal_info_config"]["locals"]))

    def __repr__(self):
        return "GoalInfoConfig(" + "target_hash = " + repr(self.target_hash) + ", " + "target_pp = " + repr(self.target_pp) + ", " + "target_pp_all = " + repr(self.target_pp_all) + ", " + "target_sexp = " + repr(self.target_sexp) + ", " + "local_cnt = " + repr(self.local_cnt) + ", " + "locals = " + repr(self.locals) + ")"


class StateInfoConfig:
    def __init__(self, proof_path_ixs: bool, proof_string: bool, state_pp: bool, state_pp_all: bool, goal_cnt: bool, goals: Option[GoalInfoConfig]):
        self.proof_path_ixs = proof_path_ixs
        self.proof_string = proof_string
        self.state_pp = state_pp
        self.state_pp_all = state_pp_all
        self.goal_cnt = goal_cnt
        self.goals = goals
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"state_info_config": {"proof_path_ixs": self.proof_path_ixs, "proof_string": self.proof_string, "state_pp": self.state_pp, "state_pp_all": self.state_pp_all, "goal_cnt": self.goal_cnt, "goals": self.goals.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "StateInfoConfig":
        """Build StateInfoConfig from dictionary which was deserialized from JSON"""
        return StateInfoConfig(d["state_info_config"]["proof_path_ixs"], d["state_info_config"]["proof_string"], d["state_info_config"]["state_pp"], d["state_info_config"]["state_pp_all"], d["state_info_config"]["goal_cnt"], Option.from_dict(d["state_info_config"]["goals"]))

    def __repr__(self):
        return "StateInfoConfig(" + "proof_path_ixs = " + repr(self.proof_path_ixs) + ", " + "proof_string = " + repr(self.proof_string) + ", " + "state_pp = " + repr(self.state_pp) + ", " + "state_pp_all = " + repr(self.state_pp_all) + ", " + "goal_cnt = " + repr(self.goal_cnt) + ", " + "goals = " + repr(self.goals) + ")"


class LeanServerRequest:
    """Request to the server"""
    @staticmethod
    def execute_tactic(state_ix: int, focus: TacticFocus, tactic: LeanTactic, cfg: StateInfoConfig) -> "ExecuteTacticLeanServerRequest":
        return ExecuteTacticLeanServerRequest(state_ix, focus, tactic, cfg)

    @staticmethod
    def change_goal(goal: LeanGoal, cfg: StateInfoConfig) -> "ChangeGoalLeanServerRequest":
        return ChangeGoalLeanServerRequest(goal, cfg)

    @staticmethod
    def get_state_info(state_ix: int, cfg: StateInfoConfig) -> "GetStateInfoLeanServerRequest":
        return GetStateInfoLeanServerRequest(state_ix, cfg)

    @staticmethod
    def exit(msg: Option[str], state_ix: Option[int]) -> "ExitLeanServerRequest":
        return ExitLeanServerRequest(msg, state_ix)

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> "LeanServerRequest":
        """Build LeanServerRequest from dictionary which was deserialized from JSON"""
        if "execute_tactic" in d:
            return ExecuteTacticLeanServerRequest.from_dict(d)
        if "change_goal" in d:
            return ChangeGoalLeanServerRequest.from_dict(d)
        if "get_state_info" in d:
            return GetStateInfoLeanServerRequest.from_dict(d)
        if "exit" in d:
            return ExitLeanServerRequest.from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class ExecuteTacticLeanServerRequest(LeanServerRequest):
    """Apply a tactic to a tactic state and return information about the new state."""
    def __init__(self, state_ix: int, focus: TacticFocus, tactic: LeanTactic, cfg: StateInfoConfig):
        self.state_ix = state_ix
        assert state_ix >= 0
        self.focus = focus
        self.tactic = tactic
        self.cfg = cfg
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"execute_tactic": {"state_ix": self.state_ix, "focus": self.focus.to_dict(), "tactic": self.tactic.to_dict(), "cfg": self.cfg.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "ExecuteTacticLeanServerRequest":
        """Build ExecuteTacticLeanServerRequest from dictionary which was deserialized from JSON"""
        return ExecuteTacticLeanServerRequest(d["execute_tactic"]["state_ix"], TacticFocus.from_dict(d["execute_tactic"]["focus"]), LeanTactic.from_dict(d["execute_tactic"]["tactic"]), StateInfoConfig.from_dict(d["execute_tactic"]["cfg"]))

    def __repr__(self):
        return "ExecuteTacticLeanServerRequest(" + "state_ix = " + repr(self.state_ix) + ", " + "focus = " + repr(self.focus) + ", " + "tactic = " + repr(self.tactic) + ", " + "cfg = " + repr(self.cfg) + ")"


class ChangeGoalLeanServerRequest(LeanServerRequest):
    """Create a new goal, reset all the states, and return information about the new state."""
    def __init__(self, goal: LeanGoal, cfg: StateInfoConfig):
        self.goal = goal
        self.cfg = cfg
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"change_goal": {"goal": self.goal.to_dict(), "cfg": self.cfg.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "ChangeGoalLeanServerRequest":
        """Build ChangeGoalLeanServerRequest from dictionary which was deserialized from JSON"""
        return ChangeGoalLeanServerRequest(LeanGoal.from_dict(d["change_goal"]["goal"]), StateInfoConfig.from_dict(d["change_goal"]["cfg"]))

    def __repr__(self):
        return "ChangeGoalLeanServerRequest(" + "goal = " + repr(self.goal) + ", " + "cfg = " + repr(self.cfg) + ")"


class GetStateInfoLeanServerRequest(LeanServerRequest):
    """Return information about the new state."""
    def __init__(self, state_ix: int, cfg: StateInfoConfig):
        self.state_ix = state_ix
        assert state_ix >= 0
        self.cfg = cfg
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"get_state_info": {"state_ix": self.state_ix, "cfg": self.cfg.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "GetStateInfoLeanServerRequest":
        """Build GetStateInfoLeanServerRequest from dictionary which was deserialized from JSON"""
        return GetStateInfoLeanServerRequest(d["get_state_info"]["state_ix"], StateInfoConfig.from_dict(d["get_state_info"]["cfg"]))

    def __repr__(self):
        return "GetStateInfoLeanServerRequest(" + "state_ix = " + repr(self.state_ix) + ", " + "cfg = " + repr(self.cfg) + ")"


class ExitLeanServerRequest(LeanServerRequest):
    """Exit the interface.  The message is mention and state will be passed to a lean tactic.  If run inside an interactive tactic, the state_ix can be used to set what the state is after the tactic is run.  The message can be traced to the user.  Pro tip: Any message with one or more lines of the form "Try it: <proof>" will be suggested for the user."""
    def __init__(self, msg: Option[str], state_ix: Option[int]):
        self.msg = msg
        self.state_ix = state_ix
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"exit": {"msg": self.msg.to_dict(), "state_ix": self.state_ix.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "ExitLeanServerRequest":
        """Build ExitLeanServerRequest from dictionary which was deserialized from JSON"""
        return ExitLeanServerRequest(Option.from_dict(d["exit"]["msg"]), Option.from_dict(d["exit"]["state_ix"]))

    def __repr__(self):
        return "ExitLeanServerRequest(" + "msg = " + repr(self.msg) + ", " + "state_ix = " + repr(self.state_ix) + ")"


class LocalReport:
    def __init__(self, local_var_hash: Option[int], local_var_name: Option[str], local_var_sexp: Option[str], local_type_hash: Option[int], local_type_pp: Option[str], local_type_pp_all: Option[str], local_type_sexp: Option[str]):
        self.local_var_hash = local_var_hash
        self.local_var_name = local_var_name
        self.local_var_sexp = local_var_sexp
        self.local_type_hash = local_type_hash
        self.local_type_pp = local_type_pp
        self.local_type_pp_all = local_type_pp_all
        self.local_type_sexp = local_type_sexp
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"local_report": {"local_var_hash": self.local_var_hash.to_dict(), "local_var_name": self.local_var_name.to_dict(), "local_var_sexp": self.local_var_sexp.to_dict(), "local_type_hash": self.local_type_hash.to_dict(), "local_type_pp": self.local_type_pp.to_dict(), "local_type_pp_all": self.local_type_pp_all.to_dict(), "local_type_sexp": self.local_type_sexp.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "LocalReport":
        """Build LocalReport from dictionary which was deserialized from JSON"""
        return LocalReport(Option.from_dict(d["local_report"]["local_var_hash"]), Option.from_dict(d["local_report"]["local_var_name"]), Option.from_dict(d["local_report"]["local_var_sexp"]), Option.from_dict(d["local_report"]["local_type_hash"]), Option.from_dict(d["local_report"]["local_type_pp"]), Option.from_dict(d["local_report"]["local_type_pp_all"]), Option.from_dict(d["local_report"]["local_type_sexp"]))

    def __repr__(self):
        return "LocalReport(" + "local_var_hash = " + repr(self.local_var_hash) + ", " + "local_var_name = " + repr(self.local_var_name) + ", " + "local_var_sexp = " + repr(self.local_var_sexp) + ", " + "local_type_hash = " + repr(self.local_type_hash) + ", " + "local_type_pp = " + repr(self.local_type_pp) + ", " + "local_type_pp_all = " + repr(self.local_type_pp_all) + ", " + "local_type_sexp = " + repr(self.local_type_sexp) + ")"


class GoalReport:
    def __init__(self, target_hash: Option[int], target_pp: Option[str], target_pp_all: Option[str], target_sexp: Option[str], local_cnt: Option[int], locals: Option[List[LocalReport]]):
        self.target_hash = target_hash
        self.target_pp = target_pp
        self.target_pp_all = target_pp_all
        self.target_sexp = target_sexp
        self.local_cnt = local_cnt
        self.locals = locals
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"goal_report": {"target_hash": self.target_hash.to_dict(), "target_pp": self.target_pp.to_dict(), "target_pp_all": self.target_pp_all.to_dict(), "target_sexp": self.target_sexp.to_dict(), "local_cnt": self.local_cnt.to_dict(), "locals": self.locals.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "GoalReport":
        """Build GoalReport from dictionary which was deserialized from JSON"""
        return GoalReport(Option.from_dict(d["goal_report"]["target_hash"]), Option.from_dict(d["goal_report"]["target_pp"]), Option.from_dict(d["goal_report"]["target_pp_all"]), Option.from_dict(d["goal_report"]["target_sexp"]), Option.from_dict(d["goal_report"]["local_cnt"]), Option.from_dict(d["goal_report"]["locals"]))

    def __repr__(self):
        return "GoalReport(" + "target_hash = " + repr(self.target_hash) + ", " + "target_pp = " + repr(self.target_pp) + ", " + "target_pp_all = " + repr(self.target_pp_all) + ", " + "target_sexp = " + repr(self.target_sexp) + ", " + "local_cnt = " + repr(self.local_cnt) + ", " + "locals = " + repr(self.locals) + ")"


class StateReport:
    def __init__(self, is_solved: bool, proof_path_ixs: Option[List[int]], proof_string: Option[str], state_pp: Option[str], state_pp_all: Option[str], goal_cnt: Option[int], goals: Option[List[GoalReport]]):
        self.is_solved = is_solved
        self.proof_path_ixs = proof_path_ixs
        self.proof_string = proof_string
        self.state_pp = state_pp
        self.state_pp_all = state_pp_all
        self.goal_cnt = goal_cnt
        self.goals = goals
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"state_report": {"is_solved": self.is_solved, "proof_path_ixs": self.proof_path_ixs.to_dict(), "proof_string": self.proof_string.to_dict(), "state_pp": self.state_pp.to_dict(), "state_pp_all": self.state_pp_all.to_dict(), "goal_cnt": self.goal_cnt.to_dict(), "goals": self.goals.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "StateReport":
        """Build StateReport from dictionary which was deserialized from JSON"""
        return StateReport(d["state_report"]["is_solved"], Option.from_dict(d["state_report"]["proof_path_ixs"]), Option.from_dict(d["state_report"]["proof_string"]), Option.from_dict(d["state_report"]["state_pp"]), Option.from_dict(d["state_report"]["state_pp_all"]), Option.from_dict(d["state_report"]["goal_cnt"]), Option.from_dict(d["state_report"]["goals"]))

    def __repr__(self):
        return "StateReport(" + "is_solved = " + repr(self.is_solved) + ", " + "proof_path_ixs = " + repr(self.proof_path_ixs) + ", " + "proof_string = " + repr(self.proof_string) + ", " + "state_pp = " + repr(self.state_pp) + ", " + "state_pp_all = " + repr(self.state_pp_all) + ", " + "goal_cnt = " + repr(self.goal_cnt) + ", " + "goals = " + repr(self.goals) + ")"


class LeanTacticResult:
    @staticmethod
    def success(tactic_ix: int, state_info: StateReport) -> "SuccessLeanTacticResult":
        return SuccessLeanTacticResult(tactic_ix, state_info)

    @staticmethod
    def failure(msg: str) -> "FailureLeanTacticResult":
        return FailureLeanTacticResult(msg)

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> "LeanTacticResult":
        """Build LeanTacticResult from dictionary which was deserialized from JSON"""
        if "success" in d:
            return SuccessLeanTacticResult.from_dict(d)
        if "failure" in d:
            return FailureLeanTacticResult.from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class SuccessLeanTacticResult(LeanTacticResult):
    def __init__(self, tactic_ix: int, state_info: StateReport):
        self.tactic_ix = tactic_ix
        assert tactic_ix >= 0
        self.state_info = state_info
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"success": {"tactic_ix": self.tactic_ix, "state_info": self.state_info.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "SuccessLeanTacticResult":
        """Build SuccessLeanTacticResult from dictionary which was deserialized from JSON"""
        return SuccessLeanTacticResult(d["success"]["tactic_ix"], StateReport.from_dict(d["success"]["state_info"]))

    def __repr__(self):
        return "SuccessLeanTacticResult(" + "tactic_ix = " + repr(self.tactic_ix) + ", " + "state_info = " + repr(self.state_info) + ")"


class FailureLeanTacticResult(LeanTacticResult):
    def __init__(self, msg: str):
        self.msg = msg
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"failure": {"msg": self.msg}}

    @staticmethod
    def from_dict(d: dict) -> "FailureLeanTacticResult":
        """Build FailureLeanTacticResult from dictionary which was deserialized from JSON"""
        return FailureLeanTacticResult(d["failure"]["msg"])

    def __repr__(self):
        return "FailureLeanTacticResult(" + "msg = " + repr(self.msg) + ")"


class LeanServerResponse:
    @staticmethod
    def execute_tactic(tactic_result: LeanTacticResult) -> "ExecuteTacticLeanServerResponse":
        return ExecuteTacticLeanServerResponse(tactic_result)

    @staticmethod
    def change_goal(state_info: StateReport) -> "ChangeGoalLeanServerResponse":
        return ChangeGoalLeanServerResponse(state_info)

    @staticmethod
    def get_state_info(state_info: StateReport) -> "GetStateInfoLeanServerResponse":
        return GetStateInfoLeanServerResponse(state_info)

    @staticmethod
    def exit(msg: Option[str], state_ix: Option[int]) -> "ExitLeanServerResponse":
        return ExitLeanServerResponse(msg, state_ix)

    @staticmethod
    def error(msg: str) -> "ErrorLeanServerResponse":
        return ErrorLeanServerResponse(msg)

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> "LeanServerResponse":
        """Build LeanServerResponse from dictionary which was deserialized from JSON"""
        if "execute_tactic" in d:
            return ExecuteTacticLeanServerResponse.from_dict(d)
        if "change_goal" in d:
            return ChangeGoalLeanServerResponse.from_dict(d)
        if "get_state_info" in d:
            return GetStateInfoLeanServerResponse.from_dict(d)
        if "exit" in d:
            return ExitLeanServerResponse.from_dict(d)
        if "error" in d:
            return ErrorLeanServerResponse.from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class ExecuteTacticLeanServerResponse(LeanServerResponse):
    def __init__(self, tactic_result: LeanTacticResult):
        self.tactic_result = tactic_result
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"execute_tactic": {"tactic_result": self.tactic_result.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "ExecuteTacticLeanServerResponse":
        """Build ExecuteTacticLeanServerResponse from dictionary which was deserialized from JSON"""
        return ExecuteTacticLeanServerResponse(LeanTacticResult.from_dict(d["execute_tactic"]["tactic_result"]))

    def __repr__(self):
        return "ExecuteTacticLeanServerResponse(" + "tactic_result = " + repr(self.tactic_result) + ")"


class ChangeGoalLeanServerResponse(LeanServerResponse):
    def __init__(self, state_info: StateReport):
        self.state_info = state_info
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"change_goal": {"state_info": self.state_info.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "ChangeGoalLeanServerResponse":
        """Build ChangeGoalLeanServerResponse from dictionary which was deserialized from JSON"""
        return ChangeGoalLeanServerResponse(StateReport.from_dict(d["change_goal"]["state_info"]))

    def __repr__(self):
        return "ChangeGoalLeanServerResponse(" + "state_info = " + repr(self.state_info) + ")"


class GetStateInfoLeanServerResponse(LeanServerResponse):
    def __init__(self, state_info: StateReport):
        self.state_info = state_info
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"get_state_info": {"state_info": self.state_info.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "GetStateInfoLeanServerResponse":
        """Build GetStateInfoLeanServerResponse from dictionary which was deserialized from JSON"""
        return GetStateInfoLeanServerResponse(StateReport.from_dict(d["get_state_info"]["state_info"]))

    def __repr__(self):
        return "GetStateInfoLeanServerResponse(" + "state_info = " + repr(self.state_info) + ")"


class ExitLeanServerResponse(LeanServerResponse):
    def __init__(self, msg: Option[str], state_ix: Option[int]):
        self.msg = msg
        self.state_ix = state_ix
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"exit": {"msg": self.msg.to_dict(), "state_ix": self.state_ix.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> "ExitLeanServerResponse":
        """Build ExitLeanServerResponse from dictionary which was deserialized from JSON"""
        return ExitLeanServerResponse(Option.from_dict(d["exit"]["msg"]), Option.from_dict(d["exit"]["state_ix"]))

    def __repr__(self):
        return "ExitLeanServerResponse(" + "msg = " + repr(self.msg) + ", " + "state_ix = " + repr(self.state_ix) + ")"


class ErrorLeanServerResponse(LeanServerResponse):
    def __init__(self, msg: str):
        self.msg = msg
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {"error": {"msg": self.msg}}

    @staticmethod
    def from_dict(d: dict) -> "ErrorLeanServerResponse":
        """Build ErrorLeanServerResponse from dictionary which was deserialized from JSON"""
        return ErrorLeanServerResponse(d["error"]["msg"])

    def __repr__(self):
        return "ErrorLeanServerResponse(" + "msg = " + repr(self.msg) + ")"
