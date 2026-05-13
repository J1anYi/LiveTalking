import time
import os
import re
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from avatars.base_avatar import BaseAvatar
from utils.logger import logger
from rag import build_rag_prompt
from server.session_manager import session_manager


# 预编译正则表达式，避免重复编译开销
_RE_EMOJI = re.compile(r'[\U0001F300-\U0001F9FF]')
_RE_BOLD = re.compile(r'\*\*([^*]+)\*\*')
_RE_ITALIC = re.compile(r'\*([^*]+)\*')
_RE_HEADER = re.compile(r'^#+\s*', re.MULTILINE)
_RE_CODE = re.compile(r'`([^`]+)`')
_RE_LIST = re.compile(r'^[\-\*]\s+', re.MULTILINE)
_RE_SPACES = re.compile(r'  +')


def clean_text_for_tts(text: str) -> str:
    """清理文本中的 Markdown 格式符号，避免 TTS 读出来"""
    if not text:
        return text
    # 快速检查：如果没有特殊字符且没有 emoji，直接返回
    if '*' not in text and '#' not in text and '`' not in text and '-' not in text:
        if not _RE_EMOJI.search(text):
            return text

    # 移除 emoji
    text = _RE_EMOJI.sub('', text)
    # 移除 **粗体** 和 *斜体*
    text = _RE_BOLD.sub(r'\1', text)
    text = _RE_ITALIC.sub(r'\1', text)
    # 移除 # 标题
    text = _RE_HEADER.sub('', text)
    # 移除 `代码`
    text = _RE_CODE.sub(r'\1', text)
    # 移除行首列表符号
    text = _RE_LIST.sub('', text)
    # 移除多余空格
    text = _RE_SPACES.sub(' ', text)
    return text.strip()

# RAG integration (set by app.py during initialization)
rag_retriever = None

# 缓存 OpenAI 客户端，避免每次调用重新创建
_openai_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        api_key = os.environ.get("DASHSCOPE_API_KEY")
        if api_key is None:
            raise ValueError(
                "DASHSCOPE_API_KEY not set. "
                "Please set the environment variable DASHSCOPE_API_KEY."
            )
        base_url = os.environ.get(
            "DASHSCOPE_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        from openai import OpenAI
        _openai_client = OpenAI(api_key=api_key, base_url=base_url)
    return _openai_client


def llm_response(message,avatar_session:'BaseAvatar',datainfo:dict={}):
    try:
        opt = avatar_session.opt

        # Initialize conversation history if not exists
        if not hasattr(avatar_session, '_llm_history'):
            avatar_session._llm_history = []

        start = time.perf_counter()
        client = _get_openai_client()
        end = time.perf_counter()
        logger.info(f"llm Time init: {end-start}s,{message}")

        # 记录当前的生成 ID，用于中断检测
        gen_id = getattr(avatar_session, '_gen_id', 0)

        # RAG retrieval for chat mode (enhanced prompt)
        enhanced_message = message
        rag_mode = session_manager.get_rag_mode(avatar_session.sessionid)

        if rag_retriever and getattr(opt, 'rag_enabled', False):
            try:
                # Build retrieval query with conversation context
                retrieval_query = message
                if avatar_session._llm_history:
                    # Include last 2 turns for context
                    context_msgs = avatar_session._llm_history[-4:]
                    retrieval_query = " ".join([m["content"] for m in context_msgs]) + " " + message

                # Retrieve relevant documents
                retrieved = rag_retriever.retrieve(retrieval_query)

                if retrieved:
                    if rag_mode == "rag_only":
                        # 原有模式：只使用 RAG 内容
                        enhanced_message = build_rag_prompt(message, retrieved)
                    else:
                        # RAG+Model 模式：将 RAG 内容作为参考信息
                        context_parts = []
                        for chunk in retrieved[:3]:  # 最多使用 3 个文档
                            text = chunk.get("text", "")
                            context_parts.append(f"- {text}")
                        context = "\n".join(context_parts)
                        enhanced_message = f"参考信息:\n{context}\n\n用户问题: {message}\n\n请结合参考信息和你的知识，用简短、口语化的方式回答问题:"
                    logger.info(f"RAG retrieved {len(retrieved)} documents, mode={rag_mode}")
            except Exception as e:
                logger.warning(f"RAG retrieval failed, using original message: {e}")

        completion = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "qwen-plus"),
            messages=[{'role': 'system', 'content': '你是一个知识助手，尽量以简短、口语化的方式输出'},
                    {'role': 'user', 'content': enhanced_message}],
            stream=True,
        )
        result=""
        first = True
        chunk_count = 0
        for chunk in completion:
            if len(chunk.choices)>0:
                if first:
                    end = time.perf_counter()
                    logger.info(f"llm Time to first chunk: {end-start}s")
                    first = False
                msg = chunk.choices[0].delta.content
                if msg is None:
                    continue
                chunk_count += 1
                lastpos=0
                for i, char in enumerate(msg):
                    if char in ",.!;:，。！？：；\n" :
                        result = result+msg[lastpos:i+1]
                        lastpos = i+1
                        if len(result)>=5:  # 降低阈值，更快发送
                            # 中断检测：如果 flush_talk 被调用过，丢弃当前分段
                            if getattr(avatar_session, '_gen_id', 0) != gen_id:
                                logger.info("LLM segment discarded due to interrupt")
                                result=""
                                break
                            cleaned = clean_text_for_tts(result)
                            if cleaned:
                                logger.info(f"LLM segment: {cleaned[:50]}...")
                                avatar_session.put_msg_txt(cleaned, datainfo)
                            result=""
                result = result+msg[lastpos:]
        end = time.perf_counter()
        logger.info(f"llm Time to last chunk: {end-start}s, total chunks: {chunk_count}")
        # 最终段也做中断检测
        if result and getattr(avatar_session, '_gen_id', 0) == gen_id:
            cleaned = clean_text_for_tts(result)
            if cleaned:
                logger.info(f"LLM final segment: {cleaned[:50]}...")
                avatar_session.put_msg_txt(cleaned, datainfo)

        # Update conversation history
        avatar_session._llm_history.append({'role': 'user', 'content': message})
        
    except Exception as e:
        logger.exception('llm exceptiopn:')
        return   