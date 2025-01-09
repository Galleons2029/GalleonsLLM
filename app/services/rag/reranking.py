from langchain_openai import ChatOpenAI

from app.services.llm.chain import GeneralChain
from app.services.llm.prompt_templates import RerankingTemplate
from app.config import settings
import requests
import json
import os

class Reranker:
    @staticmethod
    def generate_response(
        query: str, passages: list[str], keep_top_k: int
    ) -> list[str]:
        # reranking_template = RerankingTemplate()
        # prompt_template = reranking_template.create_template(keep_top_k=keep_top_k)
        #
        # model = ChatOpenAI(
        #     model=settings.Silicon_model_v1,
        #     openai_api_key=settings.Silicon_api_key1,
        #     openai_api_base=settings.Silicon_base_url,
        #     temperature=0
        # )
        # chain = GeneralChain().get_chain(
        #     llm=model, output_key="rerank", template=prompt_template
        # )
        #
        # stripped_passages = [
        #     stripped_item for item in passages if (stripped_item := item.strip())
        # ]
        # passages = reranking_template.separator.join(stripped_passages)
        # response = chain.invoke({"question": query, "passages": passages})
        #
        # result = response["rerank"]
        # reranked_passages = result.strip().split(reranking_template.separator)
        # stripped_passages = [
        #     stripped_item
        #     for item in reranked_passages
        #     if (stripped_item := item.strip())
        # ]

        payload = {
            "model": settings.Silicon_model_rerank,
            "query": query,
            "documents": passages,
            "top_n": keep_top_k,
            "return_documents": False,
            "max_chunks_per_doc": 1024,
            "overlap_tokens": 80
        }

        headers = {
            "Authorization": f"Bearer {settings.Silicon_api_key1}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            os.path.join(settings.Silicon_base_url, 'rerank'),
            json=payload,
            headers=headers)
        response_data = json.loads(response.text)

        # Sort passages based on reranking results
        ranked_indices = [result["index"] for result in response_data["results"]]
        reranked_passages = [passages[idx] for idx in ranked_indices]

        return reranked_passages


if __name__ == "__main__":
    query = "苹果"
    passages = ["苹果", "香蕉", "水果", "蔬菜"]
    keep_top_k = 4
    reranked_passages = Reranker.generate_response(query, passages, keep_top_k)
    print(reranked_passages)