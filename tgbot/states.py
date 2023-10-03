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
    problem_details = State()


class ContactSupportState(StatesGroup):
    enter_name = State()
    enter_contact = State()
    enter_message = State()
    entry_confirmation = State()


class WarrantyState(StatesGroup):
    describe_problem = State()
    where_when_buy = State()
    location = State()
    car_brand = State()
    confirm_entry = State()
    approval_docs_contact = State()
    confirm_mail_sending = State()
