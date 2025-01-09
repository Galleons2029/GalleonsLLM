from typing import Optional, List
from datetime import datetime
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId
from uuid import uuid4


class JobInModel(BaseModel):
    """
    输入上下文以及需要解析的文本描述的容器。
    """

    #id: Optional[PyObjectId] = Field(alias="_id", default=None)
    #job_name: str = Field(...)
    company_name: str = Field(...)
    #position_name: str = Field(...)
    companyIntro: str = Field(...)
    positionIntro: str = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "company_name": "长沙市云研网络科技有限公司",
                #"position_name": "PHP开发工程师",
                "companyIntro": """云研科技稳中前进，不断发展，顺应“互联网+”时代潮流，积极推进就业工作。为高校打造移动化、智能化、精准化的“互联网+就业”平台，以实际行动践行 “创新引领创业，创业带动就业”。
        公司致力于：
         · 用互联网思维优化就业方式
         · 用大数据平台指引就业服务
         · 用精准服务帮助天下毕业生走稳求职第一步
        云就业创新性：
         · 配置型SaaS模式高校就业云平台
         · 大型招聘会实时数据分析平台
         · 校园招聘单位诚信评估体系
         · 高校O2O线上招聘会
         · 高校云宣讲直播平'""",
                "positionIntro": """'PHP开发工程师 8000左右，长沙市 本科 2人 人工智能，计算机类，计算机科学与技术，软件工程，物联网工程，电子与计算机工程，数据科学与大数据技术
        公司福利：年底双薪 绩效奖金 岗前培训 节日礼物 扁平管理
        岗位职责
        1、独立或者分组进行针对项目需求的功能开发和优化；
        2、对现有产品进行二次开发；
        3、根据项目开发进度和任务分配，开发相应的模块；
        4、根据需要不断修改完善项目功能
        5、深入理解产品原型，保持与产品人员的随时沟通，不断改进产品功能流程或逻辑；
        6、解决项目开发过程中遇到的技术和业务问题。
        简历投递说明
        简历投递邮箱123123123123@qq.com，联系电话：13612345678
        岗位要求
        1、熟悉掌握php，有良好的编程规范，熟悉掌握Thinkphp、Larvel中的任意一种框架；
        2、熟悉MySQL，能独立设计良好的数据库结构，懂SQL优化；
        3、熟悉使用redis等nosql技术；
        4、熟悉linux开发环境，熟悉LNMP环境搭建及设置；
        5、计算机相关专业本科以上学历，两年以上后端研发工作经验优先；
        6、熟悉swoole协程方式开发，有hyperf框架开发经验优先；
        7、应届本科及以上毕业，有物联网开发经验或大数据分析经验优先；'。""",
            }
        },
    )


class JobOutModel(BaseModel):
    """
    单个职位描述的容器。
    """

    # 职位模型的主键，存储为实例上的 `str`。
    # 这将在发送到 MongoDB 时别名为 `_id`，
    # 但在 API 请求和响应中提供为 `id`。
    #id: Optional[PyObjectId] = Field(alias="_id", default=None)
    job_name: str = Field(...)
    parent_category: str = Field(...)
    second_category: str = Field(...)
    province: str = Field(...)
    cities: str = Field(...)
    attribute: str = Field(...)
    education: str = Field(...)
    salary: str = Field(...)
    about_major: str = Field(...)
    number: int = Field(..., gt=0)
    tempt: str = Field(...)

    duty: str = Field(...)
    explain: str = Field(...)
    requirements: str = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "job_name": "营养师",
                "parent_category": "生物/制药/医疗/护理",
                "second_category": "医院/医疗",
                "cities": "长沙市",
                "attribute": "校招",
                "education": "本科及以上",
                "salary": "长沙市",
                "about_major": "经济学",
                "number": 5,
            }
        },
    )

class Job2StudentModel(BaseModel):
    """
    单个职位描述的容器。
    """

    # 职位模型的主键，存储为实例上的 `str`。
    # 这将在发送到 MongoDB 时别名为 `_id`，
    # 但在 API 请求和响应中提供为 `id`。
    # id: Optional[PyObjectId] = Field(alias="_id", default=None)
    desire_industry: str = Field(...)
    attribute: str = Field(...)
    category: str = Field(...)
    second_category: str = Field(...)
    cities: str = Field(...)
    desire_salary: str = Field(...)
    reason: str | None = None
    # about_major: str = Field(...)
    # number: int = Field(..., gt=0)
    # tempt: str = Field(...)

    # duty: str = Field(...)
    # explain: str = Field(...)
    # requirements: str = Field(...)

    # model_config = ConfigDict(
    #     populate_by_name=True,
    #     arbitrary_types_allowed=True,
    #     json_schema_extra={
    #         "example": {
    #             "job_name": "营养师",
    #             "parent_category": "生物/制药/医疗/护理",
    #             "second_category": "医院/医疗",
    #             "cities": "长沙市",
    #             "attribute": "校招",
    #             "education": "本科及以上",
    #             "salary": "长沙市",
    #             "about_major": "经济学",
    #             "number": 5,
    #         }
    #     },
    # )

class Major2StudentModel(BaseModel):
    """
    单个职位描述的容器。
    """

    # 职位模型的主键，存储为实例上的 `str`。
    # 这将在发送到 MongoDB 时别名为 `_id`，
    # 但在 API 请求和响应中提供为 `id`。
    # id: Optional[PyObjectId] = Field(alias="_id", default=None)
    # desire_industry: str = Field(...)
    # attribute: str = Field(...)
    # category: str = Field(...)
    # second_category: str = Field(...)
    # cities: str = Field(...)
    # desire_salary: str = Field(...)
    major: str = Field(...)

    reason: str | None = None



class Double_choose(BaseModel):
    """
    单个岗位对象
    """
    desire_industry : str = Field(default_factory=lambda: uuid4().hex,)
    attribute : str = Field(frozen=True)       # 职位id(不可更改）
    category : str = Field(...)               # 企业id


class QueryRequest(BaseModel):
    collection_name: str = 'jobs'
    content : str
    is_vector : bool = True
    top_k : int = 10
    filtered : dict = None
