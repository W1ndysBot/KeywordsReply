import logging
import os
import sys
import asyncio
import re
import sqlite3

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

DB_PATH = os.path.join(DATA_DIR, "keywords.db")


# 查看功能开关状态
def load_KeywordsReply(group_id):
    return load_switch(group_id, "关键词回复")


# 保存功能开关状态
def save_KeywordsReply(group_id, status):
    save_switch(group_id, "关键词回复", status)


# 初始化关键词数据库
def init_KeywordsReply_database():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 创建表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keywords (
                group_id TEXT NOT NULL,
                keyword TEXT NOT NULL,
                reply TEXT NOT NULL,
                UNIQUE(group_id, keyword)
            )
        """
        )

        conn.commit()
        conn.close()
        logging.info(f"初始化关键词数据库成功")


# 添加关键词回复
async def add_KeywordsReply(websocket, group_id, raw_message, message_id):
    if raw_message.startswith("kradd"):
        match = re.match(r"kradd(.*?)\s+(.*)", raw_message)
        if match:
            keyword = match.group(1).strip()

            # 将cq码中的&#91;和&#93;替换为[]
            reply = match.group(2).replace("&#91;", "[").replace("&#93;", "]")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT OR REPLACE INTO keywords (group_id, keyword, reply) VALUES (?, ?, ?)",
                    (group_id, keyword, reply),
                )
                conn.commit()
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]关键词回复已更新\n关键词：{keyword}\n回复：{reply}",
                )
            except Exception as e:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]添加关键词发生错误，错误信息：{e}",
                )
            finally:
                conn.close()


# 删除关键词回复
async def remove_KeywordsReply(websocket, group_id, raw_message, message_id):
    match = re.match(r"krrm(.*)", raw_message)
    if match:
        keyword = match.group(1).strip()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM keywords WHERE group_id = ? AND keyword = ?",
                (group_id, keyword),
            )
            conn.commit()
            await send_group_msg(
                websocket,
                group_id,
                f"[CQ:reply,id={message_id}]关键词回复已删除",
            )
        except Exception as e:
            await send_group_msg(
                websocket,
                group_id,
                f"[CQ:reply,id={message_id}]删除关键词发生错误，错误信息：{e}",
            )
        finally:
            conn.close()


# 管理关键词回复
async def manage_KeywordsReply(
    websocket, user_id, group_id, raw_message, role, message_id
):
    try:
        # 开启关键词回复
        if raw_message == "kron":
            if is_authorized(role, user_id):
                if load_KeywordsReply(group_id):
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]关键词回复已开启，无需重复开启",
                    )
                else:
                    save_KeywordsReply(group_id, True)
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]关键词回复已开启",
                    )
            else:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]您没有权限开启关键词回复",
                )
            return True

        # 关闭关键词回复
        elif raw_message == "kroff":
            if is_authorized(role, user_id):
                if not load_KeywordsReply(group_id):
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]关键词回复已关闭，无需重复关闭",
                    )
                else:
                    save_KeywordsReply(group_id, False)
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]关键词回复已关闭",
                    )
            else:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]您没有权限关闭关键词回复",
                )
            return True

        # 添加关键词回复
        elif raw_message.startswith("kradd"):
            if is_authorized(role, user_id):
                if load_KeywordsReply(group_id):
                    await add_KeywordsReply(
                        websocket, group_id, raw_message, message_id
                    )
                else:
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]关键词回复未开启，请联系管理员使用“kron”开启功能",
                    )
            else:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]您没有权限添加关键词回复",
                )
            return True

        # 删除关键词回复
        elif raw_message.startswith("krrm"):
            if is_authorized(role, user_id):
                if load_KeywordsReply(group_id):
                    await remove_KeywordsReply(
                        websocket, group_id, raw_message, message_id
                    )
                else:
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"[CQ:reply,id={message_id}]关键词回复未开启，请联系管理员使用“kron”开启功能",
                    )
            else:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]您没有权限删除关键词回复",
                )
            return True

    except Exception as e:
        logging.error(f"管理关键词回复失败: {e}")
        return


# 关键词回复
async def reply_KeywordsReply(websocket, group_id, raw_message, message_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM keywords WHERE group_id = ? AND keyword = ?",
            (group_id, raw_message),
        )
        keywords = cursor.fetchone()
        if keywords:
            _, keyword, reply = keywords
            if keyword == raw_message:
                reply_message = reply.replace("&#91;", "[").replace("&#93;", "]")
                reply_message = f"[CQ:reply,id={message_id}]{reply_message}"
                await send_group_msg(
                    websocket,
                    group_id,
                    reply_message,
                )

    except Exception as e:
        logging.error(f"关键词回复失败: {e}")
    finally:
        conn.close()


# 菜单
async def menu_KeywordsReply(websocket, group_id, message_id):
    content = """关键词回复系统菜单
    
kron 开启关键词回复
kroff 关闭关键词回复
kradd关键词 回复 添加关键词回复
krrm关键词 删除关键词回复"""
    await send_group_msg(
        websocket,
        group_id,
        f"[CQ:reply,id={message_id}]{content}",
    )


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

        init_KeywordsReply_database()

        # 菜单
        if raw_message == "keywordsreply":
            await menu_KeywordsReply(websocket, group_id, message_id)
            return

        # 先处理管理关键词回复
        if await manage_KeywordsReply(
            websocket, user_id, group_id, raw_message, role, message_id
        ):
            return

        # 再处理关键词回复
        await reply_KeywordsReply(websocket, group_id, raw_message, message_id)

    except Exception as e:
        logging.error(f"处理KeywordsReply群消息失败: {e}")
        return


# 统一事件处理入口
async def handle_events(websocket, msg):
    """统一事件处理入口"""
    post_type = msg.get("post_type", "response")  # 添加默认值
    try:
        # 处理回调事件
        if msg.get("status") == "ok":
            return

        # 处理元事件
        if post_type == "meta_event":
            return

        # 处理消息事件
        elif post_type == "message":
            message_type = msg.get("message_type")
            if message_type == "group":
                await handle_KeywordsReply_group_message(websocket, msg)
            elif message_type == "private":
                return

        # 处理通知事件
        elif post_type == "notice":
            return

    except Exception as e:
        error_type = {
            "message": "消息",
            "notice": "通知",
            "request": "请求",
            "meta_event": "元事件",
        }.get(post_type, "未知")

        logging.error(f"处理KeywordsReply{error_type}事件失败: {e}")

        # 发送错误提示
        if post_type == "message":
            message_type = msg.get("message_type")
            if message_type == "group":
                await send_group_msg(
                    websocket,
                    msg.get("group_id"),
                    f"处理KeywordsReply{error_type}事件失败，错误信息：{str(e)}",
                )
            elif message_type == "private":
                await send_private_msg(
                    websocket,
                    msg.get("user_id"),
                    f"处理KeywordsReply{error_type}事件失败，错误信息：{str(e)}",
                )
