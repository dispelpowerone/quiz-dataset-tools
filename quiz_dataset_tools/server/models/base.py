from pydantic import BaseModel


class DomainRequest(BaseModel):
    domain: str


class DomainResponse(BaseModel):
    error_code: int
