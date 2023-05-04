from bp_model_check import ModelChecker
from examples.dining_philosophers import *
from examples.hot_cold import *
import sys

def main(args):
    example = args[0]

    if example == "hot_cold1":
        N = int(args[1])
        M = int(args[2])
        set_bprogram(N, M)
        mc = ModelChecker(["Start", "HOT"] + ["COLD" + str(i) for i in range(M)],
                          [lambda: add_a()] + list(map((lambda n: lambda: add_b("COLD" + str(n))), range(M))) + [lambda: control()],
                          ["adda"] + ["addb"+str(i) for i in range(M)] + ["control"])
        spec = "AG (AF must_finish = FALSE)"
    elif example == "hot_cold2":
        N = int(args[1])
        M = int(args[2])
        set_bprogram(N, M)
        mc = ModelChecker(["Start", "HOT"] + ["COLD" + str(i) for i in range(M)],
                          [lambda: add_a()] + list(map((lambda n: lambda: add_b("COLD" + str(n))), range(M))) + [lambda: control2()],
                          ["adda"] + ["addb"+str(i) for i in range(M)] + ["control"])
        spec = "AG (AF must_finish = FALSE)"
    elif example == "dining_philosophers1":
        N = int(args[1])
        set_dp_bprogram(int(args[1]))
        all_events = [BEvent(f"T{i}R") for i in range(N)] + \
                 [BEvent(f"T{i}L") for i in range(N)] + \
                 [BEvent(f"P{i}R") for i in range(N)] + \
                 [BEvent(f"P{i}L") for i in range(N)]
        mc = ModelChecker([x.name for x in all_events],
                          list(map((lambda n: lambda: philosopher(n)), range(N))) +
                          list(map((lambda n: lambda: fork(n)), range(N))) +
                          [lambda: fork_eventually_released(0)],
                          ["p" + str(i) for i in range(N)] +
                          ["f" + str(i) for i in range(N)] +
                          ["f0r"]
                          )
        spec = "AG (!(event = DONE))"
    elif example == "dining_philosophers2":
        N = int(args[1])
        set_dp_bprogram(int(args[1]))
        all_events = [BEvent(f"T{i}R") for i in range(N)] + \
                     [BEvent(f"T{i}L") for i in range(N)] + \
                     [BEvent(f"P{i}R") for i in range(N)] + \
                     [BEvent(f"P{i}L") for i in range(N)] + \
                     [BEvent(f"TS{i}") for i in range(N)] + \
                     [BEvent(f"RS{i}") for i in range(N)]
        mc = ModelChecker([x.name for x in all_events],
                          list(map((lambda n: lambda: philosopher(n)), range(N))) +
                          list(map((lambda n: lambda: fork(n)), range(N))) +
                          [lambda: fork_eventually_released(0)] +
                          [lambda: semaphore()] +
                          list(map((lambda n: lambda: take_semaphore(n)), range(N))),
                          ["p" + str(i) for i in range(N)] +
                          ["f" + str(i) for i in range(N)] +
                          ["f0r"] +
                          ["s"] +
                          ["ts" + str(i) for i in range(N)])
        spec = "AG (!(event = DONE))"

    # spec = prop.ag(prop.af(prop.atom(("bt0.must_finish = FALSE"))))
    print("number of events:", len(mc.event_list))
    result, explanation = mc.check(spec, debug=True, find_counterexample=False)
    print(result)
    if not result and explanation is not None:
        print("violation event trace:")
        print(explanation)


if __name__ == "__main__":
    if True:#len(sys.argv) >= 2:
        #main(sys.argv[1:])
        main("dining_philosophers2 3".split())
        #main("hot_cold2 90 3".split())
    else:
        for i in [10, 20, 30]:
            for j in range(1, 4):
                print("-"*80)
                print("Example:", "hot_cold1", i, j)
                args = ["hot_cold1", i, j]
                main(args)
                print("-" * 80)
                print("Example:", "hot_cold2", i, j)
                args = ["hot_cold2", i, j]
                main(args)
        for i in [2, 3]:
            print("-" * 80)
            print("Example:", "dining_philosophers1", i)
            args = ["dining_philosophers1", i]
            main(args)
            print("-" * 80)
            print("Example:", "dining_philosophers2", i)
            args = ["dining_philosophers2", i]
            main(args)




