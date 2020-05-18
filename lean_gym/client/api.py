class LeanTactic:
    def _to_dict(self):
        pass

    @staticmethod
    def _from_dict(d):
        if 'apply' in d:
            return LeanTacticApply._from_dict(d)
        if 'cases' in d:
            return LeanTacticCases._from_dict(d)
        if 'intro' in d:
            return LeanTacticIntro._from_dict(d)
        if 'split' in d:
            return LeanTacticSplit._from_dict(d)
        if 'left' in d:
            return LeanTacticLeft._from_dict(d)
        if 'right' in d:
            return LeanTacticRight._from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))


class LeanTacticApply(LeanTactic):
    def __init__(self, sexp):
        self.sexp = sexp
        pass

    def _to_dict(self):
        return {'apply': {'sexp': self.sexp}}

    @staticmethod
    def _from_dict(d):
        return LeanTacticApply(d['apply']['sexp'])


class LeanTacticCases(LeanTactic):
    def __init__(self, sexp):
        self.sexp = sexp
        pass

    def _to_dict(self):
        return {'cases': {'sexp': self.sexp}}

    @staticmethod
    def _from_dict(d):
        return LeanTacticCases(d['cases']['sexp'])


class LeanTacticIntro(LeanTactic):
    def __init__(self, ):
        pass

    def _to_dict(self):
        return {'intro': {}}

    @staticmethod
    def _from_dict(d):
        return LeanTacticIntro()


class LeanTacticSplit(LeanTactic):
    def __init__(self, ):
        pass

    def _to_dict(self):
        return {'split': {}}

    @staticmethod
    def _from_dict(d):
        return LeanTacticSplit()


class LeanTacticLeft(LeanTactic):
    def __init__(self, ):
        pass

    def _to_dict(self):
        return {'left': {}}

    @staticmethod
    def _from_dict(d):
        return LeanTacticLeft()


class LeanTacticRight(LeanTactic):
    def __init__(self, ):
        pass

    def _to_dict(self):
        return {'right': {}}

    @staticmethod
    def _from_dict(d):
        return LeanTacticRight()


class LeanStateControl:
    def _to_dict(self):
        pass

    @staticmethod
    def _from_dict(d):
        if 'jump_to_state' in d:
            return LeanStateControlJumpToState._from_dict(d)
        if 'change_top_goal' in d:
            return LeanStateControlChangeTopGoal._from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))


class LeanStateControlJumpToState(LeanStateControl):
    def __init__(self, state_index):
        self.state_index = state_index
        pass

    def _to_dict(self):
        return {'jump_to_state': {'state_index': self.state_index}}

    @staticmethod
    def _from_dict(d):
        return LeanStateControlJumpToState(d['jump_to_state']['state_index'])


class LeanStateControlChangeTopGoal(LeanStateControl):
    def __init__(self, sexp):
        self.sexp = sexp
        pass

    def _to_dict(self):
        return {'change_top_goal': {'sexp': self.sexp}}

    @staticmethod
    def _from_dict(d):
        return LeanStateControlChangeTopGoal(d['change_top_goal']['sexp'])


class LeanServerRequest:
    def _to_dict(self):
        pass

    @staticmethod
    def _from_dict(d):
        if 'apply_tactic' in d:
            return LeanServerRequestApplyTactic._from_dict(d)
        if 'change_state' in d:
            return LeanServerRequestChangeState._from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))


class LeanServerRequestApplyTactic(LeanServerRequest):
    def __init__(self, tactic):
        self.tactic = tactic
        pass

    def _to_dict(self):
        return {'apply_tactic': {'tactic': self.tactic._to_dict()}}

    @staticmethod
    def _from_dict(d):
        return LeanServerRequestApplyTactic(LeanTactic._from_dict(d['apply_tactic']['tactic']))


