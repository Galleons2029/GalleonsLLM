from langchain_openai import ChatOpenAI
from app.services.llm.chain import GeneralChain
from app.services.llm.prompt_templates import SelfQueryTemplate
from app.config import settings


class SelfQuery:
    @staticmethod
    def generate_response(query: str) -> str | None:
        prompt = SelfQueryTemplate().create_template()
        model = ChatOpenAI(
            model=settings.Silicon_model_mini,
            openai_api_key=settings.Silicon_api_key1,
            openai_api_base=settings.Silicon_base_url,
            temperature=0
        )

        chain = GeneralChain().get_chain(
            llm=model, output_key="metadata_filter_value", template=prompt
        )

        response = chain.invoke({"question": query})
        result = response.get("metadata_filter_value", "none")

        if result.lower() == "none":
            return None

        return result
