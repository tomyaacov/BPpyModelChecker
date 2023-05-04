from bp_modules import *
from hot_cold_scripts.hot_cold_original import *
import sys
import pynusmv
from pynusmv import prop
from pynusmv.mc import check_ctl_spec
import time
import tracemalloc


sys.setrecursionlimit(10000)

class ModelChecker:

    def __init__(self, event_list, bt_generators_list, bt_names_list):
        self.event_list = event_list
        self.bt_generators_list = bt_generators_list
        self.bt_names_list = bt_names_list

    def check(self, spec, debug=False, find_counterexample=False):
        if debug:
            print("initializing NuSMV")
            ts = time.time()
            tracemalloc.start()
        pynusmv.init.init_nusmv()
        if debug:
            print("Converting bthreads to NuSMV modules")
        bt_list = [bthread_to_module(g, n, self.event_list) for g, n in zip(self.bt_generators_list, self.bt_names_list)]
        if debug:
            print("Creating main module")
        main = main_module(self.event_list, bt_list)
        if debug:
            print("Loading model into NuSMV")

        with open("output/bp_model.smv", "w") as f:
            for bt in bt_list:
                f.write(str(bt))
                f.write("\n")
            f.write(str(main))
            f.write("\n")
            f.write("SPEC " + str(spec))
        pynusmv.glob.load_from_file("output/bp_model.smv")

        if debug:
            print("Computing model")
        pynusmv.glob.compute_model()


        #spec = prop.ag(prop.af(prop.atom(("must_finish = FALSE"))))
        spec = pynusmv.glob.prop_database()[0].expr

        if debug:
            print("Checking CTL spec")
        fsm = pynusmv.glob.prop_database().master.bddFsm
        result = check_ctl_spec(fsm, spec)
        if debug:
            print("Done in", time.time() - ts, "seconds")
            print("Memory usage (bytes):", tracemalloc.get_traced_memory()[1])
            tracemalloc.stop()
        if not result and find_counterexample:
            from pynusmv.mc import explain, eval_ctl_spec
            if debug:
                print("Finding counterexample")
            explanation = explain(fsm, fsm.init & ~eval_ctl_spec(fsm, spec), spec)
            skip_last = False
            explanation_str = ""
            for state in explanation[2::2]:
                if state == explanation[-1]:
                    if skip_last:
                        break
                    skip_last = True
                    explanation_str += "-- Loop starts here" + "\n"
                explanation_str += state.get_str_values()["event"] + "\n"
            # for state in explanation[::2]:
            #     if state == explanation[-1]:
            #         print("-- Loop starts here")
            #     d = {k: v for k, v in state.get_str_values().items() if
            #          k in ["event", "bt0.state", "bt1.state", "bt2.state", "bt0.must_finish", "bt1.must_finish",
            #                "bt2.must_finish", "must_finish"]}
            #     print(d)
        else:
            explanation_str = None

        pynusmv.init.deinit_nusmv()
        return result, explanation_str


