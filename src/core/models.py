"""Response models for consistent API responses."""

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    limit: int
    total: int
    total_pages: int


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope."""

    data: T
    pagination: Optional[PaginationMeta] = None


class ErrorDetail(BaseModel):
    """Error details."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    error: ErrorDetail
