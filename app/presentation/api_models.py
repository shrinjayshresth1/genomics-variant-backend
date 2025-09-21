"""
API request and response models for the presentation layer.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.core.models import (
    VariantResult, ProcessingSummary, ClinVarStatus, 
    VariantClassification, VariantImpact
)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    components: Optional[Dict[str, str]] = Field(None, description="Component status")


class ProcessingResponse(BaseModel):
    """Response model for VCF processing endpoint."""
    success: bool = Field(..., description="Processing success status")
    message: str = Field(..., description="Processing message")
    total_variants: int = Field(..., description="Total number of variants processed")
    top_variants: List[VariantResult] = Field(..., description="Top variants by significance")
    summary: ProcessingSummary = Field(..., description="Processing summary statistics")


class ClassificationRulesResponse(BaseModel):
    """Response model for classification rules endpoint."""
    frequency_thresholds: Dict[str, float] = Field(..., description="Frequency thresholds")
    rules: List[Dict[str, str]] = Field(..., description="Classification rules")
    scoring_factors: Dict[str, Dict[str, Any]] = Field(..., description="Scoring factors")


class SupportedFormatsResponse(BaseModel):
    """Response model for supported formats endpoint."""
    supported_formats: List[str] = Field(..., description="List of supported file formats")


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error details")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: Optional[str] = Field(None, description="Error timestamp")
