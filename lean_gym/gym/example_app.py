# make script runnable by pointing to lean_gym package
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

from lean_gym.gym.gym_env_example import LeanEnvExample


def main():
    print("", file=sys.stderr)
    print("Starting up fixed solution solver", file=sys.stderr)

    print("Communicating with lean", file=sys.stderr)

    # use --app flag to run as lean-callable application
    if len(sys.argv) == 2 and sys.argv[1] == "--app":
        env = LeanEnvExample(None, use_in_reverse=True)
    else:
        env = LeanEnvExample("∀ p q : Prop, q → p → q", use_in_reverse=False)

    print("Solving...", file=sys.stderr)
    env.step({'tactic': 'intro'})
    env.step({'tactic': 'intro'})
    env.step({'tactic': 'intro'})
    env.step({'tactic': 'intro'})
    env.step({'tactic': 'apply', 'local_id': 'a'})

    print("Solved", file=sys.stderr)
    print("", file=sys.stderr)

    env.close(msg=("Try this: " + env.info['proof']))


if __name__ == '__main__':
    main()
