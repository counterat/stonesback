from db import *
import uuid
import jwt
import requests

async def generate_unique_uuid(is_payout=False):
    async with async_session() as session:

        while True:
            new_uuid = uuid.uuid4()

            if is_payout:
                # Асинхронно проверяем, существует ли уже такой UUID в базе данных для Payouts
                stmt = select(Payouts).filter(Payouts.order_id == str(new_uuid))
                result = await session.execute(stmt)
                existing_record = result.scalar()
                if not existing_record:
                    # Если такого UUID еще нет в базе данных, возвращаем его
                    return str(new_uuid)
            else:
                # Асинхронно проверяем, существует ли уже такой UUID в базе данных для Payments
                stmt = select(Payments).filter(Payments.order_id == str(new_uuid))
                result = await session.execute(stmt)
                existing_record = result.scalar()
                if not existing_record:
                    # Если такого UUID еще нет в базе данных, возвращаем его
                    return str(new_uuid)


async def find_user_by_telegram_id(telegram_id):
    try:
        async with async_session() as session:
            async with session.begin():
                query = select(User).where(User.telegram_id == telegram_id)
                result = await session.execute(query)
                users = result.scalars().all()
            
                return users[0]
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

async  def find_user_by_invit_code(invit_code):
    try:
        async with async_session() as session:
            query = select(User).where(User.invitation_code == invit_code)
            result = await session.execute(query)
            return result.scalar()
    except Exception as ex:
        print(ex)

async def find_user_by_id(id):
    try:
        async with async_session() as session:
            async with session.begin():
                query = select(User).where(User.id == id)
                result = await session.execute(query)
                users = result.scalars().all()
                return users[0]
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
from decimal import Decimal, getcontext
getcontext().prec = 10

async def add_purchase(user_id, good_id,deltatime):
    try:
        created_at =  datetime.utcnow()
        new_purchase = Purchase(
            was_purchased_by_user_id = user_id,
            good_id = good_id,
            created_at = created_at,
            expiration_date = created_at+timedelta(minutes=deltatime)


        )
        async with async_session() as session:
            async with session.begin():
                session.add(new_purchase)
        return new_purchase
    except Exception as ex:
        print(ex)

async def buy_mana_by_user(user_id):
    user = await find_user_by_id(user_id)
    if user.mana<100 and user.fehu_balance>=15: 
        async with async_session() as session:
            async with session.begin():
                mana_to_add = 10
                if mana_to_add + user.mana > 100:
                    mana_to_add = 100-user.mana
                update_user_query = update(User).where(User.id==user_id).values(fehu_balance=user.fehu_balance-15, mana =user.mana+mana_to_add)
                result = await session.execute(update_user_query)
            user = await find_user_by_id(user_id)
            return user
    return False

async def add_payout(user_id, amount, address):
    try:
        """__tablename__ = 'Payouts'
        id = Column(Integer, primary_key=True)
        by_user_id = Column(Integer)
        ton_amount = Column(DECIMAL)
        is_paid = Column(Boolean)
        created_at = Column(DateTime)
        is_approved = Column(Boolean)
        address = Column(String)"""
        user = await find_user_by_id(user_id)
        if user.real_balance:
            uniq_id = await generate_unique_uuid(True)
            new_payout = Payouts(
by_user_id = user_id, ton_amount=amount, order_id=uniq_id, address=address
        )
            async with async_session() as session:
                async with session.begin():
                    session.add(new_payout)
                    update_user_query= (update(User)
                                        .where(User.id == user_id)
                                        .values(real_balance=user.real_balance-Decimal(str(amount)))

                                        )
                    await session.execute(update_user_query)
            return new_payout, user
    except Exception as ex:
        print(ex)



async def add_payment(user_id, amount,  uuid, status  , order_id , address , url ):
    try:
        new_payment = Payments(
            user_id=user_id,
            amount=amount,
            uuid=uuid,
            order_id =order_id,
            status =status,
            created_at =datetime.now(),
            address=address,
            url=url

        )
        async with async_session() as session:
            async with session.begin():
                print(new_payment.to_dict(), 'LOXXXXXXXXXXXXXXX')
                session.add(new_payment)
        return new_payment


    except Exception as ex:
        print(ex, 'LXOXOXOXOXOXO')
        return False


async def buy_stone_by_user(user_id, stone_id):
    
        async with async_session() as session:
            async with session.begin():
                print(stone_id)
                query_for_good = select(Good).where(Good.id == stone_id)

                result = await  session.execute(query_for_good)
                good = result.scalar()
                query_for_user = select(User).where(User.id == user_id)
               
                result = await session.execute(query_for_user)
                user = result.scalar()
                
                print(user.balances)
               
                if (user.real_balance >=Decimal(str( good.price_in_ton))):
                    mana = 0
                    mana_spent = 100-user.mana
                    additional_hours = mana_spent//25
                    if user.mana>=20:
                        mana = user.mana-20
                    
                    purchase = await add_purchase(user.id, good.id, deltatime=min_circle_in_hours+additional_hours)
                  
                    
                    stones = user.balances
                  
                    stones[str(good.id)].append( purchase.to_dict())
             
                    float_to_decimal = Decimal(str(good.price_in_ton))
                    update_user_query = (
                        update(User)
                        .where(User.id == user.id)
                        .values(real_balance=user.real_balance - float_to_decimal, balances = stones, mana=mana)
                    )
                    await session.execute(update_user_query)
                    if user.invited_by:
                        user_who_invited = await  find_user_by_id(user.invited_by)
                        update_user_who_invited_query = (
                            update(User)
                            .where(User.id == user_who_invited.id)
                            .values(real_balance=user_who_invited.real_balance+Decimal('0.05')*Decimal(str( good.price_in_ton)), fehu_balance=user.fehu_balance+10)
                        )
                        message_text = f'Вам начислено {Decimal("0.01")*Decimal(str( good.price_in_ton))} и 10 $FEHU за рефа с айди {user.id}!'

                        # Формируем URL для отправки сообщения
                        send_message_url = f'https://api.telegram.org/bot{API_TOKEN_FOR_TGBOT}/sendMessage'

                        # Параметры запроса
                        params = {
                            'chat_id': user_who_invited.telegram_id,
                            'text': message_text
                        }

                        # Отправляем POST-запрос к API Telegram для отправки сообщения
                        response = requests.post(send_message_url, json=params)
                        await session.execute(update_user_who_invited_query)
                       

                    query_for_user = select(User).where(User.id == user_id)
                    result = await session.execute(query_for_user)
                    user = result.scalar()
         
                    return user
                return 'not enough money'
async def add_user(telegram_id, name, username, created_at, invit_code):
    try:
        password = str(uuid.uuid4())
        user = await find_user_by_invit_code(invit_code)
        if not user:
            new_user = User(
                telegram_id=telegram_id,
                name=name,
                username=username,
                created_at=created_at,
                password=password,
                sign=jwt.encode({'id': telegram_id, "password": password}, 'secret_key'),
                invitation_code=random.randint(100, 2147483647),

            )
        else:
            new_user = User(
            telegram_id=telegram_id,
            name=name,
            username=username,
            created_at=created_at,
            password=password,
            sign=jwt.encode({'id':telegram_id, "password":password}, 'secret_key'),
            invitation_code = random.randint(100, 2147483647),
            invited_by = user.id
        )

        # Создание асинхронной сессии и добавление пользователя в базу данных
        async with async_session() as session:
            async with session.begin():
                session.add(new_user)
   

        return new_user
    except Exception as ex:
        print(ex, 'EEEEEEEE')
