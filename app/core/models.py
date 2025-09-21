"""
Core domain models for the genomic VCF processing application.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ClinVarStatus(str, Enum):
    """ClinVar clinical significance status."""
    PATHOGENIC = "Pathogenic"
    LIKELY_PATHOGENIC = "Likely Pathogenic"
    UNCERTAIN = "Uncertain Significance"
    LIKELY_BENIGN = "Likely Benign"
    BENIGN = "Benign"
    CONFLICTING = "Conflicting Interpretations"


class VariantClassification(str, Enum):
    """ACMG-inspired variant classification."""
    LIKELY_PATHOGENIC = "Likely Pathogenic"
    LIKELY_BENIGN = "Likely Benign"
    UNCERTAIN = "Uncertain"


class VariantImpact(str, Enum):
    """Variant impact levels."""
    HIGH = "HIGH"
    MODERATE = "MOD"
    LOW = "LOW"
    MODIFIER = "MODIFIER"


class Variant(BaseModel):
    """Individual variant data model."""
    chrom: str = Field(..., description="Chromosome")
    pos: int = Field(..., description="Position")
    variant_id: str = Field(..., description="Variant ID (rs number or custom)")
    ref: str = Field(..., description="Reference allele")
    alt: str = Field(..., description="Alternate allele")
    gene: Optional[str] = Field(None, description="Gene name")
    impact: Optional[VariantImpact] = Field(None, description="Variant impact")
    quality: Optional[float] = Field(None, description="Variant quality score")
    filter_status: Optional[str] = Field(None, description="Filter status")
    clinical: Optional[str] = Field(None, description="Clinical significance")


class VariantWithClassification(BaseModel):
    """Variant with classification data."""
    variant: Variant
    clinvar_status: ClinVarStatus
    population_frequency: float = Field(..., ge=0.0, le=1.0, description="Population frequency (0-1)")
    classification: VariantClassification
    significance_score: float = Field(..., description="Calculated significance score")


class VariantResult(BaseModel):
    """Result for a single classified variant."""
    variant_id: str
    gene: Optional[str]
    chrom: str
    pos: int
    ref: str
    alt: str
    clinvar_status: ClinVarStatus
    population_frequency: float
    classification: VariantClassification
    significance_score: float
    impact: Optional[VariantImpact]
    clinical: Optional[str]


class ProcessingSummary(BaseModel):
    """Summary statistics for processed variants."""
    total_variants: int
    pathogenic_variants: int
    benign_variants: int
    uncertain_variants: int
    high_impact_variants: int
    drug_response_variants: int
    unique_genes: int


class ProcessingResponse(BaseModel):
    """Response model for VCF processing endpoint."""
    success: bool
    message: str
    total_variants: int
    top_variants: List[VariantResult]
    summary: ProcessingSummary
