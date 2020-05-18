import json
import subprocess
from datetime import datetime
from pprint import pprint

from client import dumb_json, api


class LeanServer:
    """
    Open up my special Lean server and communicate with it.
    """

    def __init__(self):
        self.proc = subprocess.Popen(['lean', '--run', '../src/examples/main_entry.lean'],
                                     universal_newlines=True,
                                     stdin=subprocess.PIPE,  # pipe STDIN and STDOUT to send and receive messages
                                     stdout=subprocess.PIPE,
                                     # stderr=subprocess.PIPE
                                     )

    # make into a context manager so that it closes lean server automatically
    def __enter__(self):
        self.proc.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.proc.__exit__(type, value, traceback)

    def send_and_receive_dicts(self, d, dumb=False):
        # send
        if dumb:
            dumb_json.json_write(d, self.proc.stdin)
        else:
            print(json.dumps(d), file=self.proc.stdin, flush=True)

        # recieve
        j = None
        while j is None:
            raw_output = self.proc.stdout.readline()
            try:
                j = json.loads(raw_output)
            except:
                print("Bad json: >{}<".format(raw_output))
                raise Exception

        return j

    def send_request_and_receive_response(self, request, debug=False):
        request_dict = request._to_dict()

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

        response = api.LeanServerResponse._from_dict(response_dict)

        if isinstance(response, api.LeanServerResponseError):
            raise Exception(response.msg)

        return response

    def apply_tactic(self, tactic, debug=False):
        request = api.LeanServerRequestApplyTactic(
            tactic=tactic
        )

        response = self.send_request_and_receive_response(request, debug=debug)

        assert isinstance(response, api.LeanServerResponseApplyTactic), type(response)
        result = response.result

        if isinstance(result, api.LeanTacticResultServerError):
            raise Exception(result.msg)

        return result

    def change_state(self, state_control, debug=False):
        request = api.LeanServerRequestChangeState(
            control=state_control
        )

        response = self.send_request_and_receive_response(request, debug=debug)

        assert isinstance(response, api.LeanServerResponseChangeState), type(response)
        result = response.result

        if isinstance(result, api.LeanStateResultServerError):
            raise Exception(result.msg)

        return result