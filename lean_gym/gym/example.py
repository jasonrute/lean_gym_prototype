from lean_gym.gym.gym_env_example import LeanEnvExample

goal1 = """( expr.pi ( name.mk_string "p" ( name.anonymous ) ) ( binder_info.default ) ( expr.sort ( level.zero ) ) ( expr.pi ( name.mk_string "a" ( name.anonymous ) ) ( binder_info.default ) ( expr.var 0 ) ( expr.var 1 ) ) )"""
goal2 = """( expr.pi ( name.mk_string "p" ( name.anonymous ) ) ( binder_info.default ) ( expr.sort ( level.zero ) ) ( expr.pi ( name.mk_string "q" ( name.anonymous ) ) ( binder_info.default ) ( expr.sort ( level.zero ) ) ( expr.pi ( name.mk_string "a" ( name.anonymous ) ) ( binder_info.default ) ( expr.var 0 ) ( expr.pi ( name.mk_string "a" ( name.anonymous ) ) ( binder_info.default ) ( expr.var 2 ) ( expr.var 2 ) ) ) ) )"""
goal3 = """( expr.app ( expr.const ( name.mk_string \"not\" ( name.anonymous ) ) ( list.nil ) ) ( expr.app ( expr.app ( expr.const ( name.mk_string \"iff\" ( name.anonymous ) ) ( list.nil ) ) ( expr.local_const ( name.mk_numeral 165403 ( name.mk_numeral 8316 ( name.mk_string \"_fresh\" ( name.mk_numeral 0 ( name.anonymous ) ) ) ) ) ( name.mk_string \"p\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_numeral 1 ( name.anonymous ) ) ( list.nil ) ) ) ) ( expr.app ( expr.const ( name.mk_string \"not\" ( name.anonymous ) ) ( list.nil ) ) ( expr.local_const ( name.mk_numeral 165403 ( name.mk_numeral 8316 ( name.mk_string \"_fresh\" ( name.mk_numeral 0 ( name.anonymous ) ) ) ) ) ( name.mk_string \"p\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_numeral 1 ( name.anonymous ) ) ( list.nil ) ) ) ) ) )"""


def main():
    env = LeanEnvExample(goal2)

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
