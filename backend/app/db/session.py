from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine():
    return create_engine(
        get_settings().database_url.get_secret_value(),
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={"connect_timeout": 5},
    )


def get_session():
    """所有业务共享事务边界；成功提交，异常回滚，不在路由中自建连接。"""
    factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    with factory() as session:
        with session.begin():
            yield session


DBSession = Annotated[Session, Depends(get_session)]
