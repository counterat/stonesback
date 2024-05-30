import decimal
import random
from datetime import datetime, timedelta, timezone
from random import randint
from sqlalchemy import  Column, Integer, String, Float, JSON, DateTime, Boolean, ForeignKey,ARRAY, DECIMAL, BigInteger, Sequence, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import array
from config import * 

Base = declarative_base()

class StonesTON(Base):
    __abstract__ = True

    def to_dict(self):
        return {
            c.name: (
                getattr(self, c.name).__str__() if isinstance(getattr(self, c.name), datetime)
                else str(getattr(self, c.name)) if isinstance(getattr(self, c.name), decimal.Decimal)
                else getattr(self, c.name)
            )
            for c in self.__table__.columns if c.name != 'password'
        }

class User( StonesTON):
    __tablename__ = 'User'
    id = Column(BigInteger,Sequence('user_id_seq', start=7712779), primary_key=True)
    password = Column(String)
    sign = Column(String)
    telegram_id = Column(BigInteger)
    name = Column(String)
    mana = Column(Integer, default=100 )
    fehu_balance = Column(DECIMAL, default=0)
    username = Column(String)
    invited_by = Column(BigInteger)
    invitation_code= Column(BigInteger)
    invited_users = Column(ARRAY(Integer), default=[])
    real_balance = Column(DECIMAL, default=0)
    balances = Column(JSON, default=  {1 : [], 2: [], 3:[],4:[],5:[] })
    amount_of_money_withdrawed = Column(Float, default=0)
    amount_of_money_topupped= Column(Float, default=0)
    profit = Column(DECIMAL, default=0)
    created_at  = Column(DateTime, default=datetime.now)

class Purchase(StonesTON):
    __tablename__='Purchases'
    id = Column(Integer, primary_key=True)
    was_purchased_by_user_id = Column(Integer)
    good_id = Column(Integer)
    profit_given = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.now)
    expiration_date = Column(DateTime)
    
class Good(StonesTON):
    __tablename__='Goods'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    price_in_ton = Column(Float)
    income = Column(Float)
    income_in_fehu = Column(Float)


class  Payouts(StonesTON):
    __tablename__ = 'Payouts'
    id = Column(BigInteger, primary_key=True)
    by_user_id = Column(BigInteger)
    ton_amount = Column(DECIMAL)
    order_id = Column(String)
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime)
    is_approved = Column(Boolean, default=None)
    address = Column(String)

class Payments(StonesTON):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    amount = Column(Float)

    uuid = Column(String)
    description = Column(String)
    order_id = Column(String)
    status = Column(String)
    created_at = Column(DateTime)

    address = Column(String)

    url = Column(String)





engine = create_async_engine(DB_URL, echo=True)

# Создание асинхронной фабрики сессий
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
"""     __tablename__='Goods'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    price_in_ton = Column(Float)
    income = Column(Float)
    income_in_fehu = Column(Float) """

async def add_stones():
    try:
        first_rune = Good(
            name='1',
            price_in_ton=0.1,
            income = 0,
            income_in_fehu = 1 

        )
        second_rune = Good(
            name='2',
            price_in_ton=0.3,
            income = 0.1,
            income_in_fehu = 5 

        )
        third_rune = Good(
            name='3',
            price_in_ton=0.5,
            income = 0.2,
            income_in_fehu = 10 

        )
        fourth_rune = Good(
            name='4',
            price_in_ton=1,
            income = 0.4,
            income_in_fehu = 25 

        )
        fifth_rune = Good(
            name='5',
            price_in_ton=3,
            income = 1.3,
            income_in_fehu = 80 

        )
        async with async_session() as session:
            async with session.begin():
                session.add_all([first_rune, second_rune, third_rune, fourth_rune, fifth_rune])

    except Exception as ex:
        print(ex)

async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаляем все таблицы
        await conn.run_sync(Base.metadata.create_all) 
        
import asyncio
""" asyncio.run(add_stones()) """