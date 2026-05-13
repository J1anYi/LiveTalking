###############################################################################
#  服务器路由 — 统一异常处理的 API 路由
###############################################################################

import json
import numpy as np
import asyncio
from aiohttp import web

from utils.logger import logger


# ─── 路由工具函数 ──────────────────────────────────────────────────────────

def json_ok(data=None):
    """返回成功 JSON 响应"""
    body = {"code": 0, "msg": "ok"}
    if data is not None:
        body["data"] = data
    return web.Response(
        content_type="application/json",
        text=json.dumps(body),
    )


def json_error(msg: str, code: int = -1):
    """返回错误 JSON 响应"""
    return web.Response(
        content_type="application/json",
        text=json.dumps({"code": code, "msg": str(msg)}),
    )


from server.session_manager import session_manager

def get_session(request, sessionid: str):
    """从 app 中获取 session 实例"""
    return session_manager.get_session(sessionid)


# ─── 路由处理函数 ──────────────────────────────────────────────────────────

async def human(request):
    """文本输入（echo/chat 模式），支持 voice/emotion 参数"""
    try:
        params: dict = await request.json()

        sessionid: str = params.get('sessionid', '')
        avatar_session = get_session(request, sessionid)
        if avatar_session is None:
            return json_error("session not found")

        if params.get('interrupt'):
            avatar_session.flush_talk()

        datainfo = {}
        if params.get('tts'):  # tts 参数透传（voice, emotion 等）
            datainfo['tts'] = params.get('tts')

        if params['type'] == 'echo':
            avatar_session.put_msg_txt(params['text'], datainfo)
        elif params['type'] == 'chat':
            llm_response = request.app.get("llm_response")
            if llm_response:
                asyncio.get_event_loop().run_in_executor(
                    None, llm_response, params['text'], avatar_session, datainfo
                )

        return json_ok()
    except Exception as e:
        logger.exception('human route exception:')
        return json_error(str(e))


async def interrupt_talk(request):
    """打断当前说话"""
    try:
        params = await request.json()
        sessionid = params.get('sessionid', '')
        avatar_session = get_session(request, sessionid)
        if avatar_session is None:
            return json_error("session not found")
        avatar_session.flush_talk()
        return json_ok()
    except Exception as e:
        logger.exception('interrupt_talk exception:')
        return json_error(str(e))


async def humanaudio(request):
    """上传音频文件"""
    try:
        form = await request.post()
        sessionid = str(form.get('sessionid', ''))
        fileobj = form["file"]
        filebytes = fileobj.file.read()

        datainfo = {}

        avatar_session = get_session(request, sessionid)
        if avatar_session is None:
            return json_error("session not found")
        avatar_session.put_audio_file(filebytes, datainfo)
        return json_ok()
    except Exception as e:
        logger.exception('humanaudio exception:')
        return json_error(str(e))


async def set_audiotype(request):
    """设置自定义状态（动作编排）"""
    try:
        params = await request.json()
        sessionid = params.get('sessionid', '')
        avatar_session = get_session(request, sessionid)
        if avatar_session is None:
            return json_error("session not found")
        avatar_session.set_custom_state(params['audiotype'])
        return json_ok()
    except Exception as e:
        logger.exception('set_audiotype exception:')
        return json_error(str(e))


async def record(request):
    """录制控制"""
    try:
        params = await request.json()
        sessionid = params.get('sessionid', '')
        avatar_session = get_session(request, sessionid)
        if avatar_session is None:
            return json_error("session not found")
        if params['type'] == 'start_record':
            avatar_session.start_recording()
        elif params['type'] == 'end_record':
            avatar_session.stop_recording()
        return json_ok()
    except Exception as e:
        logger.exception('record exception:')
        return json_error(str(e))


async def is_speaking(request):
    """查询是否正在说话"""
    params = await request.json()
    sessionid = params.get('sessionid', '')
    avatar_session = get_session(request, sessionid)
    if avatar_session is None:
        return json_error("session not found")
    return json_ok(data=avatar_session.is_speaking())


