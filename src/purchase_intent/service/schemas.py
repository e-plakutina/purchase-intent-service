from pydantic import BaseModel, ConfigDict, Field


class Features(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Administrative: int = Field(ge=0, le=30)
    Administrative_Duration: float = Field(ge=0, le=3500)
    Informational: int = Field(ge=0, le=30)
    Informational_Duration: float = Field(ge=0, le=3000)
    ProductRelated: int = Field(ge=0, le=1000)
    ProductRelated_Duration: float = Field(ge=0, le=60000)
    BounceRates: float = Field(ge=0, le=1)
    ExitRates: float = Field(ge=0, le=1)
    PageValues: float | None = Field(default=None, ge=0, le=400)
    SpecialDay: float = Field(ge=0, le=1)
    Month: str
    OperatingSystems: int = Field(ge=1, le=8)
    Browser: int = Field(ge=1, le=13)
    Region: int = Field(ge=1, le=9)
    TrafficType: int = Field(ge=1, le=20)
    VisitorType: str
    Weekend: bool


class Prediction(BaseModel):
    score: float
    purchase: bool
    model_version: str
    request_id: str
