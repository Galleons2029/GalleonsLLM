from langchain_openai import ChatOpenAI

from app.services.llm.chain import GeneralChain
from app.services.llm.prompt_templates import QueryExpansionTemplate
from app.config import settings


class QueryExpansion:
    @staticmethod
    def generate_response(query: str, to_expand_to_n: int = 3) -> list[str]:
        query_expansion_template = QueryExpansionTemplate()
        prompt_template = query_expansion_template.create_template(to_expand_to_n)
        model = ChatOpenAI(
            model="qwen2-mini1",
            openai_api_key='empty',
            openai_api_base="http://192.168.100.111:8011/v1",
            # temperature=0
        )

        chain = GeneralChain().get_chain(
            llm=model, output_key="expanded_queries", template=prompt_template
        )

        response = chain.invoke({"question": query})
        result = response["expanded_queries"]

        queries = result.strip().split(query_expansion_template.separator)
        stripped_queries = [
            stripped_item for item in queries if (stripped_item := item.strip())
        ]

        return stripped_queries
