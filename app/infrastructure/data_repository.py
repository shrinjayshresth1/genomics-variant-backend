"""
Data repository for clinical and population frequency data.
"""

import random
import logging
from typing import Dict, Tuple, Optional

from app.core.models import ClinVarStatus

logger = logging.getLogger(__name__)


class ClinicalDataRepository:
    """Repository for clinical significance and population frequency data."""
    
    # Mock ClinVar data - mapping variant IDs to clinical significance
    _CLINVAR_DATA: Dict[str, ClinVarStatus] = {
        # High-impact pathogenic variants
        "rs121913530": ClinVarStatus.PATHOGENIC,  # MLH1 - Lynch syndrome
        "rs80359507": ClinVarStatus.PATHOGENIC,   # GJB2 - Deafness
        "rs80359550": ClinVarStatus.PATHOGENIC,   # BRCA2 - Breast cancer
        "rs121913529": ClinVarStatus.PATHOGENIC,  # KRAS - Lung cancer
        "rs28897756": ClinVarStatus.PATHOGENIC,   # BRCA1 - Breast/ovarian cancer
        "rs80357906": ClinVarStatus.PATHOGENIC,   # BRCA1 - Breast/ovarian cancer
        "rs80356898": ClinVarStatus.PATHOGENIC,   # BRCA1 - Breast/ovarian cancer
        "rs104894790": ClinVarStatus.PATHOGENIC,  # DMD - Duchenne muscular dystrophy
        "rs3810526": ClinVarStatus.PATHOGENIC,    # G6PD - G6PD deficiency
        "rs6025": ClinVarStatus.PATHOGENIC,       # F5 - Factor V Leiden
        
        # Likely pathogenic variants
        "rs1801133": ClinVarStatus.LIKELY_PATHOGENIC,  # MTHFR - Homocysteinuria risk
        "rs1805087": ClinVarStatus.LIKELY_PATHOGENIC,  # MTR
        "rs1800460": ClinVarStatus.LIKELY_PATHOGENIC,  # TPMT - Azathioprine sensitivity
        "rs1799853": ClinVarStatus.LIKELY_PATHOGENIC,  # CYP2C9 - Warfarin sensitivity
        "rs16969968": ClinVarStatus.LIKELY_PATHOGENIC, # CHRNA5 - Nicotine dependence
        "rs1800562": ClinVarStatus.LIKELY_PATHOGENIC,  # HFE - Hemochromatosis
        "rs1800888": ClinVarStatus.LIKELY_PATHOGENIC,  # CFTR
        "rs1126809": ClinVarStatus.LIKELY_PATHOGENIC,  # NAT2 - Isoniazid metabolism
        "rs61750900": ClinVarStatus.LIKELY_PATHOGENIC, # CYP2C9 - Phenytoin metabolism
        "rs4986893": ClinVarStatus.LIKELY_PATHOGENIC,  # CYP2C19 - Clopidogrel resistance
        "rs1800497": ClinVarStatus.LIKELY_PATHOGENIC,  # DRD2 - Antipsychotic response
        "rs267606617": ClinVarStatus.LIKELY_PATHOGENIC, # LRP5 - Osteoporosis
        "rs4149056": ClinVarStatus.LIKELY_PATHOGENIC,  # SLCO1B1 - Statin myopathy
        "rs3745274": ClinVarStatus.LIKELY_PATHOGENIC,  # CYP2B6 - Efavirenz metabolism
        "rs9934438": ClinVarStatus.LIKELY_PATHOGENIC,  # VKORC1 - Warfarin sensitivity
        "rs429358": ClinVarStatus.LIKELY_PATHOGENIC,   # APOE - Alzheimer risk
        "rs7412": ClinVarStatus.LIKELY_PATHOGENIC,     # APOE - protective
        "rs1131691": ClinVarStatus.LIKELY_PATHOGENIC,  # OPN1MW - Color blindness
        
        # Benign variants
        "rs2691305": ClinVarStatus.BENIGN,
        "rs1873778": ClinVarStatus.BENIGN,        # PDGFRA
        "rs10455872": ClinVarStatus.BENIGN,       # LPA - Cardiovascular risk
        "rs1799998": ClinVarStatus.BENIGN,        # ABCB1 - Drug response
        "rs1045642": ClinVarStatus.BENIGN,        # ABCB1 - Drug response
        "rs2470893": ClinVarStatus.BENIGN,        # CYP1A1
        "rs2472297": ClinVarStatus.BENIGN,        # CYP4F2 - Warfarin dose
        "rs2267437": ClinVarStatus.BENIGN,        # COMT - Pain sensitivity
        "rs4680": ClinVarStatus.BENIGN,           # CYP1B1
        
        # Likely benign variants
        "rs1057910": ClinVarStatus.LIKELY_BENIGN, # MTHFR - Warfarin sensitivity
        "rs4988235": ClinVarStatus.LIKELY_BENIGN, # MCM6 - Lactose intolerance
        "rs671": ClinVarStatus.LIKELY_BENIGN,     # ALDH2 - Alcohol flush
        "rs5030655": ClinVarStatus.LIKELY_BENIGN, # UGT1A1 - Gilbert syndrome
        "rs1042713": ClinVarStatus.LIKELY_BENIGN, # ADRB2 - Asthma response
        "rs113994105": ClinVarStatus.LIKELY_BENIGN, # APC
        "rs2032582": ClinVarStatus.LIKELY_BENIGN, # ABCB1 - Drug response
        "rs1042522": ClinVarStatus.LIKELY_BENIGN, # TP53 - benign
        "rs16942": ClinVarStatus.LIKELY_BENIGN,   # BRCA1
    }

    # Mock population frequency data (gnomAD-like)
    _POPULATION_FREQUENCY: Dict[str, float] = {
        # Rare variants (pathogenic)
        "rs121913530": 0.0001,  # MLH1
        "rs80359507": 0.0002,   # GJB2
        "rs80359550": 0.0001,   # BRCA2
        "rs121913529": 0.0001,  # KRAS
        "rs28897756": 0.0001,   # BRCA1
        "rs80357906": 0.0001,   # BRCA1
        "rs80356898": 0.0001,   # BRCA1
        "rs104894790": 0.0001,  # DMD
        "rs3810526": 0.0001,    # G6PD
        "rs6025": 0.0001,       # F5
        
        # Low frequency variants
        "rs1801133": 0.005,     # MTHFR
        "rs1805087": 0.003,     # MTR
        "rs1800460": 0.002,     # TPMT
        "rs1799853": 0.004,     # CYP2C9
        "rs16969968": 0.006,    # CHRNA5
        "rs1800562": 0.002,     # HFE
        "rs1800888": 0.003,     # CFTR
        "rs1126809": 0.004,     # NAT2
        "rs61750900": 0.002,    # CYP2C9
        "rs4986893": 0.003,     # CYP2C19
        "rs1800497": 0.005,     # DRD2
        "rs267606617": 0.001,   # LRP5
        "rs4149056": 0.004,     # SLCO1B1
        "rs3745274": 0.003,     # CYP2B6
        "rs9934438": 0.004,     # VKORC1
        "rs429358": 0.008,      # APOE
        "rs7412": 0.006,        # APOE
        "rs1131691": 0.002,     # OPN1MW
        
        # Common variants (benign)
        "rs2691305": 0.15,      # Common variant
        "rs1873778": 0.12,      # PDGFRA
        "rs10455872": 0.08,     # LPA
        "rs1799998": 0.10,      # ABCB1
        "rs1045642": 0.09,      # ABCB1
        "rs2470893": 0.11,      # CYP1A1
        "rs2472297": 0.07,      # CYP4F2
        "rs2267437": 0.13,      # COMT
        "rs4680": 0.14,         # CYP1B1
        
        # Moderate frequency variants
        "rs1057910": 0.03,      # MTHFR
        "rs4988235": 0.04,      # MCM6
        "rs671": 0.02,          # ALDH2
        "rs5030655": 0.03,      # UGT1A1
        "rs1042713": 0.02,      # ADRB2
        "rs113994105": 0.01,    # APC
        "rs2032582": 0.03,      # ABCB1
        "rs1042522": 0.05,      # TP53
        "rs16942": 0.02,        # BRCA1
    }

    @classmethod
    def get_clinvar_status(cls, variant_id: str) -> ClinVarStatus:
        """
        Get ClinVar clinical significance status for a variant.
        
        Args:
            variant_id: Variant identifier (rs number or custom ID)
            
        Returns:
            ClinVarStatus: Clinical significance status
        """
        # Check if we have mock data for this variant
        if variant_id in cls._CLINVAR_DATA:
            return cls._CLINVAR_DATA[variant_id]
        
        # For unknown variants, assign based on variant ID pattern
        if variant_id.startswith('rs'):
            # Real rs numbers - assign uncertain significance
            return ClinVarStatus.UNCERTAIN
        else:
            # Custom variant IDs - randomly assign status
            statuses = [
                ClinVarStatus.UNCERTAIN,
                ClinVarStatus.LIKELY_BENIGN,
                ClinVarStatus.LIKELY_PATHOGENIC
            ]
            return random.choice(statuses)

    @classmethod
    def get_population_frequency(cls, variant_id: str) -> float:
        """
        Get population frequency for a variant (gnomAD-like data).
        
        Args:
            variant_id: Variant identifier (rs number or custom ID)
            
        Returns:
            float: Population frequency (0.0 to 1.0)
        """
        # Check if we have mock data for this variant
        if variant_id in cls._POPULATION_FREQUENCY:
            return cls._POPULATION_FREQUENCY[variant_id]
        
        # For unknown variants, generate realistic frequency based on variant ID
        if variant_id.startswith('rs'):
            # Real rs numbers - typically common variants
            return random.uniform(0.01, 0.3)
        else:
            # Custom variant IDs - typically rare variants
            return random.uniform(0.0001, 0.01)

    @classmethod
    def get_variant_annotation(cls, variant_id: str) -> Tuple[ClinVarStatus, float]:
        """
        Get both ClinVar status and population frequency for a variant.
        
        Args:
            variant_id: Variant identifier
            
        Returns:
            Tuple[ClinVarStatus, float]: Clinical status and population frequency
        """
        clinvar_status = cls.get_clinvar_status(variant_id)
        population_frequency = cls.get_population_frequency(variant_id)
        
        return clinvar_status, population_frequency

    @classmethod
    def get_gene_clinical_info(cls, gene: Optional[str]) -> Optional[str]:
        """
        Get clinical information for a gene.
        
        Args:
            gene: Gene symbol
            
        Returns:
            Optional[str]: Clinical information if available
        """
        if not gene:
            return None
        
        # Mock clinical information for known genes
        gene_clinical_info = {
            "BRCA1": "Breast/ovarian cancer risk",
            "BRCA2": "Breast cancer risk",
            "MLH1": "Lynch syndrome",
            "KRAS": "Lung cancer",
            "GJB2": "Deafness",
            "DMD": "Duchenne muscular dystrophy",
            "G6PD": "G6PD deficiency",
            "F5": "Factor V Leiden thrombophilia",
            "MTHFR": "Homocysteinuria risk",
            "TPMT": "Azathioprine sensitivity",
            "CYP2C9": "Warfarin sensitivity",
            "CYP2C19": "Clopidogrel resistance",
            "HFE": "Hemochromatosis",
            "CFTR": "Cystic fibrosis",
            "NAT2": "Isoniazid metabolism",
            "SLCO1B1": "Statin myopathy",
            "VKORC1": "Warfarin sensitivity",
            "APOE": "Alzheimer disease risk",
            "OPN1MW": "Color blindness",
            "ALDH2": "Alcohol flush reaction",
            "UGT1A1": "Gilbert syndrome",
            "CHRNA5": "Nicotine dependence",
            "ADRB2": "Asthma response",
            "DRD2": "Antipsychotic response",
            "LRP5": "Osteoporosis",
            "COMT": "Pain sensitivity",
            "CYP1B1": "Glaucoma",
            "TP53": "Li-Fraumeni syndrome",
            "PDGFRA": "Gastrointestinal stromal tumor",
            "LPA": "Cardiovascular risk",
            "ABCB1": "Drug response",
            "CYP1A1": "Xenobiotic metabolism",
            "CYP4F2": "Warfarin dose requirement",
            "CYP2B6": "Efavirenz metabolism",
            "MCM6": "Lactose intolerance",
            "MTR": "Homocysteine metabolism",
            "APC": "Familial adenomatous polyposis"
        }
        
        return gene_clinical_info.get(gene.upper())

    @classmethod
    def is_pharmacogenomic_variant(cls, gene: Optional[str]) -> bool:
        """
        Check if a variant is in a pharmacogenomic gene.
        
        Args:
            gene: Gene symbol
            
        Returns:
            bool: True if gene is pharmacogenomic
        """
        if not gene:
            return False
        
        pharmacogenomic_genes = {
            "CYP2C9", "CYP2C19", "CYP2D6", "CYP3A4", "CYP2B6", "CYP1A1", "CYP1B1", "CYP4F2",
            "TPMT", "NAT2", "UGT1A1", "SLCO1B1", "VKORC1", "ABCB1", "MTHFR", "MTR"
        }
        
        return gene.upper() in pharmacogenomic_genes

    @classmethod
    def is_cancer_risk_variant(cls, gene: Optional[str]) -> bool:
        """
        Check if a variant is in a cancer risk gene.
        
        Args:
            gene: Gene symbol
            
        Returns:
            bool: True if gene is associated with cancer risk
        """
        if not gene:
            return False
        
        cancer_risk_genes = {
            "BRCA1", "BRCA2", "MLH1", "MSH2", "MSH6", "PMS2", "TP53", "KRAS", "APC",
            "PTEN", "ATM", "CHEK2", "PALB2", "BARD1", "BRIP1", "RAD51C", "RAD51D"
        }
        
        return gene.upper() in cancer_risk_genes
