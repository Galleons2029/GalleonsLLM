# -*- coding: utf-8 -*-
# @Time    : 2024/11/5 13:50
# @Author  : Galleons
# @File    : jobs.py

"""
这里是文件说明
"""

import datetime
from pydantic import BaseModel, Field, field_validator, ValidationInfo, ConfigDict
from typing import List, Optional
import time
from enum import IntEnum
from datetime import datetime

class JobStatus(IntEnum):
    """岗位状态枚举"""
    BLOCKED = -1  # 屏蔽
    ENDED = 0     # 已结束
    ACTIVE = 1    # 招聘中

class JobPracticeType(IntEnum):
    """实习类型枚举"""
    CAMPUS = 0    # 校招
    INTERN = 1    # 实习
    SOCIAL = 2    # 社招

class ExperienceLevel(IntEnum):
    """经验要求枚举"""
    NO_LIMIT = 1      # 不限
    UNDER_1_YEAR = 2  # 1年以下
    ONE_TO_3 = 3      # 1-3年
    THREE_TO_5 = 4    # 3-5年
    FIVE_TO_10 = 5    # 5-10年
    ABOVE_10 = 6      # 10年以上

class Jobs(BaseModel):
    """岗位数据模型"""
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        str_min_length=0,
        validate_default=True,
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    # 基础信息
    publish_id: int = Field(frozen=True, description="职位ID(不可更改)")
    company_id: int = Field(..., ge=0, description="企业ID")
    m_company_id: Optional[int] = Field(None, ge=0, description="合并后的单位ID")
    company_name: str = Field(default="未知", min_length=1, max_length=100, description="企业名称")
    job_id: Optional[int] = Field(None, ge=0, description="职位ID")
    
    # 时间相关
    end_time: int = Field(default=None, description="职位过期时间")
    create_time: Optional[int] = Field(default=None, description="创建时间")
    publish_time: Optional[int] = Field(default=None, description="发布时间")
    commend_time: Optional[int] = Field(default=None, description="推荐时间")
    modify_time: Optional[int] = Field(default=None,  description="修改时间")
    
    
    # 职位类型和状态
    is_practice: JobPracticeType = Field(default=JobPracticeType.CAMPUS, description="是否实习")
    is_zpj_job: Optional[str] = Field(None, description="招聘节职位")
    job_status: JobStatus = Field(..., description="岗位状态")
    job_type: bool = Field(..., description="职位类型：0.普通职位 1.平台职位")
    
    # 职位分类
    category: str = Field(..., min_length=1, description="职位类别")
    category_id: int = Field(..., gt=0, description="职位类别ID")
    parent_category: str = Field(..., min_length=1, description="父级职位类别")
    parent_category_id: int = Field(..., gt=0, description="父级职位类别ID")
    second_category: str = Field(..., min_length=1, description="二级职位分类")
    second_category_id: int = Field(..., gt=0, description="二级职位分类ID")
    edu_category: Optional[str] = Field(None, description="教育部职位分类")
    category_teacher_type: Optional[str] = Field(None, description="教师子类别")
    
    # 职位详情
    job_name: str = Field(..., min_length=1, max_length=100, description="职位名称")
    job_number: int = Field(ge=0, description="招聘人数")
    job_require: str = Field(..., min_length=0, description="职位要求")
    job_descript: str = Field(..., min_length=0, description="职位描述")
    job_desc: Optional[str] = Field(None, description="职位描述(备用)")
    job_other: Optional[str] = Field(None, description="职位其他描述")
    
    # 薪资福利
    salary: Optional[str] = Field(None, description="年薪，为空直接是面议")
    salary_min: int = Field(ge=0, description="薪资范围 - 最少")
    salary_max: int = Field(le=1000000, description="薪资范围 - 最多")
    biz_salary: Optional[str] = Field(None, description="运营填写的年薪字段")
    welfare: Optional[str] = Field(None, description="薪酬福利")
    amount_welfare_min: Optional[int] = Field(ge=0, default=0, description="福利金额最小值")
    amount_welfare_max: Optional[int] = Field(le=1000000, default=0, description="福利金额最大值")
    
    # 联系方式和地址
    contact_tel: Optional[str] = Field(None, description="联系电话")
    city_name: str = Field(default="未知", description="工作城市")
    work_address: Optional[str] = Field(None, description="工作地点")
    province: Optional[str] = Field(None, description="省份")
    
    # 要求和统计
    keywords: Optional[str] = Field(None, description="关键字(空格分开)")
    degree_require: Optional[str] = Field(None, description="学历要求")
    experience: Optional[ExperienceLevel] = Field(None, description="经验要求")
    about_major: Optional[str] = Field(..., description="相关专业")
    view_count: int = Field(default=0, ge=0, description="职位浏览数量")
    apply_count: int = Field(ge=0, description="收到简历数量")
    
    # 投递流程说明
    intro_apply: Optional[str] = Field(None, description="投递说明")
    intro_screen: Optional[str] = Field(None, description="筛选简历说明")
    intro_interview: Optional[str] = Field(None, description="面试说明")
    intro_sign: Optional[str] = Field(None, description="签约说明")
    
    # 来源信息
    source: Optional[str] = Field(None, description="来源：hr、school")
    source_school_id: Optional[int] = Field(None, gt=0, description="来源学校ID")
    source_school: Optional[str] = Field(None, description="来源学校名称")
    
    # 状态标记
    is_commend: Optional[bool] = Field(default=False, description="是否推荐")
    is_publish: bool = Field(..., description="是否发布：0下架 1上架")
    is_top: Optional[bool] = Field(default=False, description="是否置顶")
    time_type: Optional[str] = Field(None, description="工作时间类型")
    
    # HR信息
    publish_hr_id: Optional[int] = Field(None, description="HRID")
    publish_hr_openid: Optional[str] = Field(None, description="发布人HR的openid")
    create_by: Optional[int] = Field(None, description="创建人")
    modify_by: Optional[int] = Field(None, description="修改人")

    @field_validator('salary_max')
    def validate_salary_range(cls, v: int, info: ValidationInfo) -> int:
        """验证最高薪资必须大于最低薪资"""
        if v < info.data.get('salary_min', 0):
            raise ValueError("最高薪资必须大于最低薪资")
        return v

    @field_validator('end_time')
    def validate_end_time(cls, v: Optional[int]) -> Optional[int]:
        """验证结束时间必须大于当前时间"""
        if v and v < int(time.time()):
            raise ValueError("结束时间不能早于当前时间")
        return v

    # @field_validator('job_require', 'job_descript')
    # def validate_text_length(cls, v: str) -> str:
    #     """验证文本长度"""
    #     if len(v.strip()) < 10:
    #         raise ValueError("描述文本至少需要10个字符")
    #     return v.strip()

    def get_search_text(self) -> str:
        """获取用于搜索的文本组合"""
        search_fields = [
            self.job_name,
            self.job_descript,
            self.job_require,
            self.about_major,
            self.keywords or ""
        ]
        return " ".join(filter(None, search_fields))

