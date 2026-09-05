"""Visualization helpers for broflow's register pattern (broflow.core).

`to_edges` / `to_tree` / `to_mermaid` answer "what COULD this flow do" -- built from
each task's `possible_next`, which is documentation only and can drift from reality.

For "what DID this run actually do", no helper is needed here -- `Flow` itself records
it: after `flow.run(...)`, read `flow.trace` for the real `(task_name, next)` sequence
taken.
"""
from typing import Any, Callable
from broflow.core import TaskRegistry


def to_edges(registry: TaskRegistry) -> list[tuple[Any, Any]]:
    """Flattens a registry into a sorted list of every possible (from, to) edge.

    Unlike `to_tree`/`to_mermaid`, this doesn't walk from a start -- it lists every
    task's declared `possible_next` directly, so it also surfaces edges from tasks
    that aren't currently reachable from wherever a flow actually starts. Meant to
    be diffed in git or asserted on in a test, not read as a picture.

    Args:
        registry (TaskRegistry): Registry to read every task's `possible_next` from.

    Returns:
        list[tuple[Any, Any]]: Sorted `(from, to)` pairs, one per declared edge,
        with both sides converted to `str` for stable, readable output.
    """
    return sorted(
        (str(process), str(nxt))
        for process, task in registry.items()
        for nxt in task.possible_next
    )


def to_tree(registry: TaskRegistry, start: Any, terminate: Any) -> str:
    """Renders a flow's possible shape as a plain indented text tree.

    No rendering dependency -- readable directly in any terminal or log.

    Args:
        registry (TaskRegistry): Registry to resolve each identifier's task from.
        start (Any): Identifier to start walking from.
        terminate (Any): Identifier that stops the walk -- reaching it renders as
            a leaf, never expanded further.

    Returns:
        str: The tree, as one newline-joined string, `start` on the first line
        and each `possible_next` edge indented one level deeper than its source.
    """
    lines = [str(start)]

    def visit(_process: Any, nxt: Any, depth: int) -> None:
        lines.append("  " * (depth + 1) + f"-> {nxt}")

    _walk(registry, start, terminate, visit)
    return "\n".join(lines)


def to_mermaid(registry: TaskRegistry, start: Any, terminate: Any) -> str:
    """Renders a flow's possible shape as Mermaid flowchart text.

    A task with more than one `possible_next` is a live branch point -- only one
    of its edges actually fires on any given run -- so those edges are drawn
    dashed (`-.->`) to set them apart from a task with exactly one path, drawn
    solid (`-->`).

    Args:
        registry (TaskRegistry): Registry to resolve each identifier's task from.
        start (Any): Identifier to start walking from.
        terminate (Any): Identifier that stops the walk -- reaching it renders as
            a leaf, never expanded further.

    Returns:
        str: A ```` ```mermaid ```` fenced `flowchart TD` block, ready to paste
        anywhere Mermaid is rendered.
    """
    lines = ["```mermaid", "flowchart TD"]

    def visit(process: Any, nxt: Any, _depth: int) -> None:
        task = registry.get(process)
        arrow = "-.->" if len(task.possible_next) > 1 else "-->"
        lines.append(f"    {process} {arrow} {nxt}")

    _walk(registry, start, terminate, visit)
    lines.append("```")
    return "\n".join(lines)


def _walk(
    registry: TaskRegistry,
    start: Any,
    terminate: Any,
    visit: Callable[[Any, Any, int], None],
) -> None:
    """Depth-first walks a registry's possible_next edges, safe for cycles.

    An edge into an already-visited node is still passed to `visit` once, but
    that node's own children are only ever expanded the first time it's reached
    -- otherwise a loop like `Answer -> Input` would recurse forever.

    Args:
        registry (TaskRegistry): Registry to resolve each identifier's task from.
        start (Any): Identifier to start walking from.
        terminate (Any): Identifier that stops the walk -- reaching it is treated
            as a leaf and never expanded.
        visit (Callable[[Any, Any, int], None]): Called once per edge as
            `visit(process, nxt, depth)`, where `process` is the edge's source
            identifier, `nxt` is its target, and `depth` is how many edges deep
            `process` is from `start`.
    """
    visited: set = set()

    def go(process: Any, depth: int = 0) -> None:
        if process in visited or process == terminate:
            return
        visited.add(process)
        task = registry.get(process)
        for nxt in sorted(task.possible_next, key=str):
            visit(process, nxt, depth)
            go(nxt, depth + 1)

    go(start)
