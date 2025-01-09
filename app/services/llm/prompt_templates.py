# -*- coding: utf-8 -*-
# @Time    : 2024/9/20 15:11
# @Author  : Galleons
# @File    : prompts_templates.py

"""
构建基于langchain.PromptTemplate的提示模板
"""

from abc import ABC, abstractmethod

from langchain.prompts import PromptTemplate
from pydantic import BaseModel
from app.services.llm.prompts import prompts

class BasePromptTemplate(ABC, BaseModel):
    @abstractmethod
    def create_template(self, *args) -> PromptTemplate:
        pass


class QueryExpansionTemplate(BasePromptTemplate):
    prompt: str = prompts.query_expansion

    @property
    def separator(self) -> str:
        return "#next-question#"

    def create_template(self, to_expand_to_n: int) -> PromptTemplate:
        return PromptTemplate(
            template=self.prompt,
            input_variables=["question"],
            partial_variables={
                "separator": self.separator,
                "to_expand_to_n": to_expand_to_n,
            },
        )


class SelfQueryTemplate(BasePromptTemplate):
    prompt: str  = prompts.self_query

    def create_template(self) -> PromptTemplate:
        return PromptTemplate(template=self.prompt, input_variables=["question"])


class RerankingTemplate(BasePromptTemplate):
    prompt: str  = prompts.reranking

    def create_template(self, keep_top_k: int) -> PromptTemplate:
        return PromptTemplate(
            template=self.prompt,
            input_variables=["question", "passages"],
            partial_variables={"keep_top_k": keep_top_k, "separator": self.separator},
        )

    @property
    def separator(self) -> str:
        return "\n#next-document#\n"


class InferenceTemplate(BasePromptTemplate):
    simple_prompt: str  = prompts.simple_prompt
    rag_prompt: str  = prompts.rag_prompt

    def create_template(self, enable_rag: bool = True) -> PromptTemplate:
        if enable_rag is True:
            return PromptTemplate(
                template=self.rag_prompt, input_variables=["question", "context"]
            )

        return PromptTemplate(template=self.simple_prompt, input_variables=["question"])


class LLMEvaluationTemplate(BasePromptTemplate):
    prompt: str  = prompts.llm_evaluation

    def create_template(self) -> PromptTemplate:
        return PromptTemplate(template=self.prompt, input_variables=["query", "output"])


class RAGEvaluationTemplate(BasePromptTemplate):
    prompt: str  = prompts.rag_evaluation

    def create_template(self) -> PromptTemplate:
        return PromptTemplate(
            template=self.prompt, input_variables=["query", "context", "output"]
        )
