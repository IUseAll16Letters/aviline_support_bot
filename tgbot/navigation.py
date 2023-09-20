__all__ = ("Navigation", "template_from_state")

from typing import Optional, List
from aiogram.fsm.state import State

from tgbot.states import *


class Node:
    def __init__(self, state: Optional[State], pre: Optional["Node"] = None, next_: Optional[List["Node"]] = None):
        self.s = state
        self.prev = pre
        self.next = [] if next_ is None else next_
        if pre is not None:
            pre.next.append(self)

    def find(self, value: Optional[str]) -> "Node":

        def dfs(root: Node, v: str):
            if root == v:
                return root

            for node in root.next:
                res = dfs(node, v)
                if res is not None:
                    return res

        return dfs(self, value)

    def reverse_state(self, par: Optional[str] = None) -> Optional[State]:
        if self.s is None:
            return None

        if self.s is ContactSupportState.enter_name and par in ('purchase', 'support'):
            if par == 'purchase':
                return PurchaseState.product_description
            else:
                return TechSupportState.product_problems

        return self.prev.s

    def __eq__(self, other):
        if self.s is None:
            return self.s == other
        if isinstance(self.s, State):
            return self.s.state == other
        else:
            raise ValueError(f'Unsupported comparison for class Node, allowed {State} or {None}, '
                             f'got {self.__class__} and {other.__class__}')

    def __str__(self):
        return f"StateNode (state={str(self.s) if self.s is not None else None})"


def get_navigation() -> Node:
    start = Node(None)
    support = Node(TechSupportState.select_product, pre=start)
    problems = Node(TechSupportState.product_problems, pre=support)
    problem_detail = Node(TechSupportState.problem_details, pre=problems)

    purchase = Node(PurchaseState.select_product, pre=start)
    product_desc = Node(PurchaseState.product_description, pre=purchase)
    sub_product = ...

    enter_name = Node(ContactSupportState.enter_name)
    product_desc.next = [enter_name]
    problem_detail.next = [enter_name]

    enter_contact = Node(ContactSupportState.enter_contact, pre=enter_name)
    enter_message = Node(ContactSupportState.enter_message, pre=enter_contact)
    confirm = Node(ContactSupportState.entry_confirmation, pre=enter_message)

    return start


Navigation: Node = get_navigation()

template_from_state = {
    None: "start.html",
    PurchaseState.select_product: "products_list.html",
    PurchaseState.product_description: "product_description.html",
    TechSupportState.select_product: "products_list.html",
    TechSupportState.product_problems: "product_problems.html",
    TechSupportState.problem_details: "product_problem_solution.html",
    ContactSupportState.enter_name: "client_enter_name.html",
    ContactSupportState.enter_contact: "client_enter_contact.html",
    ContactSupportState.enter_message: "client_enter_message.html",
    ContactSupportState.entry_confirmation: "client_message_confirm.html",
}
