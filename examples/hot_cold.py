from bppy.model.b_thread import b_thread
from bppy.model.b_event import BEvent
from bppy.model.sync_statement import waitFor, request, block
must_finish = "must_finish"
data = "data"
N = 3
M = 1
LETTERS = "BCDEFGH"
import tracemalloc
import time
event_list = ["Start", "HOT", "IDLE"] + [C for C in LETTERS[:M]]
any_event = [BEvent(C) for C in LETTERS[:M]]

@b_thread
def add_a():
    yield {waitFor: BEvent("Start"), must_finish: False, data: locals()}
    for i in range(N):
        yield {request: BEvent("HOT"), must_finish: True, data: locals()}

@b_thread
def add_b(C):
    yield {waitFor: BEvent("Start"), must_finish: False, data: locals()}
    for i in range(N):
        yield {request: BEvent(C), must_finish: False, data: locals()}
    while True:
        yield {request: BEvent("IDLE"), must_finish: False, data: locals()}

@b_thread
def control():
    yield {request: BEvent("Start"), must_finish: False, data: locals()}
    while True:
        yield {waitFor: BEvent("HOT"), must_finish: False, data: locals()}
        yield {waitFor: any_event, block: BEvent("HOT"), must_finish: False, data: locals()}


if __name__ == "__main__":
    import pynusmv
    from pynusmv import prop
    from pynusmv.mc import check_ctl_spec
    from bp_modules import *
    import sys

    sys.setrecursionlimit(10000)
    pynusmv.init.init_nusmv()
    event_list = ["Start", "HOT", "IDLE"] + [C for C in LETTERS[:M]]
    any_event = [BEvent(C) for C in event_list]
    bt_list = []
    bt_list.append(bthread_to_module(add_a, "adda", event_list))
    bt_list.extend([bthread_to_module(lambda: add_b(C), "add"+C, event_list) for C in LETTERS[:M]])
    bt_list.append(bthread_to_module(control, "control", event_list))
    main = main_module(event_list, bt_list)
    print(bt_list[0])
    print(bt_list[1])
    print(bt_list[2])
    print(main)
    st = time.time()
    pynusmv.glob.load(bt_list[0], bt_list[1], bt_list[2], main)
    #pynusmv.glob.load(bt_list[0], bt_list[1], main)
    pynusmv.glob.compute_model()

    fsm = pynusmv.glob.prop_database().master.bddFsm
    spec = prop.ag(prop.af(prop.atom(("bt0.must_finish = FALSE"))))
    # spec = prop.ag(prop.af(prop.atom(("must_finish = FALSE"))))
    import tracemalloc
    tracemalloc.start()
    result = check_ctl_spec(fsm, spec)
    print(tracemalloc.get_traced_memory()[1])
    tracemalloc.stop()
    print(result)
    print(time.time() - st)
    if not result:
        from pynusmv.mc import explain, eval_ctl_spec

        # explanation = explain(fsm, fsm.init & ~eval_ctl_spec(fsm, spec), spec)
        a = eval_ctl_spec(fsm, spec)
        print(a)
        explanation = explain(fsm, fsm.init, spec)
        # print(explanation[0].get_str_values())
        for state in explanation[::2]:
            if state == explanation[-1]:
                print("-- Loop starts here")
            d = {k: v for k, v in state.get_str_values().items() if
                 k in ["event", "bt0.state", "bt1.state", "bt2.state", "bt0.must_finish", "bt1.must_finish",
                       "bt2.must_finish", "must_finish"]}
            print(d)