from langchain_openai import ChatOpenAI

from app.services.llm.chain import GeneralChain
from app.services.llm.prompt_templates import LLMEvaluationTemplate
from app.config import settings


def evaluate(query: str, output: str) -> str:
    evaluation_template = LLMEvaluationTemplate()
    prompt_template = evaluation_template.create_template()

    model = ChatOpenAI(model=settings.Silicon_model_v1,openai_api_key=settings.Silicon_api_key1,openai_api_base=settings.Silicon_base_url,temperature=0)
    chain = GeneralChain.get_chain(
        llm=model, output_key="evaluation", template=prompt_template
    )

    response = chain.invoke({"query": query, "output": output})

    return response["evaluation"]
