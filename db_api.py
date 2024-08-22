import datetime

from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from fastapi import FastAPI, Request, Depends
from models import *
import db
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ton_api import check_ton_wallet
# from ton import send_ton
import httpx
import base64

tags_metadata=[
    {
        "name": "authorize",
        "description": "Принимает telegram id  если данного пользователя нет,"
                       "то создает и возвращает id пользователя из "
                       "базы данные Users"
    },
    {
        "name": "check_payment",
        "description": "Принимает: кошелёк пользователя. Проверяет "
                       "получена ли оплата от пользователя если получена "
                       "возвращает: payment receive и изменяет баланс у пользователя добавляя в таблицу "
                       "payments информацию об операции"
                       "иначе: payment don't receive"
    },
    {
        "name": "send_ton_to_client",
        "description": "Принимает: user_id, ton coin wallet"
                       ", количество"
                       "payload сообщение которое пользователь получит в кошельке. "
                       "Если всё успешно то вернёт status ok,"
                       "иначе вернёт ошибку. Изменяет баланс у пользователя и вносит "
                       "изменения в таблицу payments to users"
    },
    {
        "name": "get_wallet_for_receive",
        "description": "Возвращает кошелёк для оплаты пользователю"
    },
    {
        "name": "get_payments_to_users",
        "description": "Возвращает таблицу payments to users"
    }
]


app = FastAPI(
    title="BD",
    version="1.0",
    openapi_tags=tags_metadata
)
templates = Jinja2Templates(directory="ton_game")
app.mount("/assets", StaticFiles(directory="ton_game/assets"), name="assets")

Token = "q6AUI7RYhksYMQ2HbhDDBA6pA16HS4l4YGYbgvn/OfKXyuEjfPPTMlb?BNC-?NWbC168ne0r8=zDWmAPHe3ogFQdNimC4UfVhK?L41wqn1D?2qOZn2YntAf=JTUG5gg=949v697L-DD5aU9Zm1peZDQ!QPLq1lNOLUPC?BPGe4hsK=ClQw!6Gvv7uhPZNWUUaIJDYS?oA/Eq6k!EcK8u-TE3X8jAyPxc4gnywT24LSAu2GStTkc/1BvkukuKC85x"
encoded_token = base64.urlsafe_b64encode(Token.encode())

# print("Encoded token:", encoded_token)

# Enter wallet for receiving
owner_wallet = "EQDftQdPITnb-x8-gj3f15dtpQbn94F1yYxiftLoQPeGBizQ"


status_ok = {"status": "ok"}
status_error = {"status":  "error"}
status_invalid_token = {"status": "error", "error": "Invalid token"}


async def get_user_on_id(id=None, telegram_id=None, session=None):
    if id:
        user = select(db.Users).filter(db.Users.id == id)
        user = await session.execute(user)
        try:
            user = user.scalars().one()
            return user
        except Exception as e:
            print(e)
            return None
    elif telegram_id:
        user = select(db.Users).filter(db.Users.telegram_id == telegram_id)
        user = await session.execute(user)
        try:
            user = user.scalars().one()
            return user
        except Exception as e:
            print(e)
            return None
    else:
        return None


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    async with httpx.AsyncClient() as client:

        items_response = await client.get(
            "http://127.0.0.1:8000/get_user_items",
            params={"user_id": 1},
            headers={"Token": Token}
        )
        items_data = items_response.json().get('items', [])


        full_items_data = []
        for item in items_data:
            item_id = item['item_id']
            item_response = await client.get(
                "http://127.0.0.1:8000/get_item",
                params={"item_id": item_id},
                headers={"Token": Token}
            )
            item_data = item_response.json()
            if item_data.get('status') == 'ok':
                full_items_data.append(item_data)


        user_response = await client.get(
            "http://127.0.0.1:8000/get_user",
            params={"user_id": 1},
            headers={"Token": Token}
        )
        user_data = user_response.json()


        items_response = await client.get(
            "http://127.0.0.1:8000/get_items",
            headers={"Token": Token}
        )
        markets_list = items_response.json().get('items', [])

    return templates.TemplateResponse("index.html", {
        "request": request,
        "items": full_items_data,
        "user": user_data,
        "markets_list": markets_list
    })



