# 数据表对应的model对象

from __future__ import annotations

from sqlalchemy import func

from dingo_command.db.engines.mysql import get_session
from dingo_command.db.models.message.models import ExternalMessage


external_message_dir_dic = {"create_date": ExternalMessage.create_date,}

class MessageSQL:

    @classmethod
    def create_external_message(cls, message_info):
        session = get_session()
        with session.begin():
            session.add(message_info)

    @classmethod
    def update_external_message(cls, message_info):
        session = get_session()
        with session.begin():
            session.merge(message_info)

    @classmethod
    def delete_external_message(cls, message_id):
        session = get_session()
        with session.begin():
            # 删除消息
            session.query(ExternalMessage).filter(ExternalMessage.id == message_id).delete()

    @classmethod
    def delete_external_message_by_ids(cls, message_ids):
        session = get_session()
        with session.begin():
            # 删除消息
            session.query(ExternalMessage).filter(ExternalMessage.id.in_(message_ids)).delete()

    @classmethod
    def get_external_message_by_id(cls, message_id):
        session = get_session()
        with session.begin():
            return session.query(ExternalMessage).filter(ExternalMessage.id == message_id).first()


    @classmethod
    def list_external_message(cls, query_params, page=1, page_size=10, field=None, dir="ascend"):
        session = get_session()
        with session.begin():
            # 查询语句
            query = session.query(ExternalMessage)
            # 查询条件
            # 类型以某个参数开头
            if "message_type_start" in query_params and query_params["message_type_start"]:
                query = query.filter(ExternalMessage.message_type.like(query_params["message_type_start"] + '%'))
            # 某个指定的类型
            if "message_type" in query_params and query_params["message_type"]:
                query = query.filter(ExternalMessage.message_type == query_params["message_type"])
            # 总数
            count = query.count()
            # 排序
            if field is not None and field in external_message_dir_dic:
                if dir == "ascend" or dir is None :
                    query = query.order_by(external_message_dir_dic[field].asc())
                elif dir == "descend":
                    query = query.order_by(external_message_dir_dic[field].desc())
            else:
                query = query.order_by(ExternalMessage.create_date.asc())
                # 分页条件
            page_size = int(page_size)
            page_num = int(page)
            # 查询所有数据
            if page_size == -1:
                return count, query.all()
            # 页数计算
            start = (page_num - 1) * page_size
            query = query.limit(page_size).offset(start)
            message_list = query.all()
            # 返回
            return count, message_list

    @classmethod
    def get_external_message_number_by_status(cls, message_type, message_status):
        session = get_session()
        with session.begin():
            return session.query(ExternalMessage).filter(ExternalMessage.message_type == message_type).filter(ExternalMessage.message_status == message_status).count()

    @classmethod
    def update_external_message_4error(cls, message_ids, description):
        session = get_session()
        with session.begin():
            session.query(ExternalMessage).filter(ExternalMessage.id.in_(message_ids)).update({'message_status':'ERROR', 'message_description': description, 'update_date': func.now()}, synchronize_session=False)