class JobUpdateItem(BaseModel):
    """岗位更新请求项模型"""
    publish_id: int = Field(..., description="职位ID(必填)")
    company_id: Optional[int] = Field(None, description="企业ID")
    m_company_id: Optional[int] = Field(None, description="合并后的单位ID")
    company_name: Optional[str] = Field(None, description="企业名称")
    job_id: Optional[int] = Field(None, description="职位ID")
    end_time: Optional[int] = Field(None, description="职位过期时间")
    is_practice: Optional[int] = Field(None, ge=0, le=2, description="是否实习 0：校招 1：实习 2：社招")
    is_zpj_job: Optional[int] = Field(None, description="招聘节职位")
    apply_count: Optional[int] = Field(None, ge=0, description="收到简历数量")
    job_name: Optional[str] = Field(None, description="职位名称")
    edu_category: Optional[str] = Field(None, description="教育部职位分类")
    category: Optional[str] = Field(None, description="职位类别")
    category_id: Optional[int] = Field(None, description="职位类别ID")
    parent_category: Optional[str] = Field(None, description="父级职位类别")
    parent_category_id: Optional[int] = Field(None, description="父级职位类别ID")
    second_category: Optional[str] = Field(None, description="二级职位分类")
    second_category_id: Optional[int] = Field(None, description="二级职位分类ID")
    category_teacher_type: Optional[str] = Field(None, description="教师子类别")
    job_number: Optional[int] = Field(None, ge=0, description="招聘人数")
    job_status: Optional[int] = Field(None, description="1招聘中，0已结束，-1屏蔽")
    job_require: Optional[str] = Field(None, description="职位要求")
    job_descript: Optional[str] = Field(None, description="职位描述")
    salary: Optional[str] = Field(None, description="年薪，为空直接是面议")
    salary_min: Optional[int] = Field(None, ge=0, description="薪资范围 - 最少")
    salary_max: Optional[int] = Field(None, le=1000000, description="薪资范围 - 最多")
    contact_tel: Optional[str] = Field(None, description="联系电话")
    city_name: Optional[str] = Field(None, description="工作城市")
    work_address: Optional[str] = Field(None, description="工作地点")
    keywords: Optional[str] = Field(None, description="关键字 空格分开")
    welfare: Optional[str] = Field(None, description="薪酬福利")
    intro_apply: Optional[str] = Field(None, description="投递说明")
    intro_screen: Optional[str] = Field(None, description="筛选简历说明")
    intro_interview: Optional[str] = Field(None, description="面试说明")
    intro_sign: Optional[str] = Field(None, description="签约说明")
    source : Optional[str] = Field(None, description="来源：hr、school")
    province: Optional[str] = Field(None, description="省份")
    degree_require: Optional[str] = Field(None, description="学历要求")
    experience: Optional[str] = Field(None, description="经验要求")
    job_desc: Optional[str] = Field(None, description="职位描述")
    biz_salary: Optional[str] = Field(None, description="运营填写的年薪字段")
    about_major: Optional[str] = Field(None, description="相关专业")
    view_count: Optional[int] = Field(None, ge=0, description="职位浏览数量")
    job_other: Optional[str] = Field(None, description="职位其他描述")
    source_school_id: Optional[int] = Field(None, description="来源学校ID")
    source_school: Optional[str] = Field(None, description="来源学校名称")
    is_commend: Optional[bool] = Field(None, description="是否推荐")
    is_publish: Optional[bool] = Field(None, description="是否发布：0下架 1上架")
    commend_time : int | None = None
    amount_welfare_min: Optional[int] = Field(None, ge=0, description="福利金额最小值")
    amount_welfare_max: Optional[int] = Field(None, le=1000000, description="福利金额最大值")
    time_type: Optional[str] = Field(None, description="工作时间类型")
    is_top: Optional[bool] = Field(None, description="是否置顶")
    job_type: Optional[bool] = Field(None, description="职位类型： 0.普通职位 1.平台职位")
    create_time: int | None = None
    modify_by: int | None = None
    modify_time: int | None = None
    is_default: int | None = None
    company_id_bak: int | None = None
    removed: int | None = None
    publish_hr_id: Optional[int] = Field(None, description="HRID，如果是PC端，没有openid")
    publish_hr_openid: Optional[str] = Field(None, description="发布人HR的openid")
    publish_time: Optional[int] = Field(None, description="发布时间")

    # @field_validator('end_time')
    # def validate_end_time(cls, v):
    #     if v is not None:
    #         current_time = int(time.time())
    #         if v < current_time:
    #             raise ValueError("结束时间不能早于当前时间")
    #     return v

    @field_validator('salary_min', 'salary_max')
    def validate_salary_range(cls, value: Optional[int], info: ValidationInfo) -> Optional[int]:
        """验证薪资范围
        
        Args:
            value: 当前字段的值
            info: 包含验证上下文的信息对象
        """
        if value is not None:
            field_name = info.field_name
            if field_name == 'salary_max' and info.data.get('salary_min') is not None:
                salary_min = info.data['salary_min']
                if value < salary_min:
                    raise ValueError("最高薪资不能低于最低薪资")
        return value

    def get_non_none_fields(self) -> dict:
        """获取所有非None的字段值"""
        return {
            field: value
            for field, value in self.model_dump().items()
            if value is not None
        }



