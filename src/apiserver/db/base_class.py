from typing import Dict, Any
import datetime
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.sql import func

class_registry: Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    id: Any
    __name__: str
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    def to_dict(self):
        intermediate_dict = {}
        for field in self.__table__.c:
            value = getattr(self, field.name)
            if type(value) == datetime.datetime:
                value: datetime.datetime
                value = value.isoformat()
            intermediate_dict[field.name] = value
        return intermediate_dict
