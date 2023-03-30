import pynusmv
from pynusmv import prop
from pynusmv.mc import check_ctl_spec

from bp_modules import *
from hot_cold import *
pynusmv.init.init_nusmv()
event_list = ["Start", "HOT", "COLD", "IDLE"]
bt_list = [
    bthread_to_module(add_a, "adda", event_list),
    bthread_to_module(add_b, "addb", event_list),
    bthread_to_module(control, "control", event_list),
]
main = main_module(event_list, bt_list)
# print(bt_list[0])
# print(bt_list[1])
# print(bt_list[2])
# print(main)
pynusmv.glob.load(bt_list[0], bt_list[1], bt_list[2], main)
pynusmv.glob.compute_model()

fsm = pynusmv.glob.prop_database().master.bddFsm
spec = prop.af(prop.atom("bt0.must_finish = FALSE"))

print(check_ctl_spec(fsm, spec))
if not check_ctl_spec(fsm, spec):
    from pynusmv.mc import explain, eval_ctl_spec
    explanation = explain(fsm, fsm.init & ~eval_ctl_spec(fsm, spec), spec)
    #print(explanation[0].get_str_values())
    for state in explanation[::2]:
        if state == explanation[-1]:
            print("-- Loop starts here")
        d = {k: v for k, v in state.get_str_values().items() if k in ["event", "bt0.state", "bt1.state", "bt2.state", "bt0.must_finish", "bt1.must_finish", "bt2.must_finish", "must_finish"]}
        print(d)