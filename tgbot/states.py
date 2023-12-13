from aiogram.fsm.state import StatesGroup, State


class PurchaseState(StatesGroup):
    select_product = State()
    select_sub_product = State()
    product_description = State()


class TechSupportState(StatesGroup):
    select_product = State()
    product_problems = State()
    problem_details = State()


class ContactSupportState(StatesGroup):
    confirm_policy = State()
    enter_name = State()
    enter_contact = State()
    enter_message = State()
    entry_confirmation = State()


class WarrantyState(StatesGroup):
    confirm_policy = State()
    describe_problem = State()
    where_when_buy = State()
    location = State()
    car_brand = State()
    confirm_entry = State()
    approval_docs_contact = State()
    confirm_mail_sending = State()
