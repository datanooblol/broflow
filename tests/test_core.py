import pytest
from conftest import Ctx, Step

from broflow import BaseTask, Flow, TaskRegistry


def test_base_task_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        BaseTask(name="x")


def test_set_next_updates_next_and_next_action():
    class Noop(BaseTask):
        def __call__(self, *args, **kwargs):
            self.set_next("done")

    task = Noop(name="noop")
    assert task.next is None
    assert task.next_action is None

    task()
    assert task.next == "done"
    assert task.next_action == "done"


def test_registry_get_returns_the_registered_instance():
    class Noop(BaseTask):
        def __call__(self, *args, **kwargs): ...

    reg = TaskRegistry()
    task = Noop(name="x")
    reg.register("x", task)

    assert reg.get("x") is task


def test_registry_get_missing_identifier_raises_keyerror():
    reg = TaskRegistry()
    with pytest.raises(KeyError):
        reg.get("missing")


def test_registry_items_returns_every_registered_pair():
    class Noop(BaseTask):
        def __call__(self, *args, **kwargs): ...

    reg = TaskRegistry()
    one, two = Noop(name="1"), Noop(name="2")
    reg.register("one", one)
    reg.register("two", two)

    assert dict(reg.items()) == {"one": one, "two": two}


def test_flow_runs_the_default_linear_path(registry):
    flow = Flow(registry)
    result = flow.run(start=Step.A, end=Step.END, ctx=Ctx(branch='end'))

    assert result.log == ['a', 'b']


def test_flow_follows_a_live_branch_decision(registry):
    flow = Flow(registry)
    result = flow.run(start=Step.A, end=Step.END, ctx=Ctx(branch='c'))

    assert result.log == ['a', 'b', 'c']


def test_flow_trace_records_the_actual_path_taken(registry):
    flow = Flow(registry)
    flow.run(start=Step.A, end=Step.END, ctx=Ctx(branch='c'))

    assert flow.trace == [('a', Step.B), ('b', Step.C), ('c', Step.END)]


def test_flow_trace_resets_on_each_run_instead_of_accumulating(registry):
    flow = Flow(registry)
    flow.run(start=Step.A, end=Step.END, ctx=Ctx(branch='c'))
    assert len(flow.trace) == 3

    flow.run(start=Step.A, end=Step.END, ctx=Ctx(branch='end'))
    assert flow.trace == [('a', Step.B), ('b', Step.END)]


def test_flow_show_trace_false_leaves_trace_empty(registry):
    flow = Flow(registry)
    flow.run(start=Step.A, end=Step.END, show_trace=False, ctx=Ctx(branch='c'))

    assert flow.trace == []


def test_flow_can_loop_back_to_an_earlier_step(registry):
    """C routing back to A (its declared possible_next includes Step.A) must be
    safe -- Flow tracks no predecessors, so nothing deadlocks or refuses to re-run
    a step, unlike a join-based DAG model would."""

    class LoopingC(BaseTask):
        possible_next = {Step.A, Step.END}

        def __call__(self, ctx: Ctx):
            ctx.log.append('c')
            ctx.loops = getattr(ctx, 'loops', 0) + 1
            self.set_next(Step.A if ctx.loops < 2 else Step.END)
            return ctx

    registry.register(Step.C, LoopingC(name='c'))
    flow = Flow(registry)
    result = flow.run(start=Step.A, end=Step.END, ctx=Ctx(branch='c'))

    assert result.log == ['a', 'b', 'c', 'a', 'b', 'c']


def test_flow_forwards_kwargs_to_every_task_unchanged(registry):
    """Flow.run doesn't thread a return value between steps -- state only carries
    forward if it's a shared mutable object passed through kwargs and mutated in
    place, which is exactly what `ctx` is here."""
    flow = Flow(registry)
    ctx = Ctx(branch='end')

    returned = flow.run(start=Step.A, end=Step.END, ctx=ctx)

    assert returned is ctx
    assert ctx.log == ['a', 'b']
