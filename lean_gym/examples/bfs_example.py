from pathlib import Path
from pprint import pprint

from client import api
from client.lean_server import LeanServer
from examples.bfs import BreathFirstProofSearch

goal = """( expr.app ( expr.const ( name.mk_string \"not\" ( name.anonymous ) ) ( list.nil ) ) ( expr.app ( expr.app ( expr.const ( name.mk_string \"iff\" ( name.anonymous ) ) ( list.nil ) ) ( expr.local_const ( name.mk_numeral 165403 ( name.mk_numeral 8316 ( name.mk_string \"_fresh\" ( name.mk_numeral 0 ( name.anonymous ) ) ) ) ) ( name.mk_string \"p\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_numeral 1 ( name.anonymous ) ) ( list.nil ) ) ) ) ( expr.app ( expr.const ( name.mk_string \"not\" ( name.anonymous ) ) ( list.nil ) ) ( expr.local_const ( name.mk_numeral 165403 ( name.mk_numeral 8316 ( name.mk_string \"_fresh\" ( name.mk_numeral 0 ( name.anonymous ) ) ) ) ) ( name.mk_string \"p\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_numeral 1 ( name.anonymous ) ) ( list.nil ) ) ) ) ) )"""

def main():
    lean_file_path = Path(__file__).parent / "../../src/examples/main_entry.lean"
    lean_path_str = str(lean_file_path.absolute())
    with LeanServer(["lean", "--run", lean_path_str]) as lean:
        # not needed.  Just for warmup to test speed
        lean.change_state(
                api.LeanStateControlChangeTopGoal(
                    sexp=goal
                )
            )
        print("Ready, set, go...")
        pprint(BreathFirstProofSearch(lean).search(goal))

if __name__ == '__main__':
    main()
