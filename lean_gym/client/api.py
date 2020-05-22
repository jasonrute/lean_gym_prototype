class LeanTactic:
    """Tactic grammer"""

    @staticmethod
    def skip() -> 'SkipLeanTactic':
        return SkipLeanTactic()

    @staticmethod
    def apply(sexp: str) -> 'ApplyLeanTactic':
        return ApplyLeanTactic(sexp)

    @staticmethod
    def cases(sexp: str) -> 'CasesLeanTactic':
        return CasesLeanTactic(sexp)

    @staticmethod
    def intro() -> 'IntroLeanTactic':
        return IntroLeanTactic()

    @staticmethod
    def split() -> 'SplitLeanTactic':
        return SplitLeanTactic()

    @staticmethod
    def left() -> 'LeftLeanTactic':
        return LeftLeanTactic()

    @staticmethod
    def right() -> 'RightLeanTactic':
        return RightLeanTactic()

    @staticmethod
    def exfalso() -> 'ExfalsoLeanTactic':
        return ExfalsoLeanTactic()

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> 'LeanTactic':
        """Build LeanTactic from dictionary which was deserialized from JSON"""
        if 'skip' in d:
            return SkipLeanTactic.from_dict(d)
        if 'apply' in d:
            return ApplyLeanTactic.from_dict(d)
        if 'cases' in d:
            return CasesLeanTactic.from_dict(d)
        if 'intro' in d:
            return IntroLeanTactic.from_dict(d)
        if 'split' in d:
            return SplitLeanTactic.from_dict(d)
        if 'left' in d:
            return LeftLeanTactic.from_dict(d)
        if 'right' in d:
            return RightLeanTactic.from_dict(d)
        if 'exfalso' in d:
            return ExfalsoLeanTactic.from_dict(d)

        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class SkipLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'skip': {}}

    @staticmethod
    def from_dict(d: dict) -> 'SkipLeanTactic':
        """Build SkipLeanTactic from dictionary which was deserialized from JSON"""
        return SkipLeanTactic()

    def __repr__(self):
        return 'SkipLeanTactic(' + ')'


class ApplyLeanTactic(LeanTactic):
    def __init__(self, sexp: str):
        self.sexp = sexp
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'apply': {'sexp': self.sexp}}

    @staticmethod
    def from_dict(d: dict) -> 'ApplyLeanTactic':
        """Build ApplyLeanTactic from dictionary which was deserialized from JSON"""
        return ApplyLeanTactic(d['apply']['sexp'])

    def __repr__(self):
        return 'ApplyLeanTactic(' + 'sexp = ' + repr(self.sexp) + ')'


class CasesLeanTactic(LeanTactic):
    def __init__(self, sexp: str):
        self.sexp = sexp
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'cases': {'sexp': self.sexp}}

    @staticmethod
    def from_dict(d: dict) -> 'CasesLeanTactic':
        """Build CasesLeanTactic from dictionary which was deserialized from JSON"""
        return CasesLeanTactic(d['cases']['sexp'])

    def __repr__(self):
        return 'CasesLeanTactic(' + 'sexp = ' + repr(self.sexp) + ')'


class IntroLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'intro': {}}

    @staticmethod
    def from_dict(d: dict) -> 'IntroLeanTactic':
        """Build IntroLeanTactic from dictionary which was deserialized from JSON"""
        return IntroLeanTactic()

    def __repr__(self):
        return 'IntroLeanTactic(' + ')'


class SplitLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'split': {}}

    @staticmethod
    def from_dict(d: dict) -> 'SplitLeanTactic':
        """Build SplitLeanTactic from dictionary which was deserialized from JSON"""
        return SplitLeanTactic()

    def __repr__(self):
        return 'SplitLeanTactic(' + ')'


class LeftLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'left': {}}

    @staticmethod
    def from_dict(d: dict) -> 'LeftLeanTactic':
        """Build LeftLeanTactic from dictionary which was deserialized from JSON"""
        return LeftLeanTactic()

    def __repr__(self):
        return 'LeftLeanTactic(' + ')'


class RightLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'right': {}}

    @staticmethod
    def from_dict(d: dict) -> 'RightLeanTactic':
        """Build RightLeanTactic from dictionary which was deserialized from JSON"""
        return RightLeanTactic()

    def __repr__(self):
        return 'RightLeanTactic(' + ')'


class ExfalsoLeanTactic(LeanTactic):
    def __init__(self, ):
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'exfalso': {}}

    @staticmethod
    def from_dict(d: dict) -> 'ExfalsoLeanTactic':
        """Build ExfalsoLeanTactic from dictionary which was deserialized from JSON"""
        return ExfalsoLeanTactic()

    def __repr__(self):
        return 'ExfalsoLeanTactic(' + ')'


class LeanStateControl:
    """Manually change the state"""

    @staticmethod
    def jump_to_state(state_index: int) -> 'JumpToStateLeanStateControl':
        return JumpToStateLeanStateControl(state_index)

    @staticmethod
    def change_top_goal(sexp: str) -> 'ChangeTopGoalLeanStateControl':
        return ChangeTopGoalLeanStateControl(sexp)

    @staticmethod
    def change_top_goal_pp(sexp: str) -> 'ChangeTopGoalPpLeanStateControl':
        return ChangeTopGoalPpLeanStateControl(sexp)

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> 'LeanStateControl':
        """Build LeanStateControl from dictionary which was deserialized from JSON"""
        if 'jump_to_state' in d:
            return JumpToStateLeanStateControl.from_dict(d)
        if 'change_top_goal' in d:
            return ChangeTopGoalLeanStateControl.from_dict(d)
        if 'change_top_goal_pp' in d:
            return ChangeTopGoalPpLeanStateControl.from_dict(d)

        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class JumpToStateLeanStateControl(LeanStateControl):
    def __init__(self, state_index: int):
        self.state_index = state_index
        assert state_index >= 0
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'jump_to_state': {'state_index': self.state_index}}

    @staticmethod
    def from_dict(d: dict) -> 'JumpToStateLeanStateControl':
        """Build JumpToStateLeanStateControl from dictionary which was deserialized from JSON"""
        return JumpToStateLeanStateControl(d['jump_to_state']['state_index'])

    def __repr__(self):
        return 'JumpToStateLeanStateControl(' + 'state_index = ' + repr(self.state_index) + ')'


class ChangeTopGoalLeanStateControl(LeanStateControl):
    def __init__(self, sexp: str):
        self.sexp = sexp
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'change_top_goal': {'sexp': self.sexp}}

    @staticmethod
    def from_dict(d: dict) -> 'ChangeTopGoalLeanStateControl':
        """Build ChangeTopGoalLeanStateControl from dictionary which was deserialized from JSON"""
        return ChangeTopGoalLeanStateControl(d['change_top_goal']['sexp'])

    def __repr__(self):
        return 'ChangeTopGoalLeanStateControl(' + 'sexp = ' + repr(self.sexp) + ')'


class ChangeTopGoalPpLeanStateControl(LeanStateControl):
    def __init__(self, sexp: str):
        self.sexp = sexp
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'change_top_goal_pp': {'sexp': self.sexp}}

    @staticmethod
    def from_dict(d: dict) -> 'ChangeTopGoalPpLeanStateControl':
        """Build ChangeTopGoalPpLeanStateControl from dictionary which was deserialized from JSON"""
        return ChangeTopGoalPpLeanStateControl(d['change_top_goal_pp']['sexp'])

    def __repr__(self):
        return 'ChangeTopGoalPpLeanStateControl(' + 'sexp = ' + repr(self.sexp) + ')'