@app.post("/add_user")
async def add_user(user: User, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_user = db.Users(telegram_id=user.telegram_id,
                               balance=user.balance,
                               inviter=user.inviter,
                               deposits=user.deposits if user.deposits else 0)
            session.add(db_user)
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/authorize", tags=["authorize"])
async def authorize(user: UserAuthorize, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        user_id = await get_user_on_id(id=None, telegram_id=user.telegram_id, session=session)
        if user_id:
            return user_id.id
        else:
            try:
                db_user = db.Users(telegram_id=user.telegram_id)
                session.add(db_user)
                await session.commit()
                user_id = await get_user_on_id(id=None, telegram_id=user.telegram_id, session=session)
                if user_id:
                    return user_id.id
            except Exception as e:
                return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/check_payment", tags=["check_payment"])
async def check_payment(payment: Payment, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        db_t = await get_user_on_id(id=payment.user_id, session=session)
        if not db_t:
            return {"status": "error", "error": "user not found"}
        res = await check_ton_wallet(owner_wallet, payment.wallet_address, payment.amount)
        if res["status"] == "success":
            try:
                db_payment = db.Paymets(user_id=payment.user_id,
                                        amount=payment.amount,
                                        wallet_address=payment.wallet_address,
                                        auto_complete_time=datetime.datetime.now(),
                                        status="Complete"
                                        )
                session.add(db_payment)
                db_user = await get_user_on_id(id=payment.user_id, session=session)
                db_user.balance = db_user.balance + payment.amount
                await session.commit()
            except Exception as e:
                return {"status": "error", "error": str(e)}

        return res
    else:
        return status_invalid_token


# @app.post("/send_ton_to_client", tags=["send_ton_to_client"])
# async def send_ton_api(send: SendTon, request: Request, session: AsyncSession = Depends(db.get_async_session)):
#     if request.headers['Token'] == Token:
#         db_user = await get_user_on_id(id=send.user_id, session=session)
#         if not db_user:
#             return {"status": "error", "error": "user not found"}
#         try:
#             needed_balance = send.amount * 105 / 100
#             print(needed_balance)
#             if not db_user.balance >= needed_balance:
#                 return {"status": "error", "error": f"the user doesn't have that much money, user_id: {send.user_id}"}
#             else:
#                 res = await send_ton(address_client=send.wallet, amount=send.amount)
#                 if res["status"] == "success":
#                     db_paymentsToUsers = db.PaymentsToUsers(user_id=send.user_id,
#                                                             user_wallet=send.wallet,
#                                                             amount_ton=send.amount,
#                                                             tax_service=needed_balance - send.amount,
#                                                             complete_time=datetime.datetime.now())
#                     session.add(db_paymentsToUsers)
#                     db_user.balance -= needed_balance
#                     await session.commit()
#                     return status_ok
#                 else:
#                     return res
#         except Exception as e:
#             return {"status": "error", "error": str(e)}

#     else:
#         return status_invalid_token


@app.get("/get_wallet_for_receive", tags=["get_wallet_for_receive"])
async def get_wallet_for_receive(request: Request):
    if request.headers['Token'] == Token:
        return {"wallet": owner_wallet}
    else:
        return status_invalid_token


@app.get("/get_payments_to_users", tags=["get_payments_to_users"])
async def get_payments_to_users(request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            payments = select(db.PaymentsToUsers)
            payments = await session.execute(payments)
            payments = payments.scalars()
            return {**status_ok,
                    **{
                        "Payments to users": [{
                            "id": payment.id,
                            "user_id": payment.user_id,
                            "user_wallet": payment.user_wallet,
                            "amount_ton": payment.amount_ton,
                            "tax_service": payment.tax_service,
                            "complete_time": payment.complete_time}
                            for payment in payments]
                    }}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.get("/get_user")
async def get_user(user_id: int = 0, telegram_id: int = 0, request: Request = None,
                   session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        if not (user_id or telegram_id):
            return {"status": "error", "error": "Нет не телеграмм айди не обычного"}
        try:
            db_user = await get_user_on_id(id=user_id, telegram_id=telegram_id, session=session)

            if not db_user:
                return status_error

            return {**status_ok,
                    **{
                        "id": db_user.id,
                        "telegram_id": db_user.telegram_id,
                        "balance": db_user.balance,
                        "inviter": db_user.inviter,
                        "deposits": db_user.deposits,
                        "withdrawals": db_user.withdrawals,
                        "from_refs": db_user.from_refs
                    }
                    }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/delete_user")
async def delete_user(user: User, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        if not (user.id or user.telegram_id):
            return {"status": "error", "error": "Нет не телеграмм айди не обычного"}
        try:
            db_user = await get_user_on_id(id=user.id, telegram_id=user.telegram_id, session=session)
            if not db_user:
                return status_error
            await session.delete(db_user)
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/change_user")
async def change_user(user: User, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        if not (user.id or user.telegram_id):
            return {"status": "error", "error": "Нет не телеграмм айди не обычного"}
        try:
            db_user = await get_user_on_id(id=user.id, telegram_id=user.telegram_id, session=session)
            if not db_user:
                return status_error
            if user.balance: db_user.balance = user.balance
            if user.inviter: db_user.inviter = user.inviter
            if user.deposits: db_user.deposits = user.deposits
            if user.from_refs: db_user.from_refs = user.from_refs
            if user.withdrawals: db_user.withdrawals = user.withdrawals
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.get("/get_users")
async def get_users(request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            users = select(db.Users)
            users = await session.execute(users)
            users = users.scalars()
            return {**status_ok,
                    **{
                        "users": [{
                            "id": user.id,
                            "telegram_id": user.telegram_id,
                            "balance": user.balance,
                            "inviter": user.inviter,
                            "deposits": user.deposits,
                            "withdrawals": user.withdrawals,
                            "from_refs": user.from_refs}
                            for user in users]
                    }}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/add_item")
async def add_item(item: Item, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_item = db.Items(
                name=item.name,
                price=item.price,
                profitability=item.profitability,
                complete_time=item.complete_time,
                description=item.description,
                icon_path=item.icon_path,
                max_count=item.max_count,
            )
            session.add(db_item)
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/delete_item")
async def delete_item(item: Item, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            if item.id:
                db_item = select(db.Items).filter(db.Items.id == item.id)
                db_item = await session.execute(db_item)
                db_item = db_item.scalars().one()
            else:
                return status_error

            if not db_item:
                return status_error

            await session.delete(db_item)
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/change_item")
async def change_item(item: Item, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            if item.id:
                db_item = select(db.Items).filter(db.Items.id == item.id)
                db_item = await session.execute(db_item)
                db_item = db_item.scalars().one()
            else:
                return status_error
            if not db_item:
                return status_error

            if item.price: db_item.price = item.price
            if item.name: db_item.name = item.name
            if item.profitability: db_item.profitability = item.profitability
            if item.complete_time: db_item.complete_time = item.complete_time
            if item.description: db_item.description = item.description
            if item.icon_path: db_item.icon_path = item.icon_path
            if item.max_count: db_item.max_count = item.max_count
            await session.commit()

            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.get("/get_item")
async def get_item(item_id: int, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            if item_id:
                db_item = select(db.Items).filter(db.Items.id == item_id)
                db_item = await session.execute(db_item)
                db_item = db_item.scalars().one()
            else:
                return status_error
            if not db_item:
                return status_error

            return {**status_ok,
                    **{
                        "id": db_item.id,
                        "price": db_item.price,
                        "name": db_item.name,
                        "profitability": db_item.profitability,
                        "complete_time": db_item.complete_time,
                        "description": db_item.description,
                        "icon_path": db_item.icon_path,
                        "max_count": db_item.max_count
                    }}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.get("/get_items")
async def get_items(request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_items = select(db.Items)
            db_items = await session.execute(db_items)
            db_items = db_items.scalars()
            if not db_items:
                return status_error

            return {**status_ok,
                    **{"items": [{
                        "id": db_item.id,
                        "price": db_item.price,
                        "name": db_item.name,
                        "profitability": db_item.profitability,
                        "complete_time": db_item.complete_time,
                        "description": db_item.description,
                        "icon_path": db_item.icon_path,
                        "max_count": db_item.max_count
                    } for db_item in db_items]}}

        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/add_user_item")
async def add_user_item(item: UserItem, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            if item.item_id:
                db_item = select(db.Items).filter(db.Items.id == item.item_id)
                db_item = await session.execute(db_item)
                db_item = db_item.scalars().one()
            else:
                return status_error
            if not db_item:
                return status_error

            complete_time = datetime.datetime.now() + datetime.timedelta(hours=db_item.complete_time)
            db_user = await get_user_on_id(id=item.user_id, telegram_id=item.telegram_id, session=session)
            if not db_user:
                return status_error

            db_user_item = db.UserItems(user_id=db_user.id, item_id=item.item_id, complete_time=complete_time)

            session.add(db_user_item)
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.get("/get_user_items")
async def get_user_items(user_id: int = 0, telegram_id: int = 0, request: Request = None,
                         session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_user = await get_user_on_id(id=user_id, telegram_id=telegram_id, session=session)
            if not db_user:
                return status_error
            db_user_items = select(db.UserItems).filter(db.UserItems.user_id == db_user.id)
            db_user_items = await session.execute(db_user_items)
            db_user_items = db_user_items.scalars()
            return {**status_ok,
                    **{
                        "items": [{
                            "id": user_item.id,
                            "user_id": user_item.user_id,
                            "item_id": user_item.item_id,
                            "complete_time": user_item.complete_time
                        } for user_item in db_user_items]
                    }
                    }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/delete_user_item")
async def delete_user_item(item: UserItem, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            if item.id:
                db_item = select(db.UserItems).filter(db.UserItems.id == item.id)
                db_item = await session.execute(db_item)
                db_item = db_item.scalars().one()
            else:
                return status_error
            if not db_item:
                return status_error
            await session.delete(db_item)
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/create_add_data")
async def create_add_data(data: Additional, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            data = db.AdditionalData(
                owner_wallet=data.owner_wallet,
                tax=data.tax,
                payment_auto_complete_time=data.payment_time,
            )
            session.add(data)
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/change_add_data")
async def change_add_data(data: Additional, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_data = select(db.AdditionalData)
            db_data = await session.execute(db_data)
            db_data = db_data.scalars().one()
            if not db_data:
                return status_error
            if data.owner_wallet: db_data.owner_wallet = data.owner_wallet
            if data.tax: db_data.tax = data.tax
            if data.payment_time: db_data.payment_auto_complete_time = data.payment_time
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.get("/get_add_data")
async def get_add_data(request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_data = select(db.AdditionalData)
            db_data = await session.execute(db_data)
            db_data = db_data.scalars().one()
            if not db_data:
                return status_error
            return {**status_ok, **{
                "owner_wallet": db_data.owner_wallet,
                "tax": db_data.tax,
                "payment_auto_complete_time": db_data.payment_auto_complete_time
            }}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/add_payment")
async def add_payment(payment: Payment, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_user = await get_user_on_id(id=payment.user_id, telegram_id=payment.telegram_id, session=session)
            db_data = select(db.AdditionalData)
            db_data = await session.execute(db_data)
            db_data = db_data.scalars().one()
            if not db_data:
                return status_error
            auto_time = db_data.payment_auto_complete_time
            payment = db.Paymets(user_id=db_user.id,
                                 amount=payment.amount,
                                 wallet_address=payment.wallet_address,
                                 status=payment.status,
                                 auto_complete_time=datetime.datetime.now() + datetime.timedelta(hours=auto_time))
            session.add(payment)
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.get("/get_user_payments")
async def get_user_payments(user_id: int = 0, telegram_id: int = 0, request: Request = None,
                            session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_user = await get_user_on_id(id=user_id, telegram_id=telegram_id, session=session)
            if not db_user:
                return status_error

            db_payments = select(db.Paymets).filter(db.Paymets.user_id == db_user.id)
            db_payments = await session.execute(db_payments)
            db_payments = db_payments.scalars()

            return {**status_ok, **{"payments": [
                {
                    "id": payment.id,
                    "user_id": payment.user_id,
                    "amount": payment.amount,
                    "wallet_address": payment.wallet_address,
                    "pstatus": payment.status,
                    "auto_complete_time": payment.auto_complete_time
                } for payment in db_payments]}}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.get("/get_payments")
async def get_payments(request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_payments = select(db.Paymets)
            db_payments = await session.execute(db_payments)
            db_payments = db_payments.scalars()
            if not db_payments:
                db_payments = []

            return {**status_ok, **{"payments": [
                {
                    "id": payment.id,
                    "user_id": payment.user_id,
                    "amount": payment.amount,
                    "wallet_address": payment.wallet_address,
                    "pstatus": payment.status,
                    "auto_complete_time": payment.auto_complete_time
                } for payment in db_payments]}}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/delete_payment")
async def delete_payment(payment: Payment, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_payment = select(db.Paymets).filter(db.Paymets.id == payment.id)
            db_payment = await session.execute(db_payment)
            db_payment = db_payment.scalars().one()
            if not db_payment:
                return status_error
            await session.delete(db_payment)
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/change_payment")
async def change_payment(payment: Payment, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_payment = select(db.Paymets).filter(db.Paymets.id == payment.id)
            db_payment = await session.execute(db_payment)
            db_payment = db_payment.scalars().one()
            if not db_payment:
                return status_error
            if payment.user_id: db_payment.user_id = payment.user_id
            if payment.amount: db_payment.amount = payment.amount
            if payment.wallet_address: db_payment.wallet_address = payment.wallet_address
            if payment.status: db_payment.status = payment.status

            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.get("/get_banned_users")
async def get_banned_users(request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_banned = select(db.BannedUsers)
            db_banned = await session.execute(db_banned)
            db_banned = db_banned.scalars()
            if not db_banned:
                db_banned = []

            return {**status_ok, **{"banneds": [
                {
                    "id": banned.id,
                    "user_id": banned.user_id,
                    "telegram_id": banned.telegram_id,
                } for banned in db_banned]}}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/ban_user")
async def ban_user(ban: Banned, request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        try:
            db_user = await get_user_on_id(id=ban.user_id, telegram_id=ban.telegram_id, session=session)
            if not db_user:
                return status_error
            payment = db.BannedUsers(user_id=db_user.id, telegram_id=db_user.telegram_id)
            session.add(payment)
            await session.commit()
            return status_ok
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return status_invalid_token


@app.post("/buy_item")
async def buy_item(request: Request, session: AsyncSession = Depends(db.get_async_session)):
    if request.headers['Token'] == Token:
        data = await request.json()
        item_id = data.get('item_id')
        user_id = 1

        # item data
        item_response = await get_item(item_id=item_id, request=request, session=session)
        if item_response.get('status') != 'ok':
            return item_response

        item_price = float(item_response.get('price'))

        # user data
        user_response = await get_user(user_id=user_id, request=request, session=session)
        if user_response.get('status') != 'ok':
            return user_response

        user_balance = float(user_response.get('balance'))
        if user_balance > item_price:
            new_balance = user_balance - item_price
            print(type(new_balance))
        else:
            return {"status": "error", "error": "Not enough balance"}

        # change user balance
        change_user_response = await change_user(user=User(id=user_id, balance=new_balance), request=request, session=session)
        if change_user_response.get('status') != 'ok':
            return change_user_response

        add_item_response = await add_user_item(item=UserItem(user_id=user_id, item_id=item_id), request=request, session=session)
        if add_item_response.get('status') != 'ok':
            return add_item_response

        return status_ok
    else:
        return status_invalid_token
