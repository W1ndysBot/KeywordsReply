# script/KeywordsReply/main.py

import logging
import os
import sys
import asyncio

# 添加项目根目录到sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


from app.api import *
from app.switch import load_switch, save_switch


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "KeywordsReply",
)


# 查看功能开关状态
def load_KeywordsReply(group_id):
    return load_switch(group_id, "关键词回复")


# 保存功能开关状态
def save_KeywordsReply(group_id, status):
    save_switch(group_id, "关键词回复", status)


# 添加关键词回复
async def add_KeywordsReply(
    websocket, user_id, group_id, raw_message, role, message_id
):
    pass


# 管理关键词回复
async def manage_KeywordsReply(
    websocket, user_id, group_id, raw_message, role, message_id
):
    try:
        # 开启关键词回复
        if raw_message.startswith("kron"):
            if is_authorized(role, user_id):
                save_KeywordsReply(group_id, True)
                await send_group_msg(
                    websocket, group_id, f"[CQ:reply,id={message_id}]关键词回复已开启"
                )
            else:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]您没有权限开启关键词回复",
                )

        # 关闭关键词回复
        elif raw_message.startswith("kroff"):
            if is_authorized(role, user_id):
                save_KeywordsReply(group_id, False)
                await send_group_msg(
                    websocket, group_id, f"[CQ:reply,id={message_id}]关键词回复已关闭"
                )
            else:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]您没有权限关闭关键词回复",
                )

        # 添加关键词回复
        elif raw_message.startswith("kradd"):
            if is_authorized(role, user_id):
                await add_KeywordsReply(
                    websocket, user_id, group_id, raw_message, role, message_id
                )
            else:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]您没有权限添加关键词回复",
                )

    except Exception as e:
        logging.error(f"管理关键词回复失败: {e}")
        return


# 群消息处理函数
async def handle_KeywordsReply_group_message(websocket, msg):
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))

    except Exception as e:
        logging.error(f"处理KeywordsReply群消息失败: {e}")
        return
