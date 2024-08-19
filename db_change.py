import datetime
from db import get_engine
from db import Users, Items, UserItems, Paymets, AdditionalData
from sqlalchemy.orm import Session

engine = get_engine()

def add_user(telegram_id, balance=0, inviter=None, deposits_count=0):
    with Session(engine) as session:
        user = Users(telegram_id=telegram_id, balance=balance, inviter=inviter, deposits=deposits_count)
        session.add(user)
        session.commit()


def delete_user(id=None, telegram_id=None):
    with Session(engine) as session:
        if id:
            user = session.query(Users).filter(Users.id == id).first()
        elif telegram_id:
            user = session.query(Users).filter(Users.telegram_id == telegram_id).first()
        else:
            return None
        
        if not user:
            return None
        
        session.delete(user)
        session.commit()


def change_user(id=None, telegram_id=None, balance=None, inviter=None, deposits_count=None):
    with Session(engine) as session:
        if id:
            user = session.query(Users).filter(Users.id == id).first()
        elif telegram_id:
            user = session.query(Users).filter(Users.telegram_id == telegram_id).first()
        else:
            return None
        
        if balance: user.balance = balance
        if inviter: user.inviter  = inviter
        if deposits_count: user.deposits  = deposits_count

        session.commit()


def get_user(id=None, telegram_id=None):
    with Session(engine) as session:
        if id:
            user  = session.query(Users).filter(Users.id  == id).first()
        elif telegram_id:
            user  = session.query(Users).filter(Users.telegram_id  == telegram_id).first()
        else:
            return None
        
        if not user:
            return None
        
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "balance": user.balance,
            "inviter": user.inviter,
            "deposits": user.deposits
        }
    

def get_users():
    with Session(engine) as session:
        users = session.query(Users).all()
        return {"users":[{
                "id": user.id,
                "telegram_id": user.telegram_id,
                "balance": user.balance,
                "inviter": user.inviter,
                "deposits": user.deposits}
                for user in users]}
           


def add_item(price, name, profitability, complete_time, description, icon_path, max_count):
    with Session(engine) as session:
        item = Items(
            price=price,
            name=name,
            profitability=profitability,
            complete_time=complete_time,
            description=description,
            icon_path=icon_path,
            max_count=max_count
        )
        session.add(item)
        session.commit()


def delete_item(id=None):
    with Session(engine) as session:
        if id:
            item = session.query(Items).filter(Items.id  == id).first()
        else:
            return None
        
        if not item:
            return None
        
        session.delete(item)
        session.commit()


def change_item(id=None, price=None, name=None, profitability=None, complete_time=None, description=None, icon_path=None, max_count=None):
    with Session(engine) as session:
        if id:
            item = session.query(Items).filter(Items.id   == id).first()
        else:
            return None
        
        if not item:
            return None
        
        if price: item.price  = price
        if name: item.name  = name
        if profitability: item.profitability  = profitability
        if complete_time: item.complete_time  = complete_time
        if description: item.description  = description
        if icon_path: item.icon_path  = icon_path
        if max_count: item.max_count  = max_count

        session.commit()


def get_item(id):
    with Session(engine) as session:
        if id:
            item  = session.query(Items).filter(Items.id  == id).first()
        else:
            return None
        
        if not item:
            return None
        
        return  {
             "id": item.id,
             "price": item.price,
             "name": item.name,
             "profitability": item.profitability,
             "complete_time": item.complete_time,
             "description": item.description,
             "icon_path": item.icon_path,
             "max_count": item.max_count
         }


def get_items():
    with Session(engine) as session:
       items  = session.query(Items).all()
       return {"items":[{
             "id": item.id,
             "price": item.price,
             "name": item.name,
             "profitability": item.profitability,
             "complete_time": item.complete_time,
             "description": item.description,
             "icon_path": item.icon_path,
             "max_count": item.max_count
         }
         for item in items]}