class LeanServerRequest:
    """Request to the server"""

    @staticmethod
    def apply_tactic(tactic: LeanTactic) -> 'ApplyTacticLeanServerRequest':
        return ApplyTacticLeanServerRequest(tactic)

    @staticmethod
    def change_state(control: LeanStateControl) -> 'ChangeStateLeanServerRequest':
        return ChangeStateLeanServerRequest(control)

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> 'LeanServerRequest':
        """Build LeanServerRequest from dictionary which was deserialized from JSON"""
        if 'apply_tactic' in d:
            return ApplyTacticLeanServerRequest.from_dict(d)
        if 'change_state' in d:
            return ChangeStateLeanServerRequest.from_dict(d)

        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class ApplyTacticLeanServerRequest(LeanServerRequest):
    def __init__(self, tactic: LeanTactic):
        self.tactic = tactic
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'apply_tactic': {'tactic': self.tactic.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> 'ApplyTacticLeanServerRequest':
        """Build ApplyTacticLeanServerRequest from dictionary which was deserialized from JSON"""
        return ApplyTacticLeanServerRequest(LeanTactic.from_dict(d['apply_tactic']['tactic']))

    def __repr__(self):
        return 'ApplyTacticLeanServerRequest(' + 'tactic = ' + repr(self.tactic) + ')'


class ChangeStateLeanServerRequest(LeanServerRequest):
    def __init__(self, control: LeanStateControl):
        self.control = control
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'change_state': {'control': self.control.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> 'ChangeStateLeanServerRequest':
        """Build ChangeStateLeanServerRequest from dictionary which was deserialized from JSON"""
        return ChangeStateLeanServerRequest(LeanStateControl.from_dict(d['change_state']['control']))

    def __repr__(self):
        return 'ChangeStateLeanServerRequest(' + 'control = ' + repr(self.control) + ')'


class LeanTacticResult:

    @staticmethod
    def success(basic_goal_information: str) -> 'SuccessLeanTacticResult':
        return SuccessLeanTacticResult(basic_goal_information)

    @staticmethod
    def failure(msg: str) -> 'FailureLeanTacticResult':
        return FailureLeanTacticResult(msg)

    @staticmethod
    def server_error(msg: str) -> 'ServerErrorLeanTacticResult':
        return ServerErrorLeanTacticResult(msg)

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> 'LeanTacticResult':
        """Build LeanTacticResult from dictionary which was deserialized from JSON"""
        if 'success' in d:
            return SuccessLeanTacticResult.from_dict(d)
        if 'failure' in d:
            return FailureLeanTacticResult.from_dict(d)
        if 'server_error' in d:
            return ServerErrorLeanTacticResult.from_dict(d)

        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class SuccessLeanTacticResult(LeanTacticResult):
    def __init__(self, basic_goal_information: str):
        self.basic_goal_information = basic_goal_information
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'success': {'basic_goal_information': self.basic_goal_information}}

    @staticmethod
    def from_dict(d: dict) -> 'SuccessLeanTacticResult':
        """Build SuccessLeanTacticResult from dictionary which was deserialized from JSON"""
        return SuccessLeanTacticResult(d['success']['basic_goal_information'])

    def __repr__(self):
        return 'SuccessLeanTacticResult(' + 'basic_goal_information = ' + repr(self.basic_goal_information) + ')'


class FailureLeanTacticResult(LeanTacticResult):
    def __init__(self, msg: str):
        self.msg = msg
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'failure': {'msg': self.msg}}

    @staticmethod
    def from_dict(d: dict) -> 'FailureLeanTacticResult':
        """Build FailureLeanTacticResult from dictionary which was deserialized from JSON"""
        return FailureLeanTacticResult(d['failure']['msg'])

    def __repr__(self):
        return 'FailureLeanTacticResult(' + 'msg = ' + repr(self.msg) + ')'


class ServerErrorLeanTacticResult(LeanTacticResult):
    def __init__(self, msg: str):
        self.msg = msg
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'server_error': {'msg': self.msg}}

    @staticmethod
    def from_dict(d: dict) -> 'ServerErrorLeanTacticResult':
        """Build ServerErrorLeanTacticResult from dictionary which was deserialized from JSON"""
        return ServerErrorLeanTacticResult(d['server_error']['msg'])

    def __repr__(self):
        return 'ServerErrorLeanTacticResult(' + 'msg = ' + repr(self.msg) + ')'


