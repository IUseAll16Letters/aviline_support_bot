from tgbot.navigation import Navigation
from tgbot.states import *


def test_navigation_dfs():
    test_cases = [
        ContactSupportState.entry_confirmation,
        None
    ]
    for case in test_cases:
        res = Navigation.find(case).s
        assert res is case, f"expected: {case}, got: {res} instead."


def test_reverse():
    states = [
        (None, None, None),
        (PurchaseState.select_product, None, None),
        (TechSupportState.select_product, None, None),
        (PurchaseState.product_description, PurchaseState.select_product, None),
        (TechSupportState.product_problems, TechSupportState.select_product, None),
        (ContactSupportState.enter_name, TechSupportState.product_problems, "support"),
        (ContactSupportState.enter_name, PurchaseState.product_description, "purchase"),
        (ContactSupportState.entry_confirmation, ContactSupportState.enter_message, None),
    ]

    for test_case in states:
        current, expected, par = test_case
        res = Navigation.find(current)
        res = res.reverse_state(par=par)
        assert res is expected, f"\ncurrent: {current},\ngot: {res},\nexpected: {expected}"


test_navigation_dfs()
test_reverse()
