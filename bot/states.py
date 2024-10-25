from aiogram.fsm.state import StatesGroup, State


class PostStates(StatesGroup):
    wait_name = State()
    wait_photo = State()
    wait_price = State()
    wait_discount = State()
    wait_marketplace = State()
    wait_url_account = State()
    wait_channel = State()
    wait_product_search = State()


class DeletePost(StatesGroup):
    wait_url_post = State()


class States(StatesGroup):
    wait_telegram_admin = State()
    wait_username_admin_block = State()
    wait_username = State()
    wait_telegram_block = State()
    wait_username_unlock = State()
    wait_delete_coins = State()


class SetPull(StatesGroup):
    wait_farming = State()
    wait_task = State()
    wait_friends = State()
    wait_plan = State()
    wait_coins = State()


class StatesUserActions(StatesGroup):
    wait_username = State()
    wait_username_block = State()
    wait_username_unlock = State()


class PostStatesDelete(StatesGroup):
    wait_url = State()


class TaskStates(StatesGroup):
    wait_descript = State()
    wait_url = State()
    wait_date = State()
    wait_url_delete = State()
    wait_reward = State()


class LiquidStates(StatesGroup):
    wait_free = State()
    wait_coins = State()
    wait_money = State()
    wait_token = State()
    wait_stars = State()