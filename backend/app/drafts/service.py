"""B 的业务层入口。路由保持薄层，C 通过此服务读取当前用户草稿。

实现要求：所有读取按 user_id 过滤；CAS 更新 revision；选择幂等；
只保存获得授权的选择摘要；一次数据库事务内更新草稿及选择。
"""
from sqlalchemy.orm import Session

from app.core.errors import not_implemented
from app.drafts.schemas import DraftOut


class DraftService:
    def __init__(self, session: Session):
        self.session = session

    def get_owned(self, draft_id: str, user_id: str) -> DraftOut:
        not_implemented("DraftService.get_owned")