class LeanStateResult:

    @staticmethod
    def success(basic_state_information: str) -> 'SuccessLeanStateResult':
        return SuccessLeanStateResult(basic_state_information)

    @staticmethod
    def server_error(msg: str) -> 'ServerErrorLeanStateResult':
        return ServerErrorLeanStateResult(msg)

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> 'LeanStateResult':
        """Build LeanStateResult from dictionary which was deserialized from JSON"""
        if 'success' in d:
            return SuccessLeanStateResult.from_dict(d)
        if 'server_error' in d:
            return ServerErrorLeanStateResult.from_dict(d)

        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class SuccessLeanStateResult(LeanStateResult):
    def __init__(self, basic_state_information: str):
        self.basic_state_information = basic_state_information
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'success': {'basic_state_information': self.basic_state_information}}

    @staticmethod
    def from_dict(d: dict) -> 'SuccessLeanStateResult':
        """Build SuccessLeanStateResult from dictionary which was deserialized from JSON"""
        return SuccessLeanStateResult(d['success']['basic_state_information'])

    def __repr__(self):
        return 'SuccessLeanStateResult(' + 'basic_state_information = ' + repr(self.basic_state_information) + ')'


class ServerErrorLeanStateResult(LeanStateResult):
    def __init__(self, msg: str):
        self.msg = msg
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'server_error': {'msg': self.msg}}

    @staticmethod
    def from_dict(d: dict) -> 'ServerErrorLeanStateResult':
        """Build ServerErrorLeanStateResult from dictionary which was deserialized from JSON"""
        return ServerErrorLeanStateResult(d['server_error']['msg'])

    def __repr__(self):
        return 'ServerErrorLeanStateResult(' + 'msg = ' + repr(self.msg) + ')'


class LeanServerResponse:

    @staticmethod
    def apply_tactic(result: LeanTacticResult) -> 'ApplyTacticLeanServerResponse':
        return ApplyTacticLeanServerResponse(result)

    @staticmethod
    def change_state(result: LeanStateResult) -> 'ChangeStateLeanServerResponse':
        return ChangeStateLeanServerResponse(result)

    @staticmethod
    def error(msg: str) -> 'ErrorLeanServerResponse':
        return ErrorLeanServerResponse(msg)

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        pass

    @staticmethod
    def from_dict(d: dict) -> 'LeanServerResponse':
        """Build LeanServerResponse from dictionary which was deserialized from JSON"""
        if 'apply_tactic' in d:
            return ApplyTacticLeanServerResponse.from_dict(d)
        if 'change_state' in d:
            return ChangeStateLeanServerResponse.from_dict(d)
        if 'error' in d:
            return ErrorLeanServerResponse.from_dict(d)

        raise Exception("Dict not of the correct form: " + str(d))

    def __repr__(self):
        pass


class ApplyTacticLeanServerResponse(LeanServerResponse):
    def __init__(self, result: LeanTacticResult):
        self.result = result
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'apply_tactic': {'result': self.result.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> 'ApplyTacticLeanServerResponse':
        """Build ApplyTacticLeanServerResponse from dictionary which was deserialized from JSON"""
        return ApplyTacticLeanServerResponse(LeanTacticResult.from_dict(d['apply_tactic']['result']))

    def __repr__(self):
        return 'ApplyTacticLeanServerResponse(' + 'result = ' + repr(self.result) + ')'


class ChangeStateLeanServerResponse(LeanServerResponse):
    def __init__(self, result: LeanStateResult):
        self.result = result
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'change_state': {'result': self.result.to_dict()}}

    @staticmethod
    def from_dict(d: dict) -> 'ChangeStateLeanServerResponse':
        """Build ChangeStateLeanServerResponse from dictionary which was deserialized from JSON"""
        return ChangeStateLeanServerResponse(LeanStateResult.from_dict(d['change_state']['result']))

    def __repr__(self):
        return 'ChangeStateLeanServerResponse(' + 'result = ' + repr(self.result) + ')'


class ErrorLeanServerResponse(LeanServerResponse):
    def __init__(self, msg: str):
        self.msg = msg
        pass

    def to_dict(self) -> dict:
        """Dictionary which can later be serialized to JSON"""
        return {'error': {'msg': self.msg}}

    @staticmethod
    def from_dict(d: dict) -> 'ErrorLeanServerResponse':
        """Build ErrorLeanServerResponse from dictionary which was deserialized from JSON"""
        return ErrorLeanServerResponse(d['error']['msg'])

    def __repr__(self):
        return 'ErrorLeanServerResponse(' + 'msg = ' + repr(self.msg) + ')'
