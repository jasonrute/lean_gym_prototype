from lean_gym.gym.gym_env_example import LeanEnvExample

def main():
    env = LeanEnvExample("∀ p q : Prop, q → p → q")

    env.reset()
    env.render()
    s = env.get_state()

    env.step({'tactic': 'intro'})
    env.render()

    env.set_state(s)
    env.render()

    env.step({'tactic': 'intro'})
    env.render()

    env.step({'tactic': 'intro'})
    env.render()

    env.step({'tactic': 'intro'})
    env.render()

    env.step({'tactic': 'apply', 'local_id': 'a'})
    env.render()


if __name__ == '__main__':
    main()
