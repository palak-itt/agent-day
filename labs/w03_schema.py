from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

class ActionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task: str = Field(description="A concrete next step, starting with a verb")
    owner: str = Field(description = "Person responsible, only if stated in the text")

class TicketInsight(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(description="One sentence summary, max 25 words")
    category: Literal["bug", "billing", "feature_request", "account", "other"]
    reasoning: str = Field(description="1-2 sentences: what is the core issue and how urgesnt is it?")

    priority: Literal["low", "medium", "high", "critical"]
    customer_email: Optional[str] = Field(None, description="Customer's email address, only if stated in the text")
    action_items: Optional[list[ActionItem]] = Field(default_factory=list)


    @field_validator('summary')
    @classmethod
    def short_summary(cls, v):
        if len(v.split()) > 25:
            raise ValueError("Summary must be 25 words or less")
        return v
# import json
# open("outputs/w03_schema.json", "w").write(json.dumps(TicketInsight.model_json_schema(), indent=2))
# print(json.dumps(TicketInsight.model_json_schema(), indent=2))