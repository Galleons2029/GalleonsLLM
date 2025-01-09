"""
RAG业务模块
"""
from typing import List

from langchain_openai import ChatOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai import OpenAI, Stream

from app.services.llm.prompt_templates import InferenceTemplate
from app.services.rag.retriever import VectorRetriever
from app.config import settings

from app.utils.logging import get_logger
logger = get_logger(__name__)


class InferenceOpenAI:
    def __init__(self) -> None:
        self._langchain_client = ChatOpenAI(
            model=settings.Silicon_model_v1,
            openai_api_key=settings.Silicon_api_key1,
            openai_api_base=settings.Silicon_base_url,
        )
        self._openai_client = OpenAI(
            api_key=settings.Silicon_api_key1,
            base_url=settings.Silicon_base_url,
        )
        self.template = InferenceTemplate()

    def generate(
        self,
        query: str,
        collections: list[str],
        enable_rag: bool = True,
    ) -> str:
        prompt_template = self.template.create_template(enable_rag=enable_rag)
        prompt_template_variables = {
            "question": query,
        }

        if enable_rag is True:
            retriever = VectorRetriever(query=query)
            hits = retriever.retrieve_top_k(
                k=settings.TOP_K, to_expand_to_n_queries=settings.EXPAND_N_QUERY, collections=collections
            )
            context = retriever.rerank(hits=hits, keep_top_k=settings.KEEP_TOP_K)  # list
            prompt_template_variables["context"] = context

            prompt = prompt_template.format(question=query, context=context)
        else:
            prompt = prompt_template.format(question=query)

        # answer = self._langchain_client.invoke(prompt).content

        # completion = self._openai_client.chat.completions.create(
        #     model="Qwen/Qwen2.5-72B-Instruct",
        #     messages=[
        #         {"role": "developer", "content": "You are a helpful assistant."},
        #         {"role": "user", "content": prompt}
        #     ],
        #     stream=True
        # )


        return prompt
