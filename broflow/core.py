"""Core primitives for broflow's register pattern.

A flow is built from three pieces: BaseTask (one unit of work that decides its own
next step), TaskRegistry (a flat identifier -> task lookup), and Flow (runs a
registered flow from a start identifier to an end value). Tasks never hold
references to each other -- they only ever name where they're going, so nothing
needs to exist yet at the point a task decides its next step, and a flow can safely
loop back on itself.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseTask(ABC):
    """Base class for one step in a flow.

    Subclasses implement `__call__` to do the actual work and must call
    `set_next(...)` before returning, so `Flow.run` knows where to go next.

    Attributes:
        possible_next (set): Every identifier this task might route to. This is
            documentation only -- `Flow` never reads it -- but it lets
            `to_edges`/`to_tree`/`to_mermaid` draw the flow's possible shape without
            running anything. Keep it in sync with what `__call__` actually passes
            to `set_next`.
        name (str): Human-readable identifier for this task, recorded in
            `Flow.trace`.
        next_action (Any): The identifier `set_next` was last called with, or
            `None` before the task has ever run.
    """
    possible_next: set = set()

    def __init__(self, name):
        """Initializes BaseTask.

        Args:
            name (str): Human-readable name for this task, recorded in
                `Flow.trace`.
        """
        self.name = name
        self.next_action: Any = None

    def set_next(self, task: str) -> None:
        """Records which task should run next.

        Args:
            task (str): Identifier of the next task to run, matching a key
                registered in the `TaskRegistry` this task's flow uses.
        """
        self.next_action = task

    @property
    def next(self) -> Any:
        """Any: The identifier `set_next` was last called with."""
        return self.next_action

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        """Runs this task's work and calls `set_next(...)` before returning.

        Args:
            *args: Positional arguments, forwarded from `Flow.run`.
            **kwargs: Keyword arguments, forwarded from `Flow.run`.

        Returns:
            Any: Whatever this task produces. Becomes `Flow.run`'s return value
            if this is the task whose next step matches `end`.
        """
        ...


class TaskRegistry:
    """A flat identifier -> task lookup.

    Tasks are registered independently of each other, so nothing needs to already
    exist at the point a task's own logic decides where it will route next.
    """

    def __init__(self):
        """Initializes an empty TaskRegistry."""
        self._tasks: dict[Any, BaseTask] = {}

    def register(self, process: Any, task: BaseTask) -> None:
        """Registers a task under an identifier.

        Args:
            process (Any): Identifier this task will be looked up by (an enum
                member, a string, or any hashable value).
            task (BaseTask): The task instance to register.
        """
        self._tasks[process] = task

    def get(self, process: Any) -> BaseTask:
        """Looks up a registered task by identifier.

        Args:
            process (Any): Identifier the task was registered under.

        Returns:
            BaseTask: The task registered under `process`.

        Raises:
            KeyError: If nothing is registered under `process`.
        """
        return self._tasks[process]

    def items(self):
        """Returns every registered (identifier, task) pair.

        Returns:
            ItemsView[Any, BaseTask]: A view over every registered
            `(process, task)` pair.
        """
        return self._tasks.items()


class Flow:
    """Runs a registered flow from a start identifier to an end value.

    Flow doesn't know anything about the tasks it runs -- it just calls whatever's
    `current`, checks whether that was the terminal step, and looks up whatever
    `current` decided was next. Because nothing tracks predecessors, a task can
    route back to an earlier step (a retry, a multi-turn loop) safely.

    Attributes:
        registry (TaskRegistry): Lookup used to resolve each next step by
            identifier.
        trace (list[tuple[Any, Any]]): The real `(task_name, next)` pairs taken
            during the most recent `run()` call, reset at the start of every call.
    """

    def __init__(self, registry: TaskRegistry):
        """Initializes Flow.

        Args:
            registry (TaskRegistry): Lookup used to resolve each next step by
                identifier. Consider it a lookup for tasks.
        """
        self.registry = registry
        self.trace: list[tuple[Any, Any]] = []

    def run(self, start: Any, end: Any, show_trace: Optional[bool] = True, **kwargs) -> Any:
        """Executes tasks from the registry until reaching the end process.

        Args:
            start (Any): Identifier of the task to run first.
            end (Any): Identifier that stops the run once a task's `next_action`
                equals it.
            show_trace (bool, optional): If True, record each step taken in
                `self.trace`. Defaults to True.
            **kwargs: Forwarded to every task call as-is; a task that needs to see
                a previous step's output should read/write it through a shared
                mutable object passed in `kwargs`, since `kwargs` itself isn't
                reassigned between steps.

        Returns:
            Any: Whatever the task that reached `end` returned.
        """
        self.trace = []
        current = self.registry.get(start)
        while True:
            result = current(**kwargs)
            if show_trace:
                self.trace.append((current.name, current.next))
            if current.next == end:
                return result
            current = self.registry.get(current.next_action)
