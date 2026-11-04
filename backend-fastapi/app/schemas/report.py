from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class GrammarIssue(BaseModel):
    original: str = Field(..., description="用户原句")
    corrected: str = Field(..., description="修正后")
    reason: str = Field(..., description="中文说明")


class VocabSuggestion(BaseModel):
    word: str = Field(..., description="英文单词或短语")
    meaning: str = Field(..., description="中文释义")
    example: str = Field(..., description="英文例句")


class ExpressionUpgrade(BaseModel):
    original: str = Field(..., description="用户原表达")
    upgraded: str = Field(..., description="升级后的表达")
    reason: str = Field(..., description="中文理由")


class TaskCompletion(BaseModel):
    goal_achieved: bool = Field(..., description="是否达成核心目标")
    score: int = Field(..., ge=0, le=100, description="任务完成度得分")
    comment: str = Field(..., description="中文评语")


class FeedbackResult(BaseModel):
    grammar_issues: List[GrammarIssue] = Field(default_factory=list)
    vocab_suggestions: List[VocabSuggestion] = Field(default_factory=list)
    expression_upgrades: List[ExpressionUpgrade] = Field(default_factory=list)
    task_completion: TaskCompletion
    overall_score: int = Field(..., ge=0, le=100)
    summary: str = Field(..., max_length=500)


class ReportOut(BaseModel):
    id: int
    session_id: int
    user_id: int
    grammar_issues: list
    vocab_suggestions: list
    expression_upgrades: list
    task_completion: dict
    overall_score: int
    summary: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VocabOut(BaseModel):
    id: int
    word: str
    meaning: str
    example: str
    review_count: int
    mastered: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MistakeOut(BaseModel):
    id: int
    original: str
    corrected: str
    reason: str
    category: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)