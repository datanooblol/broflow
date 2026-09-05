from conftest import Step

from broflow import to_edges, to_mermaid, to_tree


def test_to_edges_is_flat_sorted_and_stringified(registry):
    assert to_edges(registry) == [
        ('a', 'b'),
        ('b', 'c'),
        ('b', 'end'),
        ('c', 'a'),
        ('c', 'end'),
    ]


def test_to_tree_renders_the_indented_shape(registry):
    tree = to_tree(registry, start=Step.A, terminate=Step.END)

    assert tree == (
        "a\n"
        "  -> b\n"
        "    -> c\n"
        "      -> a\n"
        "      -> end\n"
        "    -> end"
    )


def test_to_mermaid_dashes_only_branch_points(registry):
    diagram = to_mermaid(registry, start=Step.A, terminate=Step.END)

    assert diagram == (
        "```mermaid\n"
        "flowchart TD\n"
        "    a --> b\n"
        "    b -.-> c\n"
        "    c -.-> a\n"
        "    c -.-> end\n"
        "    b -.-> end\n"
        "```"
    )


def test_walkers_terminate_on_a_cyclic_registry(registry):
    """C's possible_next includes Step.A, a back-edge -- both walkers must still
    terminate instead of recursing forever."""
    to_tree(registry, start=Step.A, terminate=Step.END)
    to_mermaid(registry, start=Step.A, terminate=Step.END)


def test_to_edges_includes_unreachable_tasks():
    """Unlike to_tree/to_mermaid, to_edges doesn't walk from a start -- it lists
    every registered task's possible_next regardless of reachability."""
    from broflow import BaseTask, TaskRegistry

    class Orphan(BaseTask):
        possible_next = {"nowhere"}
        def __call__(self, *args, **kwargs): ...

    reg = TaskRegistry()
    reg.register("orphan", Orphan(name="orphan"))

    assert to_edges(reg) == [("orphan", "nowhere")]
