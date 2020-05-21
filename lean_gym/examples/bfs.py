import collections

from lean_gym.client import api
from lean_gym.examples.tools import parse_goal_info

tactics = [
    (api.LeanTacticApply, 1),
    (api.LeanTacticCases, 1),
    (api.LeanTacticIntro, 0),
    (api.LeanTacticSplit, 0),
    (api.LeanTacticLeft, 0),
    (api.LeanTacticRight, 0),
]


class BreathFirstProofSearch:

    def __init__(self, lean_server):
        self.lean = lean_server

    def search(self, goal_sexp):
        result = self.lean.change_state(
            api.LeanStateControlChangeTopGoal(
                sexp=goal_sexp
            )
        )
        state_info = parse_goal_info(result.basic_state_information)

        queue = collections.deque()
        for tac, arg_count in tactics:
            if arg_count:  # right now arg_count is either 1 or 0
                for v in state_info['locals']:
                    queue.append((state_info['state_ix'], tac, [v], [(tac.__name__, [v])]))
            else:
                queue.append((state_info['state_ix'], tac, [], [(tac.__name__, [])]))

        while queue:
            state, tactic, args, proof = queue.popleft()

            self.lean.change_state(api.LeanStateControlJumpToState(state))
            result = self.lean.apply_tactic(tactic(*args))

            if isinstance(result, api.LeanTacticResultFailure):
                continue

            state_info = parse_goal_info(result.basic_goal_information)

            if state_info['solved']:
                return proof

            for tac, arg_count in tactics:
                if arg_count:  # right now arg_count is either 1 or 0
                    for v in state_info['locals']:
                        queue.append((state_info['state_ix'], tac, [v], proof + [(tac.__name__, [v])]))
                else:
                    queue.append((state_info['state_ix'], tac, [], proof + [(tac.__name__, [])]))
