from dataclasses import dataclass, field
from enum import StrEnum

import pytest

from broflow import BaseTask, TaskRegistry


class Step(StrEnum):
    A = 'a'
    B = 'b'
    C = 'c'
    END = 'end'


@dataclass
class Ctx:
    log: list = field(default_factory=list)
    branch: str = 'end'  # 'end' -> B routes straight to END; 'c' -> B routes through C


class TaskA(BaseTask):
    possible_next = {Step.B}

    def __call__(self, ctx: Ctx):
        ctx.log.append('a')
        self.set_next(Step.B)
        return ctx


class TaskB(BaseTask):
    possible_next = {Step.C, Step.END}

    def __call__(self, ctx: Ctx):
        ctx.log.append('b')
        self.set_next(Step.C if ctx.branch == 'c' else Step.END)
        return ctx


class TaskC(BaseTask):
    possible_next = {Step.A, Step.END}  # declares a possible loop back to A

    def __call__(self, ctx: Ctx):
        ctx.log.append('c')
        self.set_next(Step.END)
        return ctx


@pytest.fixture
def registry() -> TaskRegistry:
    """A fresh 3-task registry (A -> B -> [C -> END] or END), new instance per test."""
    reg = TaskRegistry()
    reg.register(Step.A, TaskA(name='a'))
    reg.register(Step.B, TaskB(name='b'))
    reg.register(Step.C, TaskC(name='c'))
    return reg