def add_user_item(user_id=None, item_id=None, telegram_id=None):
    with Session(engine) as session:
        item = session.query(Items).filter(Items.id == item_id).first()
        complete_time = datetime.datetime.now() + datetime.timedelta(hours=item.complete_time)

        if user_id:
            user_item  = UserItems(user_id=user_id, item_id=item_id, complete_time=complete_time)
        elif telegram_id:
            user_id = session.query(Users).filter(Users.telegram_id == telegram_id).first().id
            user_item  = UserItems(user_id=user_id, item_id=item_id, complete_time=complete_time)
        else:
            return None
        
        session.add(user_item)
        session.commit()


def get_user_items(user_id=None, telegram_id=None):
    with Session(engine) as session:
        if user_id:
            user_items  = session.query(UserItems).filter(UserItems.user_id  == user_id).all()
        elif telegram_id:
            user = session.query(Users).filter(Users.telegram_id == telegram_id).first()
            user_items  = session.query(UserItems).filter(UserItems.user_id  == user.id).all()
        else:
            return None
        
        return {"items": [
            {
            "id": user_item.id,
            "user_id": user_item.user_id,
            "item_id": user_item.item_id,
            "complete_time": user_item.complete_time
            } for user_item in user_items
        ]}


def delete_user_item(id=None):
    if not id:
        return None
    with Session(engine) as session:
        user_item = session.query(UserItems).filter(UserItems.id == id).first()
        if not user_item:
            return None
        
        session.delete(user_item)
        session.commit()


def get_add_data():
    with Session(engine) as session:
       add_data  = session.query(AdditionalData).first()
       return  {
            "owner_wallet": add_data.owner_wallet,
            "tax": add_data.tax,
            "payment_auto_complete_time": add_data.payment_auto_complete_time
        }



def change_additional_data(owner_wallet=None, tax=None, payment_time=None):
    with Session(engine) as session:
        additional_data = session.query(AdditionalData).first()
        
        if owner_wallet: additional_data.owner_wallet = owner_wallet
        if tax: additional_data.tax = tax
        if payment_time: additional_data.payment_auto_complete_time = payment_time
        session.commit()


def add_payment(telegram_id=None, user_id=None, amount=None, wallet_address=None, status=None):
    with Session(engine) as session:
        auto_time = get_add_data()
        if user_id:
            pass
        if telegram_id:
            user_id = session.query(Users).filter(Users.telegram_id == telegram_id).first().id

        payment = Paymets(user_id=user_id, amout=amount, wallet_address=wallet_address, status=status,
                          auto_complete_time= datetime.datetime.now() + datetime.timedelta(hours=auto_time["payment_auto_complete_time"]))
        session.add(payment)
        session.commit()

def get_user_payments(user_id=None, telegram_id=None):
    with Session(engine) as session:
       if user_id:
           user_payments  = session.query(Paymets).filter(Paymets.user_id   == user_id).all()
       elif telegram_id:
           user = session.query(Users).filter(Users.telegram_id  == telegram_id).first()
           user_payments  = session.query(Paymets).filter(Paymets.user_id == user.id).all()
       else:
           return None
       
       return {"payments":  [
            {
            "id": payment.id,
            "user_id": payment.user_id,
            "amount": payment.amout,
            "wallet_address": payment.wallet_address,
            "pstatus": payment.status,
            "auto_complete_time": payment.auto_complete_time
            } for payment in user_payments]}


def delete_payment(id=None):
    if not id:
        return None
    with Session(engine) as session:
        payment = session.query(Paymets).filter(Paymets.id == id).first()
        if not payment:
            return None
        
        session.delete(payment)
        session.commit()


def change_payment(id=None, user_id=None, amount=None, wallet_address=None, status=None):
    with Session(engine) as session:
        if id:
            payment = session.query(Paymets).filter(Paymets.id == id).first()
        else:
            return None
        
        if not payment:
            return None
        
        if user_id: payment.user_id  = user_id
        if amount: payment.amout  = amount
        if wallet_address: payment.wallet_address  = wallet_address
        if status: payment.status  = status
        session.commit()



