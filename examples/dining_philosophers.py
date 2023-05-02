from bppy import BEvent, b_thread, waitFor, request, block, BProgram, PrintBProgramRunnerListener, \
    SimpleEventSelectionStrategy
data = "data"
PHILOSOPHER_COUNT = 2

any_take = dict([(i, [BEvent(f"T{i}R"), BEvent(f"T{(i + 1) % PHILOSOPHER_COUNT}L")]) for i in range(PHILOSOPHER_COUNT)])
any_put = dict([(i, [BEvent(f"P{i}R"), BEvent(f"P{(i + 1) % PHILOSOPHER_COUNT}L")]) for i in range(PHILOSOPHER_COUNT)])

all_events = [BEvent(f"T{i}R") for i in range(PHILOSOPHER_COUNT)] + \
             [BEvent(f"T{i}L") for i in range(PHILOSOPHER_COUNT)] + \
             [BEvent(f"P{i}R") for i in range(PHILOSOPHER_COUNT)] + \
             [BEvent(f"P{i}L") for i in range(PHILOSOPHER_COUNT)]

@b_thread
def philosopher(i):
    while True:
        for j in range(2):
            yield {request: [BEvent(f"T{i}R"), BEvent(f"T{i}L")], data: locals()}
        for j in range(2):
            yield {request: [BEvent(f"P{i}R"), BEvent(f"P{i}L")], data: locals()}


@b_thread
def fork(i):
    while True:
        yield {waitFor: any_take[i], block: any_put[i]}
        yield {waitFor: any_put[i], block: any_take[i]}



if __name__ == "__main__":
    bprog = BProgram(
        bthreads=[philosopher(i) for i in range(PHILOSOPHER_COUNT)] + [fork(i) for i in range(PHILOSOPHER_COUNT)],
        event_selection_strategy=SimpleEventSelectionStrategy(),
        listener=PrintBProgramRunnerListener())
    bprog.run()