async def set_rag_mode(request):
    """设置 RAG 模式"""
    try:
        params = await request.json()
        sessionid = params.get('sessionid', '')
        mode = params.get('mode', 'rag_only')

        if mode not in ('rag_only', 'rag_plus_model'):
            return json_error(f"Invalid mode: {mode}. Must be 'rag_only' or 'rag_plus_model'")

        session_manager.set_rag_mode(sessionid, mode)
        return json_ok(data={"mode": mode})
    except Exception as e:
        logger.exception('set_rag_mode exception:')
        return json_error(str(e))


async def get_rag_mode(request):
    """获取当前 RAG 模式"""
    try:
        params = await request.json()
        sessionid = params.get('sessionid', '')
        mode = session_manager.get_rag_mode(sessionid)
        return json_ok(data={"mode": mode})
    except Exception as e:
        logger.exception('get_rag_mode exception:')
        return json_error(str(e))


async def sse_chat(request):
    """SSE 端点：推送 LLM 流式文字到前端"""
    sessionid = request.query.get("sessionid", "")
    if not sessionid:
        return json_error("sessionid required")
    from server.sse_manager import SSEManager
    sse = SSEManager()
    q = sse.subscribe(sessionid)
    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )
    await response.prepare(request)
    try:
        while True:
            data = await asyncio.wait_for(q.get(), timeout=30)
            msg = f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            await response.write(msg.encode("utf-8"))
            if data.get("type") == "done" or data.get("type") == "error":
                break
    except asyncio.TimeoutError:
        await response.write(b"data: {\"type\":\"timeout\"}\n\n")
    except (ConnectionResetError, ConnectionAbortedError):
        pass
    finally:
        sse.unsubscribe(sessionid, q)
    return response


# ─── 会话历史 API ─────────────────────────────────────────────────────────

async def create_conversation(request):
    try:
        params = await request.json()
        sessionid = params.get("sessionid", "")
        if not sessionid:
            return json_error("sessionid required")
        from server.chat_db import ChatHistory
        ch = ChatHistory()
        conv_id = await ch.create_conversation(sessionid)
        session_manager.set_active_conversation(sessionid, conv_id)
        return json_ok(data={"conv_id": conv_id})
    except Exception as e:
        logger.exception("create_conversation error:")
        return json_error(str(e))

async def list_conversations(request):
    try:
        params = await request.json()
        sessionid = params.get("sessionid", "")
        from server.chat_db import ChatHistory
        ch = ChatHistory()
        convs = await ch.list_conversations(sessionid)
        return json_ok(data={"conversations": convs})
    except Exception as e:
        logger.exception("list_conversations error:")
        return json_error(str(e))

async def get_conversation(request):
    try:
        params = await request.json()
        conv_id = params.get("conv_id", "")
        if not conv_id:
            return json_error("conv_id required")
        from server.chat_db import ChatHistory
        ch = ChatHistory()
        conv = await ch.get_conversation(conv_id)
        if not conv:
            return json_error("conversation not found")
        return json_ok(data=conv)
    except Exception as e:
        logger.exception("get_conversation error:")
        return json_error(str(e))

async def delete_conversation(request):
    try:
        params = await request.json()
        conv_id = params.get("conv_id", "")
        if not conv_id:
            return json_error("conv_id required")
        from server.chat_db import ChatHistory
        ch = ChatHistory()
        await ch.delete_conversation(conv_id)
        return json_ok()
    except Exception as e:
        logger.exception("delete_conversation error:")
        return json_error(str(e))


# ─── 路由注册 ──────────────────────────────────────────────────────────────

def setup_routes(app):
    """注册所有路由到 aiohttp app"""
    app.router.add_post("/human", human)
    app.router.add_post("/humanaudio", humanaudio)
    app.router.add_post("/set_audiotype", set_audiotype)
    app.router.add_post("/record", record)
    app.router.add_post("/interrupt_talk", interrupt_talk)
    app.router.add_post("/is_speaking", is_speaking)
    app.router.add_post("/set_rag_mode", set_rag_mode)
    app.router.add_post("/get_rag_mode", get_rag_mode)
    app.router.add_get("/sse/chat", sse_chat)
    app.router.add_post("/conversations/create", create_conversation)
    app.router.add_post("/conversations/list", list_conversations)
    app.router.add_post("/conversations/get", get_conversation)
    app.router.add_post("/conversations/delete", delete_conversation)
    app.router.add_static('/', path='web')
