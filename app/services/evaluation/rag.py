from langchain_openai import ChatOpenAI

import app.services.llm.prompt_templates as templates
from app.services.llm.chain import GeneralChain
from app.config import settings


def evaluate(query: str, context: list[str], output: str) -> str:
    evaluation_template = templates.RAGEvaluationTemplate()
    prompt_template = evaluation_template.create_template()


    model = ChatOpenAI(model=settings.Silicon_model_v1,openai_api_key=settings.Silicon_api_key1,openai_api_base=settings.Silicon_base_url,temperature=0)
    chain = GeneralChain.get_chain(
        llm=model, output_key="rag_eval", template=prompt_template
    )

    response = chain.invoke({"query": query, "context": context, "output": output})

    return response["rag_eval"]
