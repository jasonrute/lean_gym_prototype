import re
from typing import Optional, Tuple

from client.lean_server import LeanServer
from client import api

TACTICS = {
    'apply': (api.LeanTacticApply, 1),
    'cases': (api.LeanTacticCases, 1),
    'intro': (api.LeanTacticIntro, 0),
    'split': (api.LeanTacticSplit, 0),
    'left': (api.LeanTacticLeft, 0),
    'right': (api.LeanTacticRight, 0),
}


class LeanEnvExample:
    """
    This is an example gym which follows an interface similar
    to open AI's gym.
    """
    def __init__(self, goal: Optional[str]):
        """
        :param goal:  The goal to solve.  Enter as a string of Lean code, e.g. "forall p q : Prop, p -> p \\/ q".
        """
        # TODO: Change so that the goal is Lean code and not an s-expression

        # this gym is a wrapper around a custom Lean server process.
        self.server = LeanServer()
        self.goal_string = goal  # save to reset space later
        self.info = {}
        self.reset()

    @staticmethod
    def _parse_goal_info(goal_info: str) -> dict:
        state_ix = int(goal_info.split("Current state index:\n")[1].split("\n")[0])

        goal_state_str = goal_info.split("Proof state:\n")[1].split("Current state index:")[0].strip()

        if "no goals" in goal_info:
            solved = True
        else:
            solved = False

        if not solved:
            local_vars = {}
            for l in goal_info.split("Local names:\n")[1].split("\n"):
                if l:
                    regex = r"name\.mk_string \"([^ ]*)\" \( name\.anonymous \)"
                    m = re.search(regex, l)
                    local_vars[m.group(1)] = l

        else:
            local_vars = None

        return {'state_ix': state_ix, 'locals': local_vars, 'solved': solved, 'pp_state': goal_state_str, 'raw': goal_info}

    def step(self, action: dict) -> Tuple[dict, float, bool, dict]:
        """
        Run one timestep of the environment's dynamics. When end of episode
        is reached, reset() should be called to reset the environment's internal state.
        Input
        -----
        action : an action provided by the environment
        Outputs
        -------
        (observation, reward, done, info)
        observation : agent's observation of the current environment
        reward [Float] : amount of reward due to the previous action
        done : a boolean, indicating whether the episode has ended
        info : a dictionary containing other diagnostic information from the previous action
        """

        tac, arg_cnt = TACTICS[action['tactic']]
        if arg_cnt == 1:
            args = [self.info['locals'][action['local_id']]]
        else:
            args = []

        tactic = tac(*args)
        result = self.server.apply_tactic(tactic)

        if isinstance(result, api.LeanTacticResultFailure):
            # tactic failed
            reward = -1
            done = False
            return self.info, reward, done, self.info

        assert isinstance(result, api.LeanTacticResultSuccess)
        goal_info = result.basic_goal_information
        self.info = LeanEnvExample._parse_goal_info(goal_info)

        done = self.info['solved']

        if done:
            reward = 1000
        else:
            reward = 0
        return self.info, reward, done, self.info

    def reset(self):
        """
        Resets the state of the environment, returning an initial observation.
        Outputs
        -------
        observation : the initial observation of the space. (Initial reward is assumed to be 0.)
        """
        result = self.server.change_state(api.LeanStateControlChangeTopGoal(self.goal_string))
        assert isinstance(result, api.LeanStateResultSuccess)
        goal_info = result.basic_state_information
        self.info = LeanEnvExample._parse_goal_info(goal_info)
        assert not self.info['solved']

        return self.info

    def render(self):
        print("===========================")
        print(self.info['pp_state'])
        print("===========================")
        print()

    def get_state(self) -> dict:
        return self.info

    def set_state(self, state: dict) -> dict:
        self.info = state
        return self.info

    @property
    def action_space(self):
        """
        Returns a Space object
        """
        raise NotImplementedError

    @property
    def observation_space(self):
        """
        Returns a Space object
        """
        raise NotImplementedError
