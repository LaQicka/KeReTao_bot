from sqlalchemy import Column, Integer, String, Boolean, select, update, BigInteger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

Base = declarative_base()

class KRT_User(Base):
    __tablename__ = 'krt_users'
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String) 


async def get_all_krt_users(session):
    async with session() as s:
        async with s.begin():
            result = await s.execute(select(KRT_User))

    return result.scalars().all()


async def create_krt_user(session, user_id, username):
    user = KRT_User(user_id=user_id, username=username)
    async with session() as s:
        async with s.begin():
            s.add(user)
    return user


async def get_krt_user_by_user_id(session, user_id):
    async with session() as s:
        async with s.begin():
            result = await s.execute(select(KRT_User).where(KRT_User.user_id == user_id))
            user = result.scalar_one_or_none()
    return user





class KRT_REG_Request(Base):
    __tablename__ = 'krt_reg_requests'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger)
    username = Column(String)
    reg_msg = Column(String)


async def get_krt_reg_request_by_user_id(session, user_id):
    async with session() as s:
        async with s.begin():
            result = await s.execute(select(KRT_REG_Request).where(KRT_REG_Request.user_id == user_id))
            user = result.scalar_one_or_none()
    return user


async def get_all_krt_reg_requests(session):
    async with session() as s:
        async with s.begin():
            result = await s.execute(select(KRT_REG_Request))

    return result.scalars().all()


async def create_krt_reg_request(session, user_id: BigInteger, username: String, reg_msg: String):
    req = KRT_REG_Request(user_id=user_id, username=username, reg_msg=reg_msg)
    async with session() as s:
        async with s.begin():
            s.add(req)
            
    return req


async def delete_krt_request(session, request: KRT_REG_Request):
    async with session() as s:
        async with s.begin():
            if request:
                await s.delete(request)
                await s.commit()





class VPN_User(Base):
    __tablename__ = 'vpn_users'
    user_id = Column(BigInteger, primary_key=True)
    reg = Column(Boolean)
    key = Column(String)


async def get_all_vpn_users(session):
    async with session() as s:
        async with s.begin():
            result = await s.execute(select(VPN_User))

    return result.scalars().all()


async def create_vpn_user(session, user_id, reg, key):
    user = VPN_User(user_id=user_id, reg=reg, key=key)
    async with session() as s:
        async with s.begin():
            s.add(user)
    return user


async def get_vpn_user_by_user_id(session, user_id):
    async with session() as s:
        async with s.begin():
            result = await s.execute(select(VPN_User).where(VPN_User.user_id == user_id))
            user = result.scalar_one_or_none()
    return user


async def update_vpn_user(session, user_id, key):
    async with session() as s:
        async with s.begin():
            user = await get_vpn_user_by_user_id(session, user_id)
            if user:
                stmt = update(VPN_User).where(VPN_User.user_id == user_id).values(key=key)
                user.key = key
                await s.execute(stmt)
                await s.commit()



class VPN_KEY_Request(Base):
    __tablename__ = 'vpn_key_requests'
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String)


async def get_all_vpn_key_requests(session):
    async with session() as s:
        async with s.begin():
            result = await s.execute(select(VPN_KEY_Request))

    return result.scalars().all()


async def get_vpn_request_by_user_id(session, user_id):
    async with session() as s:
        async with s.begin():
            result = await s.execute(select(VPN_KEY_Request).where(VPN_KEY_Request.user_id == user_id))
            request = result.scalar_one_or_none()
    return request


async def create_vpn_key_request(session, user_id: BigInteger, username: String):
    req = VPN_KEY_Request(user_id=user_id, username=username)
    async with session() as s:
        async with s.begin():
            s.add(req)
            
    return req


async def delete_vpn_request(session, request: VPN_KEY_Request):
    async with session() as s:
        async with s.begin():
            if request:
                await s.delete(request)
                await s.commit()





async def create_async_session():
    # engine = create_async_engine('postgresql+asyncpg://user:password@host:port/database')

    # username = config.get('DATABASE','DB_USERNAME')
    # password = config.get('DATABASE','DB_PASSWORD')
    # host = config.get('DATABASE','DB_HOST')
    # port = config.get('DATABASE','DB_PORT')
    # name = config.get('DATABASE','DB_NAME')

    engine = create_async_engine(
        'postgresql+asyncpg://'+config.get('DATABASE','DB_USERNAME')+
            ':'+str(config.get('DATABASE','DB_PASSWORD'))
            +'@'+config.get('DATABASE','DB_HOST')
            +':'+str(config.get('DATABASE','DB_PORT'))
            +'/'+config.get('DATABASE','DB_NAME'))
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session


