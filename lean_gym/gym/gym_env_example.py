import re
from pathlib import Path
from typing import Optional, Tuple

from lean_gym.client.lean_server import LeanServer
from lean_gym.client import api

TACTICS = {
    'apply': (api.ApplyLeanTactic, 1),
    'cases': (api.CasesLeanTactic, 1),
    'intro': (api.IntroLeanTactic, 0),
    'split': (api.SplitLeanTactic, 0),
    'left': (api.LeftLeanTactic, 0),
    'right': (api.RightLeanTactic, 0),
}


class LeanEnvExample:
    """
    This is an example gym which follows an interface similar
    to open AI's gym.
    """
    def __init__(self, goal: Optional[str], use_in_reverse=False):
        """
        :param goal:  The goal to solve.  Enter as a string of Lean code, e.g. "forall p q : Prop, p -> p \\/ q".
        :param use_in_reverse: This environment can be used in reverse.  The environment will communicate
        with sys.stdin and sys.stdout, allowing lean to call the agent's python file as a process to provide guidance.
        """
        # TODO: Change so that the goal is Lean code and not an s-expression

        # this gym is a wrapper around a custom Lean server process.
        if use_in_reverse:
            self.server = LeanServer(None)
        else:
            lean_file_path = Path(__file__).parent / "../../src/examples/parser_entry.lean"
            lean_path_str = str(lean_file_path.absolute())
            self.server = LeanServer(["lean", lean_path_str])

        self.goal_string = goal  # save to reset space later
        self.info = {}

        self.reset()

    @staticmethod
    def _parse_goal_info(goal_info: str) -> dict:
        proof = goal_info.split("Pretty-printed proof:\n")[1].split("\n")[0].strip()

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

        return {
            'state_ix': state_ix,
            'locals': local_vars,
            'solved': solved,
            'pp_state': goal_state_str,
            'proof': proof,
            'raw': goal_info
        }

    def _tactic(self, action: dict) -> api.LeanTactic:
        """
        Turn action into a tactic
        """
        tac, arg_cnt = TACTICS[action['tactic']]
        if arg_cnt == 1:
            args = [self.info['locals'][action['local_id']]]
        else:
            args = []

        return tac(*args)

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

        tactic = self._tactic(action)
        result = self.server.apply_tactic(tactic)

        if isinstance(result, api.FailureLeanTacticResult):
            # tactic failed
            reward = -1
            done = False
            return self.info, reward, done, self.info

        assert isinstance(result, api.SuccessLeanTacticResult)
        goal_info = result.basic_goal_information
        self.info = LeanEnvExample._parse_goal_info(goal_info)

        done = self.info['solved']

        if done:
            reward = 1000
        else:
            reward = 0
        return self.info, reward, done, self.info

    def reset(self) -> dict:
        """
        Resets the state of the environment, returning an initial observation.
        Outputs
        -------
        observation : the initial observation of the space. (Initial reward is assumed to be 0.)
        """
        if self.goal_string is None:
            change = api.JumpToStateLeanStateControl(state_index=0)
        else:
            change = api.ChangeTopGoalPpLeanStateControl(self.goal_string)

        result = self.server.change_state(change)
        assert isinstance(result, api.SuccessLeanStateResult)
        goal_info = result.basic_state_information
        self.info = LeanEnvExample._parse_goal_info(goal_info)
        assert not self.info['solved']

        return self.info

    def render(self):
        print()
        print(self.info['proof'])
        print("===========================")
        print(self.info['pp_state'])
        print("===========================")
        print()

    def get_state(self) -> dict:
        return self.info

    def set_state(self, state: dict) -> dict:
        # TODO: This is wrong!
        raise NotImplementedError

    def close(self, msg: str) -> None:
        self.server.exit(msg)
        # TODO: I also need to shut down the process

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