class CareerTalk(BaseModel):
    career_talk_id: int
    company_id: int

# 宣讲会职位
class Career_talk(BaseModel):
    school_id: str | int
    student_key: str
    career_talk: List[CareerTalk]

class Response_CareerTalk(BaseModel):
    career_talk_id: int
    job_id: List[int]




"""
双选会
"""

# 定义 JobFair 模型
class JobFair(BaseModel):
    fair_id: int                 # 双选会ID
    company_id: List[int]         # 公司ID列表

# 定义 Career 模型
class Career(BaseModel):
    career_talk_id: int           # 宣讲会ID

# 定义主模型
class JobRequestModel(BaseModel):
    # student_key: str | int | None = None
    # desire_industry: str          # 期行业
    # attribute: str                # 单位性质
    # category: str                 # 岗位类型
    # second_category: str          # 职位分类
    # cities: str                   # 工作地点
    # desire_salary: str            # 期望薪水
    # major: str                    # 专业名称
    # fair_id: str                  # 双选会
    # fair_company_id: str
    # career: Optional[List[Career]] = []  # 宣讲会 (可选,默认为空列表)
    student_key: str | int = None
    desire_industry: str
    attribute: str
    category: str
    second_category: str
    cities: str
    desire_salary: str
    major: str
    fair_id: str | int
    fair_company_id: str

    # {
    #     "student_key": "2c88bb981ed75e870ce26cd4996765e2",
    #     "desire_industry": "电力、热力、燃气及水生产和供应业+信息传输、软件和信息技术服务业",
    #     "attribute": "高等教育单位+民营企业",
    #     "category": "全职+全职",
    #     "second_category": "销售总监+高级软件工程师",
    #     "cities": "天津市+长沙市",
    #     "desire_salary": "3k-3k+5k-9k",
    #     "major": "纺织工程",
    #     "fair_id": 9104,
    #     "fair_company_id": "486217,507755"
    # }

