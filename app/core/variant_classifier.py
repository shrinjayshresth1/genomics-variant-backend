"""
Core business logic for variant classification using ACMG-inspired rules.
"""

import logging
from typing import List, Dict, Any

from app.core.models import (
    Variant, VariantWithClassification, VariantClassification, 
    ClinVarStatus, VariantImpact, VariantResult, ProcessingSummary
)
from app.infrastructure.data_repository import ClinicalDataRepository

logger = logging.getLogger(__name__)

# ACMG-inspired classification thresholds
FREQUENCY_THRESHOLD_PATHOGENIC = 0.01  # 1%
FREQUENCY_THRESHOLD_BENIGN = 0.05      # 5%


class VariantClassifier:
    """Handles variant classification using ACMG-inspired rules."""
    
    def __init__(self, data_repository: ClinicalDataRepository):
        """
        Initialize the variant classifier.
        
        Args:
            data_repository: Repository for clinical data
        """
        self.data_repository = data_repository

    def classify_variants(self, variants: List[Variant]) -> List[VariantWithClassification]:
        """
        Classify variants using ACMG-inspired rules.
        
        Args:
            variants: List of parsed variants
            
        Returns:
            List[VariantWithClassification]: Classified variants
        """
        classified_variants = []
        
        for variant in variants:
            try:
                classified_variant = self._classify_single_variant(variant)
                if classified_variant:
                    classified_variants.append(classified_variant)
            except Exception as e:
                logger.warning(f"Error classifying variant {variant.variant_id}: {str(e)}")
                continue
        
        logger.info(f"Successfully classified {len(classified_variants)} variants")
        return classified_variants

    def _classify_single_variant(self, variant: Variant) -> VariantWithClassification:
        """
        Classify a single variant using ACMG-inspired rules.
        
        Args:
            variant: Variant to classify
            
        Returns:
            VariantWithClassification: Classified variant
        """
        # Get ClinVar status and population frequency
        clinvar_status, population_frequency = self.data_repository.get_variant_annotation(variant.variant_id)
        
        # Apply ACMG-inspired classification rules
        classification = self._apply_acmg_rules(clinvar_status, population_frequency, variant)
        
        # Calculate significance score
        significance_score = self._calculate_significance_score(
            variant, clinvar_status, population_frequency, classification
        )
        
        return VariantWithClassification(
            variant=variant,
            clinvar_status=clinvar_status,
            population_frequency=population_frequency,
            classification=classification,
            significance_score=significance_score
        )

    def _apply_acmg_rules(
        self,
        clinvar_status: ClinVarStatus, 
        population_frequency: float, 
        variant: Variant
    ) -> VariantClassification:
        """
        Apply ACMG-inspired classification rules.
        
        Rules:
        1. If frequency < 0.01 and ClinVar is Pathogenic: classify as "Likely Pathogenic"
        2. If frequency > 0.05: classify as "Likely Benign"
        3. Else: classify as "Uncertain"
        
        Args:
            clinvar_status: ClinVar clinical significance
            population_frequency: Population frequency (0-1)
            variant: Variant information
            
        Returns:
            VariantClassification: Classification result
        """
        # Rule 1: Pathogenic variants with low frequency
        if (population_frequency < FREQUENCY_THRESHOLD_PATHOGENIC and 
            clinvar_status in [ClinVarStatus.PATHOGENIC, ClinVarStatus.LIKELY_PATHOGENIC]):
            return VariantClassification.LIKELY_PATHOGENIC
        
        # Rule 2: High frequency variants (likely benign)
        if population_frequency > FREQUENCY_THRESHOLD_BENIGN:
            return VariantClassification.LIKELY_BENIGN
        
        # Rule 3: Additional pathogenic criteria
        if self._has_pathogenic_criteria(variant, clinvar_status, population_frequency):
            return VariantClassification.LIKELY_PATHOGENIC
        
        # Rule 4: Additional benign criteria
        if self._has_benign_criteria(variant, clinvar_status, population_frequency):
            return VariantClassification.LIKELY_BENIGN
        
        # Default: Uncertain
        return VariantClassification.UNCERTAIN

    def _has_pathogenic_criteria(
        self,
        variant: Variant, 
        clinvar_status: ClinVarStatus, 
        population_frequency: float
    ) -> bool:
        """
        Check for additional pathogenic criteria.
        
        Args:
            variant: Variant information
            clinvar_status: ClinVar status
            population_frequency: Population frequency
            
        Returns:
            bool: True if pathogenic criteria are met
        """
        # High impact variants with low frequency
        if (variant.impact == VariantImpact.HIGH and 
            population_frequency < FREQUENCY_THRESHOLD_PATHOGENIC):
            return True
        
        # Cancer risk genes with pathogenic ClinVar status
        if (self.data_repository.is_cancer_risk_variant(variant.gene) and 
            clinvar_status in [ClinVarStatus.PATHOGENIC, ClinVarStatus.LIKELY_PATHOGENIC]):
            return True
        
        # Pharmacogenomic variants with known clinical significance
        if (self.data_repository.is_pharmacogenomic_variant(variant.gene) and 
            variant.clinical and 
            population_frequency < FREQUENCY_THRESHOLD_PATHOGENIC):
            return True
        
        return False

    def _has_benign_criteria(
        self,
        variant: Variant, 
        clinvar_status: ClinVarStatus, 
        population_frequency: float
    ) -> bool:
        """
        Check for additional benign criteria.
        
        Args:
            variant: Variant information
            clinvar_status: ClinVar status
            population_frequency: Population frequency
            
        Returns:
            bool: True if benign criteria are met
        """
        # Benign ClinVar status
        if clinvar_status in [ClinVarStatus.BENIGN, ClinVarStatus.LIKELY_BENIGN]:
            return True
        
        # Low impact variants with moderate frequency
        if (variant.impact in [VariantImpact.LOW, VariantImpact.MODIFIER] and 
            population_frequency > 0.02):
            return True
        
        return False

    def _calculate_significance_score(
        self,
        variant: Variant,
        clinvar_status: ClinVarStatus,
        population_frequency: float,
        classification: VariantClassification
    ) -> float:
        """
        Calculate significance score for variant ranking.
        
        Args:
            variant: Variant information
            clinvar_status: ClinVar status
            population_frequency: Population frequency
            classification: Final classification
            
        Returns:
            float: Significance score (higher = more significant)
        """
        score = 0.0
        
        # Base score from classification
        if classification == VariantClassification.LIKELY_PATHOGENIC:
            score += 100.0
        elif classification == VariantClassification.UNCERTAIN:
            score += 50.0
        else:  # LIKELY_BENIGN
            score += 10.0
        
        # ClinVar status bonus
        if clinvar_status == ClinVarStatus.PATHOGENIC:
            score += 50.0
        elif clinvar_status == ClinVarStatus.LIKELY_PATHOGENIC:
            score += 30.0
        elif clinvar_status == ClinVarStatus.UNCERTAIN:
            score += 20.0
        elif clinvar_status == ClinVarStatus.LIKELY_BENIGN:
            score += 5.0
        
        # Impact bonus
        if variant.impact == VariantImpact.HIGH:
            score += 40.0
        elif variant.impact == VariantImpact.MODERATE:
            score += 20.0
        elif variant.impact == VariantImpact.LOW:
            score += 5.0
        
        # Frequency penalty (rare variants are more significant)
        if population_frequency < 0.001:
            score += 30.0
        elif population_frequency < 0.01:
            score += 20.0
        elif population_frequency < 0.05:
            score += 10.0
        
        # Gene type bonus
        if self.data_repository.is_cancer_risk_variant(variant.gene):
            score += 25.0
        if self.data_repository.is_pharmacogenomic_variant(variant.gene):
            score += 15.0
        
        # Quality score bonus (if available)
        if variant.quality and variant.quality > 1000:
            score += 10.0
        elif variant.quality and variant.quality > 500:
            score += 5.0
        
        return score

    def get_top_variants(
        self,
        classified_variants: List[VariantWithClassification], 
        limit: int = 10
    ) -> List[VariantResult]:
        """
        Get top variants by significance score.
        
        Args:
            classified_variants: List of classified variants
            limit: Maximum number of variants to return
            
        Returns:
            List[VariantResult]: Top variants sorted by significance
        """
        # Sort by significance score (descending)
        sorted_variants = sorted(
            classified_variants, 
            key=lambda x: x.significance_score, 
            reverse=True
        )
        
        # Convert to result format
        top_variants = []
        for variant in sorted_variants[:limit]:
            result = VariantResult(
                variant_id=variant.variant.variant_id,
                gene=variant.variant.gene,
                chrom=variant.variant.chrom,
                pos=variant.variant.pos,
                ref=variant.variant.ref,
                alt=variant.variant.alt,
                clinvar_status=variant.clinvar_status,
                population_frequency=variant.population_frequency,
                classification=variant.classification,
                significance_score=variant.significance_score,
                impact=variant.variant.impact,
                clinical=variant.variant.clinical
            )
            top_variants.append(result)
        
        return top_variants

    def generate_processing_summary(self, classified_variants: List[VariantWithClassification]) -> ProcessingSummary:
        """
        Generate summary statistics for processed variants.
        
        Args:
            classified_variants: List of classified variants
            
        Returns:
            ProcessingSummary: Summary statistics
        """
        total_variants = len(classified_variants)
        pathogenic_variants = 0
        benign_variants = 0
        uncertain_variants = 0
        high_impact_variants = 0
        drug_response_variants = 0
        unique_genes = set()
        
        for variant in classified_variants:
            # Count by classification
            if variant.classification == VariantClassification.LIKELY_PATHOGENIC:
                pathogenic_variants += 1
            elif variant.classification == VariantClassification.LIKELY_BENIGN:
                benign_variants += 1
            else:
                uncertain_variants += 1
            
            # Count by impact
            if variant.variant.impact == VariantImpact.HIGH:
                high_impact_variants += 1
            
            # Count pharmacogenomic variants
            if self.data_repository.is_pharmacogenomic_variant(variant.variant.gene):
                drug_response_variants += 1
            
            # Count unique genes
            if variant.variant.gene:
                unique_genes.add(variant.variant.gene)
        
        return ProcessingSummary(
            total_variants=total_variants,
            pathogenic_variants=pathogenic_variants,
            benign_variants=benign_variants,
            uncertain_variants=uncertain_variants,
            high_impact_variants=high_impact_variants,
            drug_response_variants=drug_response_variants,
            unique_genes=len(unique_genes)
        )

    def get_classification_rules(self) -> Dict[str, Any]:
        """
        Get the classification rules used by the system.
        
        Returns:
            Dict[str, Any]: Classification rules and thresholds
        """
        return {
            "frequency_thresholds": {
                "pathogenic": FREQUENCY_THRESHOLD_PATHOGENIC,
                "benign": FREQUENCY_THRESHOLD_BENIGN
            },
            "rules": [
                {
                    "rule": "Pathogenic with low frequency",
                    "condition": "frequency < 0.01 AND ClinVar is Pathogenic/Likely Pathogenic",
                    "classification": "Likely Pathogenic"
                },
                {
                    "rule": "High frequency benign",
                    "condition": "frequency > 0.05",
                    "classification": "Likely Benign"
                },
                {
                    "rule": "High impact pathogenic",
                    "condition": "HIGH impact AND frequency < 0.01",
                    "classification": "Likely Pathogenic"
                },
                {
                    "rule": "Cancer risk gene",
                    "condition": "cancer risk gene AND pathogenic ClinVar status",
                    "classification": "Likely Pathogenic"
                },
                {
                    "rule": "Default",
                    "condition": "all other cases",
                    "classification": "Uncertain"
                }
            ],
            "scoring_factors": {
                "classification": {
                    "Likely Pathogenic": 100,
                    "Uncertain": 50,
                    "Likely Benign": 10
                },
                "clinvar_status": {
                    "Pathogenic": 50,
                    "Likely Pathogenic": 30,
                    "Uncertain": 20,
                    "Likely Benign": 5,
                    "Benign": 1
                },
                "impact": {
                    "HIGH": 40,
                    "MODERATE": 20,
                    "LOW": 5,
                    "MODIFIER": 1
                },
                "frequency": {
                    "< 0.001": 30,
                    "< 0.01": 20,
                    "< 0.05": 10
                },
                "gene_type": {
                    "cancer_risk": 25,
                    "pharmacogenomic": 15
                }
            }
        }
