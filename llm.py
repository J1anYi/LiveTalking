import time
import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from avatars.base_avatar import BaseAvatar
from utils.logger import logger
from rag import build_rag_prompt
from server.session_manager import session_manager

# RAG integration (set by app.py during initialization)
rag_retriever = None

def llm_response(message,avatar_session:'BaseAvatar',datainfo:dict={}):
    try:
        opt = avatar_session.opt

        # Initialize conversation history if not exists
        if not hasattr(avatar_session, '_llm_history'):
            avatar_session._llm_history = []

        start = time.perf_counter()
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "my-secret-key"),
            base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:8317/v1"),
        )
        end = time.perf_counter()
        logger.info(f"llm Time init: {end-start}s,{message}")

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
                        enhanced_message = f"参考信息:\n{context}\n\n用户问题: {message}\n\n请结合参考信息和你的知识回答问题:"
                    logger.info(f"RAG retrieved {len(retrieved)} documents, mode={rag_mode}")
            except Exception as e:
                logger.warning(f"RAG retrieval failed, using original message: {e}")

        completion = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "GLM-5"),
            messages=[{'role': 'system', 'content': '你是一个知识助手，尽量以简短、口语化的方式输出'},
                    {'role': 'user', 'content': enhanced_message}],
            stream=True,
            # 通过以下设置，在流式输出的最后一行展示token使用信息
            stream_options={"include_usage": True}
        )
        result=""
        first = True
        for chunk in completion:
            if len(chunk.choices)>0:
                #print(chunk.choices[0].delta.content)
                if first:
                    end = time.perf_counter()
                    logger.info(f"llm Time to first chunk: {end-start}s")
                    first = False
                msg = chunk.choices[0].delta.content
                if msg is None:
                    continue
                lastpos=0
                #msglist = re.split('[,.!;:，。！?]',msg)
                for i, char in enumerate(msg):
                    if char in ",.!;:，。！？：；" :
                        result = result+msg[lastpos:i+1]
                        lastpos = i+1
                        if len(result)>10:
                            logger.info(result)
                            avatar_session.put_msg_txt(result,datainfo)
                            result=""
                result = result+msg[lastpos:]
        end = time.perf_counter()
        logger.info(f"llm Time to last chunk: {end-start}s")
        if result:
            avatar_session.put_msg_txt(result,datainfo)

        # Update conversation history
        avatar_session._llm_history.append({'role': 'user', 'content': message})
        
    except Exception as e:
        logger.exception('llm exceptiopn:')
        return   