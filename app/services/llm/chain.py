from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate

#from langchain_core.output_parsers import StrOutputParser
#from langchain_core.prompts import PromptTemplate


class GeneralChain:
    @staticmethod
    def get_chain(llm, template: PromptTemplate, output_key: str, verbose=True):
        # TODO: 基于langchain——0.3 对链进行重构 （去掉对LLMChain的依赖）
        return LLMChain(
            llm=llm, prompt=template, output_key=output_key, verbose=verbose
        )
