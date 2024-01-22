import enum

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Table, BigInteger, Float, Boolean, Enum, Text, \
    Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, column_property

from apiserver.db.base_class import Base


class ProjectStatusEnum(str, enum.Enum):
    active = 'Active'
    delivered = 'Delivered'
    vendor_request_sent = 'Vendor Request Sent'
    closed = 'Closed'
    sold = 'Sold'
    lost = 'Lost'
    not_started = 'Not Started'


class CostBasisEnum(str, enum.Enum):
    one_week_media_cost = 'One Week Media Cost'
    two_week_media_cost = 'Two Week Media Cost'
    three_week_media_cost = 'Three Week Media Cost'
    four_week_media_cost = 'Four Week Media Cost'


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=False)
    password = Column(String(256), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)


class Vendor(Base):
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)
    emails = Column(JSONB)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    wilkins_id = Column(String(256), unique=True, index=True)
    name = Column(String(256), nullable=True)
    client = Column(String(256), nullable=True)
    status = Column(Enum(ProjectStatusEnum, name='project_status_enum'), nullable=False,
                    default=ProjectStatusEnum.active)
    budget = Column(Float, nullable=True)

    submissions = relationship("Submission", back_populates="project")
    project_vendors = relationship("ProjectVendor", back_populates="project")


class UserProject(Base):
    __tablename__ = "user_projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class ProjectVendor(Base):
    __tablename__ = 'project_vendors'

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    project = relationship("Project")

    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    vendor = relationship("Vendor")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(String(256), unique=True, nullable=False)
    unit = Column(String(256))

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", uselist=False)

    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    vendor = relationship("Vendor")

    town = Column(String(256))
    market = Column(String(256))
    state = Column(String(256))
    location_description = Column(Text)
    geopath_id = Column(String(512))
    target_location = Column(String(512))
    distance_to_location = Column(String(256))

    a18_weekly_impressions = Column(Integer)
    a18_4wk_reach = Column(Float)  # %
    a18_4wk_freq = Column(Float)

    size = Column(String(255))
    media_type = Column(String(64))
    facing = Column(String(16))
    is_illuminated = Column(Boolean, nullable=False, default=False)
    availability_start = Column(Date)
    availability_end = Column(Date)
    total_units = Column(Integer)

    one_week_media_cost = Column(Float)
    two_week_media_cost = Column(Float)
    three_week_media_cost = Column(Float)
    four_week_media_cost = Column(Float)

    installation_cost = Column(Float)
    markup_percentage = Column(Float)
    production_cost = Column(Float)
    is_prod_forced = Column(Boolean)
    taxes = Column(Float)

    four_week_rate_card = Column(Float)
    internal_four_week_media_cost = Column(Float)
    additional_installation_cost = Column(Float)
    initial_installation_cost = Column(Float)
    unit_highlights = Column(String(256))

    latitude = Column(Float)
    longitude = Column(Float)

    # for digital media
    no_of_spots_per_loop = Column(Float)
    spot_length_secs = Column(Float)

    user_locked = Column(Boolean, nullable=False, default=False)
    selected = Column(Boolean, nullable=False, default=False)

    raw_installation_cost = Column(String(32))
    raw_date = Column(String(64))

    no_of_periods = Column(Integer)

    image_id = Column(String(1024))

    cost_basis = Column(Enum(CostBasisEnum, name='cost_basis_enum'), nullable=False,
                        default=CostBasisEnum.four_week_media_cost, server_default=CostBasisEnum.four_week_media_cost)

    @hybrid_property
    def total_media_cost(self):
        if self.no_of_periods is not None and getattr(self, self.cost_basis.name) is not None:
            return self.no_of_periods * getattr(self, self.cost_basis.name)
        else:
            return None

    @hybrid_property
    def total_cost(self):
        if self.total_media_cost is not None and self.production_cost is not None and self.markup_percentage is not None:
            return self.total_media_cost + self.production_cost + (self.markup_percentage * self.total_media_cost)
        else:
            return None

