from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr

from apiserver.models import ProjectStatusEnum, CostBasisEnum


class RequestBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Token(BaseModel):
    access_token: str
    token_type: str


class UserAuthenticate(BaseModel):
    email: str
    password: str


class UserSchema(BaseModel):
    user_id: int
    name: str
    email: str
    is_admin: bool


class SignInResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserSchema


class SubmissionSchema(BaseModel):
    vendor: str
    unit: str
    project: "ProjectSchema"


class ProjectCreateIn(RequestBaseSchema):
    wilkins_id: str
    name: Optional[str] = None
    client: Optional[str] = None
    status: ProjectStatusEnum = ProjectStatusEnum.active
    budget: Optional[float] = None


class ProjectOut(BaseModel):
    wilkins_id: str
    name: Optional[str]
    client: Optional[str]
    status: ProjectStatusEnum
    budget: Optional[float]


class ProjectUpdateIn(RequestBaseSchema):
    name: Optional[str]
    client: Optional[str]
    status: ProjectStatusEnum
    budget: Optional[float]


class ProjectStats(RequestBaseSchema):
    project_name: str
    vendors_in_project: int
    vendors_in_submission: int
    sites: int
    total_budget: Optional[float]
    selected: int
    impressions: Optional[int]
    cpm: float
    estimated_budget: float


class VendorCreateRequestSchema(RequestBaseSchema):
    name: str
    emails: List[EmailStr] = []


class VendorCreateResponseSchema(RequestBaseSchema):
    name: str
    emails: List[EmailStr]


class UserCreateRequestSchema(RequestBaseSchema):
    name: str
    email: EmailStr
    password: str
    is_admin: Optional[bool]


class UserCreateResponseSchema(BaseModel):
    name: str
    email: EmailStr
    is_admin: bool


class Vendor(BaseModel):
    name: str


class SubmissionBase(BaseModel):
    unit: Optional[str] = None
    town: Optional[str] = None
    state: Optional[str] = None
    market: Optional[str] = None
    location_description: Optional[str] = None
    geopath_id: Optional[str] = None
    target_location: Optional[str] = None
    a18_weekly_impressions: Optional[int] = None
    a18_4wk_reach: Optional[float] = None
    a18_4wk_freq: Optional[float] = None
    availability_start: Optional[date] = None
    availability_end: Optional[date] = None
    total_units: Optional[int] = None
    installation_cost: Optional[float] = None
    markup_percentage: Optional[float] = None
    is_prod_forced: Optional[bool] = False
    taxes: Optional[float] = None
    four_week_rate_card: Optional[float] = None
    internal_four_week_media_cost: Optional[float] = None
    additional_installation_cost: Optional[float] = None
    unit_highlights: Optional[str] = None
    no_of_spots_per_loop: Optional[float] = None
    spot_length_secs: Optional[float] = None
    distance_to_location: Optional[str] = None
    media_type: Optional[str] = None
    facing: Optional[str] = None
    is_illuminated: Optional[bool] = False
    one_week_media_cost: Optional[float] = None
    two_week_media_cost: Optional[float] = None
    three_week_media_cost: Optional[float] = None
    four_week_media_cost: Optional[float] = None
    initial_installation_cost: Optional[float] = None
    production_cost: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    size: Optional[str] = None
    raw_installation_cost: Optional[str] = None
    raw_date: Optional[str] = None
    no_of_periods: Optional[int] = None
    image_id: Optional[str] = None
    cost_basis: CostBasisEnum = CostBasisEnum.four_week_media_cost


class SubmissionCreateIn(RequestBaseSchema, SubmissionBase):
    unit_id: str
    vendor: str
    vendor_email: Optional[EmailStr] = None


class SubmissionCreateOut(SubmissionBase):
    unit_id: str
    vendor: Vendor
    selected: bool


class SubmissionUpdateIn(RequestBaseSchema, SubmissionBase):
    pass


class SubmissionUpdateOut(SubmissionCreateOut):
    pass


class ProjectSchema(BaseModel):
    wilkins_id: str
    name: Optional[str] = None
    client: Optional[str] = None
    status: ProjectStatusEnum
    budget: Optional[float] = None
    vendors: List[str]


class FetchAllProjectsSchema(BaseModel):
    data: List[ProjectSchema]
    total_records: int


class FetchSubmissionSchema(SubmissionBase):
    unit_id: str
    vendor: str
    selected: bool
    image_url: Optional[str]


class ProjectSubmissionsSchema(BaseModel):
    data: List[FetchSubmissionSchema]
    total_records: int


class SelectedSubmissionIn(RequestBaseSchema):
    unit_ids: List[str]
    selected: bool


class SelectedSubmissionOut(BaseModel):
    selected: int
    impressions: Optional[int]
    cpm: float
    estimated_budget: float


SubmissionSchema.model_rebuild()