class Bilateral_record(BaseModel):
    apply_job_id: str | int = Field(..., alias='jobfair_apply_job_id')
    recruit_guid: str
    apply_id: int
    school_id: int
    fair_id: int
    company_id: int
    income_id: int
    publish_id: int
    is_registered: str | bool = Field(..., alias='is_regist')
    is_income: str | bool
    is_sign_up: int
    create_time: int
    create_by: int
    modify_timestamp: str | None = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class BilateralCollection(BaseModel):
    """
    一个容器，包含多个 `StudentModel` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    data: List[Bilateral_record]



class Bilateral_delete_record(BaseModel):
    fair_id: str | int = Field(..., alias='jobfair_apply_job_id')
    publish_id: List[int]

    class Config:
        populate_by_name = True


class BilateralDeleteCollection(BaseModel):
    """
    一个容器，包含多个 `StudentModel` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    data: List[Bilateral_delete_record]



class CareerTalkRecord(BaseModel):
    recruit_guid: str | None = None  # Nullable or Optional UUID if not provided
    career_talk_id: str | int
    school_id: str | int
    company_id: str | int
    income_id: str | int
    publish_id: str | int
    is_registered: str | bool = Field(..., alias='is_regist')
    is_income: str | int
    is_sign_up: str | int
    create_time: str | int
    create_by: str | int
    career_talk_job_id: str | int | None = None
    # m_company_id: str | int | None = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        # orm_mode = True




class CareerTalkCollection(BaseModel):
    """
    一个容器，包含多个 `CareerTalkRecord` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    data: List[CareerTalkRecord]



class CareerTalkDelete(BaseModel):
    career_talk_id: str | int = Field(..., alias='career_id')
    publish_id: List[int]

    class Config:
        populate_by_name = True


class CareerTalkDeleteCollection(BaseModel):
    """
    一个容器，包含多个 `StudentModel` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    data: List[CareerTalkDelete]



class DeletePayloadRequest(BaseModel):
    """删除请求的基础模型

    Examples:
        >>> # 删除宣讲会记录
        >>> {"publish_ids": [1, 2, 3], "meeting_id": 123, "meeting_type": "career_talk"}
        >>> # 删除双选会记录
        >>> {"publish_ids": [1, 2, 3], "meeting_id": 456, "meeting_type": "fair"}
    """
    publish_ids: List[int]
    meeting_id: int = Field(..., description="宣讲会ID(career_talk_id)或双选会ID(fair_id)")
    meeting_type: str = Field(..., description="会议类型", pattern="^(career_talk|fair)$")

class MeetingDeleteCollection(BaseModel):
    """
    一个容器，包含多个删除请求实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    data: List[DeletePayloadRequest]
