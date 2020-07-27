import json
import subprocess
import sys
from datetime import datetime
from pprint import pprint
from typing import List, Optional

from lean_gym.client import dumb_json, api


class LeanServer:
    """
    Open up my special Lean server and communicate with it.
    """

    def __init__(self, proc_args: Optional[List[str]]):
        """
        Start up connection to Lean.

        :param proc_args: The args for Popen to start the process.  The processes stdin and stdout will be piped.
        For example, use ["lean", "--run", "path-to-file.lean"] to run an io main in a lean file or
        ["lean", "path-to-file.lean"] to run another type of entry point.
        If proc_args is None, then communicate with sys.stdin an sys.stdout.  (This latter case is useful when you
        want the gym to be "reversable" so that a proof can be submitted to a human user.)
        """
        if proc_args:
            self.proc = subprocess.Popen(
                proc_args,
                universal_newlines=True,
                stdin=subprocess.PIPE,  # pipe STDIN and STDOUT to send and receive messages
                stdout=subprocess.PIPE
            )
            self.outward_comm_stream = self.proc.stdin
            self.inward_comm_stream = self.proc.stdout
        else:
            self.proc = None
            self.outward_comm_stream = sys.stdout
            self.inward_comm_stream = sys.stdin

    # make into a context manager so that it closes lean processes automatically
    def __enter__(self):
        if self.proc is not None:
            self.proc.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        if self.proc is not None:
            self.proc.__exit__(type, value, traceback)

    def send_and_receive_dicts(self, d, dumb=False):
        # send
        if dumb:
            dumb_json.json_write(d, self.outward_comm_stream)
        else:
            print(json.dumps(d), file=self.outward_comm_stream, flush=True)

        # receive
        j = None
        while j is None:
            raw_output = self.inward_comm_stream.readline()
            try:
                j = json.loads(raw_output)
            # TODO: Don't use bare except
            except:
                raise Exception("Bad json: >{}<".format(raw_output))

        return j

    def send_request_and_receive_response(self, request, debug=False):
        request_dict = request.to_dict()

        # TODO: Use logging instead
        if debug:
            print()
            print("=>:", datetime.now().strftime('%H:%M:%S.%f'))
            pprint(request_dict)
            print()

        # use "dumb" json protocol
        response_dict = self.send_and_receive_dicts(request_dict, dumb=True)

        # TODO: Use logging instead
        if debug:
            print()
            print("<=:", datetime.now().strftime('%H:%M:%S.%f'))
            pprint(response_dict)
            print()

        response = api.LeanServerResponse.from_dict(response_dict)

        if isinstance(response, api.ErrorLeanServerResponse):
            raise Exception(response.msg)

        return response

    def execute_tactic(self, state_ix: int, focus: api.TacticFocus, tactic: api.LeanTactic, cfg: api.StateInfoConfig, debug: bool = False) -> api.ExecuteTacticLeanServerResponse:
        request = api.ExecuteTacticLeanServerRequest(state_ix, focus, tactic, cfg)

        response = self.send_request_and_receive_response(request, debug=debug)

        if isinstance(response, api.ErrorLeanServerResponse):
            raise Exception(response.msg)

        assert isinstance(response, api.ExecuteTacticLeanServerResponse)

        return response

    def change_goal(self, goal: api.LeanGoal, cfg: api.StateInfoConfig, debug: bool = False) -> api.ChangeGoalLeanServerResponse:
        request = api.ChangeGoalLeanServerRequest(goal, cfg)

        response = self.send_request_and_receive_response(request, debug=debug)

        if isinstance(response, api.ErrorLeanServerResponse):
            raise Exception(response.msg)

        assert isinstance(response, api.ChangeGoalLeanServerResponse)

        return response

    def get_state_info(self, state_ix: int, cfg: api.StateInfoConfig, debug: bool = False) -> api.GetStateInfoLeanServerResponse:
        request = api.GetStateInfoLeanServerRequest(state_ix, cfg)

        response = self.send_request_and_receive_response(request, debug=debug)

        if isinstance(response, api.ErrorLeanServerResponse):
            raise Exception(response.msg)

        assert isinstance(response, api.GetStateInfoLeanServerResponse)

        return response

    def exit(self, msg: api.Option[str], state_ix: api.Option[int], debug=False) -> api.ExitLeanServerResponse:
        request = api.ExitLeanServerRequest(msg, state_ix)

        response = self.send_request_and_receive_response(request, debug=debug)

        if isinstance(response, api.ErrorLeanServerResponse):
            raise Exception(response.msg)

        assert isinstance(response, api.ExitLeanServerResponse)

        return response