class LeanServerRequestChangeState(LeanServerRequest):
    def __init__(self, control):
        self.control = control
        pass

    def _to_dict(self):
        return {'change_state': {'control': self.control._to_dict()}}

    @staticmethod
    def _from_dict(d):
        return LeanServerRequestChangeState(LeanStateControl._from_dict(d['change_state']['control']))


class LeanTacticResult:
    def _to_dict(self):
        pass

    @staticmethod
    def _from_dict(d):
        if 'success' in d:
            return LeanTacticResultSuccess._from_dict(d)
        if 'failure' in d:
            return LeanTacticResultFailure._from_dict(d)
        if 'server_error' in d:
            return LeanTacticResultServerError._from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))


class LeanTacticResultSuccess(LeanTacticResult):
    def __init__(self, basic_goal_information):
        self.basic_goal_information = basic_goal_information
        pass

    def _to_dict(self):
        return {'success': {'basic_goal_information': self.basic_goal_information}}

    @staticmethod
    def _from_dict(d):
        return LeanTacticResultSuccess(d['success']['basic_goal_information'])


class LeanTacticResultFailure(LeanTacticResult):
    def __init__(self, msg):
        self.msg = msg
        pass

    def _to_dict(self):
        return {'failure': {'msg': self.msg}}

    @staticmethod
    def _from_dict(d):
        return LeanTacticResultFailure(d['failure']['msg'])


class LeanTacticResultServerError(LeanTacticResult):
    def __init__(self, msg):
        self.msg = msg
        pass

    def _to_dict(self):
        return {'server_error': {'msg': self.msg}}

    @staticmethod
    def _from_dict(d):
        return LeanTacticResultServerError(d['server_error']['msg'])


class LeanStateResult:
    def _to_dict(self):
        pass

    @staticmethod
    def _from_dict(d):
        if 'success' in d:
            return LeanStateResultSuccess._from_dict(d)
        if 'server_error' in d:
            return LeanStateResultServerError._from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))


class LeanStateResultSuccess(LeanStateResult):
    def __init__(self, basic_state_information):
        self.basic_state_information = basic_state_information
        pass

    def _to_dict(self):
        return {'success': {'basic_state_information': self.basic_state_information}}

    @staticmethod
    def _from_dict(d):
        return LeanStateResultSuccess(d['success']['basic_state_information'])


class LeanStateResultServerError(LeanStateResult):
    def __init__(self, msg):
        self.msg = msg
        pass

    def _to_dict(self):
        return {'server_error': {'msg': self.msg}}

    @staticmethod
    def _from_dict(d):
        return LeanStateResultServerError(d['server_error']['msg'])


class LeanServerResponse:
    def _to_dict(self):
        pass

    @staticmethod
    def _from_dict(d):
        if 'apply_tactic' in d:
            return LeanServerResponseApplyTactic._from_dict(d)
        if 'change_state' in d:
            return LeanServerResponseChangeState._from_dict(d)
        if 'error' in d:
            return LeanServerResponseError._from_dict(d)
        raise Exception("Dict not of the correct form: " + str(d))


class LeanServerResponseApplyTactic(LeanServerResponse):
    def __init__(self, result):
        self.result = result
        pass

    def _to_dict(self):
        return {'apply_tactic': {'result': self.result._to_dict()}}

    @staticmethod
    def _from_dict(d):
        return LeanServerResponseApplyTactic(LeanTacticResult._from_dict(d['apply_tactic']['result']))


class LeanServerResponseChangeState(LeanServerResponse):
    def __init__(self, result):
        self.result = result
        pass

    def _to_dict(self):
        return {'change_state': {'result': self.result._to_dict()}}

    @staticmethod
    def _from_dict(d):
        return LeanServerResponseChangeState(LeanStateResult._from_dict(d['change_state']['result']))


class LeanServerResponseError(LeanServerResponse):
    def __init__(self, msg):
        self.msg = msg
        pass

    def _to_dict(self):
        return {'error': {'msg': self.msg}}

    @staticmethod
    def _from_dict(d):
        return LeanServerResponseError(d['error']['msg'])