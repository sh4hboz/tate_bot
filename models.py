from pydantic import BaseModel


class User(BaseModel):
    id: int | None = None
    telegram_id: int | None = None
    balance: float | None = None
    inviter: int | None = None
    deposits: int | None = None
    withdrawals: float | None = None
    from_refs: float | None = None


class UserAuthorize(BaseModel):
    telegram_id: int | None = None


class SendTon(BaseModel):
    user_id: int | None = None
    wallet: str | None = None
    amount: float | None = None
    payload: str | None = "Tate"


class Item(BaseModel):
    id: int | None = None
    name: str | None = None
    price: float | None = None
    profitability: float | None = None
    complete_time: int | None = None
    description: str | None = None
    icon_path: str | None = None
    max_count: int | None = None


class UserItem(BaseModel):
    id: int | None = None
    user_id: int | None = None
    item_id: int | None = None
    telegram_id: int | None = None


class Additional(BaseModel):
    owner_wallet: int | None = None
    tax: float | None = None
    payment_time: int | None = None


class Payment(BaseModel):
    id: int | None = None
    telegram_id: int | None = None
    user_id: int | None = None
    wallet_address: str | None = None
    amount: float | None = None
    status: str | None = "In progress"


class Banned(BaseModel):
    id: int | None = None
    telegram_id: int | None = None
    user_id: int | None = None
