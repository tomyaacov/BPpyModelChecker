from pynusmv.model import *
from bppy import request, block, waitFor, BEvent
from bppy.model.event_selection.simple_event_selection_strategy import SimpleEventSelectionStrategy
from copy import copy as copy_obj
from itertools import chain, combinations
from dfs import DFSBThread


def powerset(iterable):
    xs = list(iterable)
    return chain.from_iterable(combinations(xs,n) for n in range(1, len(xs)+1))


def bthread_to_module(bthread, bthread_name, event_list):
    dfs = DFSBThread(lambda: bthread(), SimpleEventSelectionStrategy(), event_list)
    init_s, visited = dfs.run()
    visited = dict([(k, v) for k, v in enumerate(visited)])
    id_to_change = [k for k, v in visited.items() if v == init_s][0]
    s_to_change = visited[0]
    visited[id_to_change] = s_to_change
    visited[0] = init_s
    rev_visited = {v: k for k, v in visited.items()}

    bt1_mod_dict = {}
    bt1_mod_dict["event"] = Identifier("event")
    bt1_mod_dict["ARGS"] = [bt1_mod_dict["event"]]
    bt1_mod_dict["state"] = Var(Range(0, len(visited)))

    bt1_mod_dict.update({
        e + "_requested": Var(Boolean(), name=e + "_requested") for e in event_list
    })
    bt1_mod_dict.update({
        e + "_blocked": Var(Boolean(), name=e + "_blocked") for e in event_list
    })
    bt1_mod_dict["must_finish"] = Var(Boolean())
    bt1_mod_dict["INIT"] = [bt1_mod_dict["state"] == 0]
    bt1_mod_dict_assign = {}
    for e in event_list:
        case_list = tuple([(bt1_mod_dict["state"] == i, Trueexp()) if e == node.data.get(request,
                                                                                         BEvent("")).name else (
        bt1_mod_dict["state"] == i, Falseexp()) for i, node in visited.items()])
        bt1_mod_dict_assign[e + "_requested"] = Case(case_list + ((Trueexp(), Falseexp()),))
        case_list = tuple([(bt1_mod_dict["state"] == i, Trueexp()) if e == node.data.get(block, BEvent("")).name else (
        bt1_mod_dict["state"] == i, Falseexp()) for i, node in visited.items()])
        bt1_mod_dict_assign[e + "_blocked"] = Case(case_list + ((Trueexp(), Falseexp()),))

    case_list = []
    for i, node in visited.items():
        d = {}
        for e, next_node in node.transitions.items():
            d[rev_visited[next_node]] = d.get(rev_visited[next_node], []) + [e]
        for j, events in d.items():
            if i == j:
                continue  # self loop not necessary
            or_chain = Falseexp()
            for e in events:
                or_chain = Or(bt1_mod_dict["event"].next() == e, or_chain)
            case_list.append((And(bt1_mod_dict["state"] == i, or_chain), j))
    bt1_mod_dict_assign["next(state)"] = Case(tuple(case_list) + ((Trueexp(), bt1_mod_dict["state"]),))
    true_set = set([i for i, node in visited.items() if node.must_finish])
    true_or_chain = Falseexp()
    false_or_chain = Falseexp()
    for i, node in visited.items():
        if i in true_set:
            true_or_chain = Or(bt1_mod_dict["state"] == i, true_or_chain)
        else:
            false_or_chain = Or(bt1_mod_dict["state"] == i, false_or_chain)
    bt1_mod_dict_assign["must_finish"] = Case(((true_or_chain, Trueexp()),
                                               (false_or_chain, Falseexp()),
                                               (Trueexp(), Falseexp())))
    bt1_mod_dict["ASSIGN"] = bt1_mod_dict_assign
    return type(bthread_name, (Module,), bt1_mod_dict)


def main_module(event_list, bt_list):
    mod_dict = {}
    mod_dict["event"] = Var(Scalar(tuple(["START", "DONE", "Dummy"] + event_list)))
    bt_modules = []
    for i, bt in enumerate(bt_list):
        mod_dict["bt"+str(i)] = Var(bt(mod_dict["event"]))
        bt_modules.append(mod_dict["bt"+str(i)])
    mod_dict["INIT"] = [mod_dict["event"] == "START"]
    mod_dict_define = {}
    for e in event_list:
        mod_dict_define[e + "_requested"] = Falseexp()
        mod_dict_define[e + "_blocked"] = Falseexp()
    for i in range(len(bt_list)):
        for v in mod_dict["bt"+str(i)].type.VAR:
            if v.name in mod_dict_define:
                mod_dict_define[v.name] = Or("bt"+str(i) + "." + v.name, mod_dict_define[v.name])
    mod_dict_define["must_finish"] = Falseexp()
    for i in range(len(bt_list)):
        mod_dict_define["must_finish"] = Or("bt"+str(i) + ".must_finish", mod_dict_define["must_finish"])
    mod_dict["DEFINE"] = mod_dict_define
    mod_dict_assign = {}
    case_list = [(mod_dict["event"] == "DONE", "DONE")]
    for subset in powerset(event_list):
        statement = Trueexp()
        for e in event_list:
            if e in subset:
                statement = And(And(statement, e + "_requested"), "!" + e + "_blocked")
            else:
                statement = And(statement, Or("!" + e + "_requested", e + "_blocked"))
        case_list.append((statement, "{" + ",".join(subset) + "}"))
    case_list.append((Trueexp(), "DONE"))
    mod_dict_assign["next(event)"] = Case(tuple(case_list))
    mod_dict["ASSIGN"] = mod_dict_assign
    return type("main", (Module,), mod_dict)

if __name__ == "__main__":
    from hot_cold import *
    event_list = ["Start", "HOT", "COLD", "IDLE"]
    # bt_list = [
    #     bthread_to_module(add_a(), "adda", event_list),
    #     bthread_to_module(add_b(), "addb", event_list),
    #     bthread_to_module(control(), "control", event_list),
    # ]
    #print(main_module(event_list, bt_list))
    print(bthread_to_module(control, "control", event_list))

    # bt = bthread_to_module(add_a(), "add_a", event_list)
    # v = Var(bt(Var(Scalar(tuple(["START", "DONE"] + event_list)))))
    # print(v)
