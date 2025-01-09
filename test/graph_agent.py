from getpass import getpass
from langchain_openai import ChatOpenAI

# OPENAI_API_KEY = getpass()

import os

# os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# OPENAI_API_SECRET = getpass()
# os.environ['OPENAI_API_SECRET'] = OPENAI_API_SECRET
os.environ['api_key'] = "sk-orbrjhjcqmgezlurbvsmfxqmnjwkmjdrypwdiwvyfarkbnag"
os.environ['base_url'] = "https://api.siliconflow.cn/v1"

os.environ["OPENAI_API_BASE"] = "http://192.168.100.111:9997/v1/"
os.environ["OPENAI_API_KEY"] = "xxx"
os.environ["TAVILY_API_KEY"] = "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"  # 官网注册获取key

from openai import OpenAI
from langchain_core.prompts import PromptTemplate

# from langchain_openai import OpenAI


client = OpenAI(api_key="sk-orbrjhjcqmgezlurbvsmfxqmnjwkmjdrypwdiwvyfarkbnag", base_url="https://api.siliconflow.cn/v1")

chat_completion = client.chat.completions.create(
    model='THUDM/glm-4-9b-chat',
    messages=[{"role": "user", "content": "Hello world"}]
)

llm = ChatOpenAI(model="qwen2", max_tokens=100, max_retries=2)


class Agent:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = client.chat.completions.create(
            model='THUDM/glm-4-9b-chat',
            # model='Qwen/Qwen2-7B-Instruct',
            temperature=0,
            messages=self.messages)
        return completion.choices[0].message.content



prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

average_dog_weight:
e.g. average_dog_weight: Collie
returns average weight of a dog when given the breed

Example session:

Question: How much does a Bulldog weigh?
Thought: I should look the dogs weight using average_dog_weight
Action: average_dog_weight: Bulldog
PAUSE

You will be called again with this:

Observation: A Bulldog weights 51 lbs

You then output:

Answer: A bulldog weights 51 lbs
""".strip()


def calculate(what):
    return eval(what)


def average_dog_weight(name):
    if name in "Scottish Terrier":
        return ("Scottish Terriers average 20 lbs")
    elif name in "Border Collie":
        return ("a Border Collies average weight is 37 lbs")
    elif name in "Toy Poodle":
        return ("a toy poodles average weight is 7 lbs")
    else:
        return ("An average dog weights 50 lbs")


known_actions = {
    "calculate": calculate,
    "average_dog_weight": average_dog_weight
}

abot = Agent(prompt)

result = abot("How much does a toy poodle weigh?")
print(result)