__all__ = ("Navigation", "template_from_state")

import logging
from typing import Optional, List

from tgbot.states import PurchaseState, ContactSupportState, WarrantyState, TechSupportState
from aiogram.fsm.state import State
from tgbot.logging_config.setup_logger import navigation

navigation.setLevel(logging.DEBUG)


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

        res_node = dfs(self, value)
        msg = f"searching: {value}, found: {res_node}"
        navigation.info(msg=msg)
        return res_node

    def reverse_state(self, par: Optional[str] = None) -> Optional[State]:
        if self.s is None:
            return None

        if self.s is ContactSupportState.confirm_policy:
            if par == 'purchase':
                return PurchaseState.product_description
            elif par == 'support':
                return TechSupportState.product_problems
            else:
                return None
        msg = f"reversing from {self.s}"
        navigation.info(msg=msg)
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
        return f"StateNode (state={str(self.s) if self.s is not None else str(None)})"


def get_navigation() -> Node:
    start = Node(None)
    support = Node(TechSupportState.select_product, pre=start)
    problems = Node(TechSupportState.product_problems, pre=support)
    problem_detail = Node(TechSupportState.problem_details, pre=problems)

    purchase = Node(PurchaseState.select_product, pre=start)
    sub_product = Node(PurchaseState.select_sub_product, pre=purchase)
    product_desc = Node(PurchaseState.product_description, pre=purchase)

    warranty_confirm_policy = Node(WarrantyState.confirm_policy, pre=start)
    warranty_describe = Node(WarrantyState.describe_problem, pre=start)
    warranty_where_when = Node(WarrantyState.where_when_buy, pre=warranty_describe)
    warranty_city = Node(WarrantyState.location, pre=warranty_where_when)
    warranty_car = Node(WarrantyState.car_brand, pre=warranty_city)
    warranty_confirm = Node(WarrantyState.confirm_entry, pre=warranty_car)
    warranty_attach = Node(WarrantyState.approval_docs_contact, pre=warranty_confirm)

    confirm_policy = Node(ContactSupportState.confirm_policy)
    product_desc.next = [confirm_policy]
    sub_product.next = [confirm_policy]
    problem_detail.next = [confirm_policy]

    enter_name = Node(ContactSupportState.enter_name, pre=confirm_policy)
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
    ContactSupportState.confirm_policy: "privacy_policy.html",
    ContactSupportState.enter_name: "client_enter_name.html",
    ContactSupportState.enter_contact: "client_enter_contact.html",
    ContactSupportState.enter_message: "client_enter_message.html",
    ContactSupportState.entry_confirmation: "client_message_confirm.html",
    WarrantyState.confirm_policy: 'privacy_policy.html',
    WarrantyState.describe_problem: 'warranty_describe_problem.html',
    WarrantyState.where_when_buy: 'warranty_where_when_buy.html',
    WarrantyState.location: 'warranty_location.html',
    WarrantyState.car_brand: 'warranty_client_car.html',
    WarrantyState.confirm_entry: 'warranty_confirm_entry.html',
    WarrantyState.approval_docs_contact: 'warranty_enter_approval_docs.html',
}
