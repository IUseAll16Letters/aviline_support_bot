from aiogram.fsm.state import StatesGroup, State


class BaseState(StatesGroup):
    select_service = State()


class PurchaseState(BaseState):
    select_product = State()
    product_description = State()


class ProductDetails(PurchaseState):
    price = State()
    versions = State()
    details = State()
    manual = State()


class TechSupportState(BaseState):
    select_product = State()
    product_problems = State()


class ContactSupportState(StatesGroup):
    enter_name = State()
    enter_contact = State()
    enter_message = State()


STATES = {}
