from __future__ import annotations

__all__ = ["to_ir"]

from functools import singledispatch
from typing import Literal, TypedDict, cast
from camel.dsl import Action, AddAction, Condition, Elem, Empty, Event, Fragment, If, State, StateRef, Value

# See docs/ir.md
type IRNode = ElemIR | FragmentIR | TextIR | StateIR | StateRefIR | EmptyIR | IfIR

type ValueIR = LiteralIR | StateRefIR


class ElemIR(TypedDict):
    type: Literal["Elem"]
    tag: str
    classes: tuple[str, ...]
    children: tuple[IRNode, ...]
    events: tuple[EventIR, ...]


class FragmentIR(TypedDict):
    type: Literal["Fragment"]
    children: tuple[IRNode, ...]


class EmptyIR(TypedDict):
    type: Literal["Empty"]


class TextIR(TypedDict):
    type: Literal["Text"]
    contents: str


class StateIR(TypedDict):
    type: Literal["State"]
    initial: dict[str, int | str]
    child: IRNode


class StateRefIR(TypedDict):
    type: Literal["StateRef"]
    name: str


class IfIR(TypedDict):
    type: Literal["If"]
    condition: ConditionIR
    then: IRNode
    otherwise: IRNode


class ConditionIR(TypedDict):
    type: Literal["Condition"]
    op: Literal["Eq"]  # "Gt", ...
    left: ValueIR
    right: ValueIR


class LiteralIR(TypedDict):
    type: Literal["Literal"]
    value: int | str


class EventIR(TypedDict):
    name: str
    actions: tuple[ActionIR, ...]


type ActionIR = AddActionIR  # | ...


class AddActionIR(TypedDict):
    type: Literal["Action"]
    name: str
    target: StateRefIR
    amount: ValueIR


@singledispatch
def to_ir(node) -> IRNode:
    raise TypeError(f"don't know how to compile {type(node)!r}")


@to_ir.register
def _(elem: Elem) -> ElemIR:
    return {
        "type": "Elem",
        "tag": elem.tag,
        "classes": elem.classes,
        "children": tuple(map(to_ir, elem.children)),
        "events": tuple(map(_event_to_ir, elem.events))
    }


@to_ir.register
def _(fragment: Fragment) -> FragmentIR:
    return {
        "type": "Fragment",
        "children": tuple(map(to_ir, fragment.children)),
    }


@to_ir.register
def _(empty: Empty) -> EmptyIR:
    return {"type": "Empty"}


@to_ir.register
def _(node: str) -> TextIR:
    return {"type": "Text", "contents": node}


@to_ir.register
def _(state: State) -> StateIR:
    return {
        "type": "State",
        "initial": dict(state.initial),
        "child": to_ir(state.child),
    }


@to_ir.register
def _(state_ref: StateRef) -> StateRefIR:
    return {"type": "StateRef", "name": state_ref.name}


@to_ir.register
def _(if_: If) -> IfIR:
    return {
        "type": "If",
        "condition": _condition_to_ir(if_.condition),
        "then": to_ir(if_.then),
        "otherwise": to_ir(if_.otherwise_),
    }


def _condition_to_ir(condition: Condition) -> ConditionIR:
    return {
        "type": "Condition",
        "op": condition.op,
        "left": _value_to_ir(condition.left),
        "right": _value_to_ir(condition.right),
    }


def _value_to_ir(value: Value) -> LiteralIR | StateRefIR:
    if isinstance(value, StateRef):
        return cast(StateRefIR, to_ir(value))
    return {"type": "Literal", "value": value}


def _event_to_ir(event: Event) -> EventIR:
    return {
        "name": event.name,
        "actions": tuple(map(_action_to_ir, event.actions))
    }


@singledispatch
def _action_to_ir(action: Action) -> ActionIR:
    raise TypeError(f"don't know how to compile {type(action)!r}")


@_action_to_ir.register
def _(action: AddAction) -> AddActionIR:
    return {
        "type": "Action",
        "name": "Add",
        "target": cast(StateRefIR, to_ir(action.target)),
        "amount": _value_to_ir(action.amount),
    }
