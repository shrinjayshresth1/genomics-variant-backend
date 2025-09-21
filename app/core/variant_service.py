"""
Core service layer for variant processing operations.
"""

import logging
from typing import List, Dict, Any
from fastapi import UploadFile

from app.core.models import Variant, VariantWithClassification, ProcessingResponse
from app.core.variant_classifier import VariantClassifier
from app.infrastructure.vcf_parser import VCFParser
from app.infrastructure.file_handler import VCFFileHandler
from app.infrastructure.data_repository import ClinicalDataRepository

logger = logging.getLogger(__name__)


class VariantProcessingService:
    """Service for processing VCF files and classifying variants."""
    
    def __init__(self):
        """Initialize the variant processing service."""
        self.data_repository = ClinicalDataRepository()
        self.classifier = VariantClassifier(self.data_repository)
        self.file_handler = VCFFileHandler()
        self.vcf_parser = VCFParser()

    def process_vcf_file(self, file: UploadFile) -> ProcessingResponse:
        """
        Process uploaded VCF file and classify genetic variants.
        
        Args:
            file: VCF file upload
            
        Returns:
            ProcessingResponse: JSON containing top 10 classified variants
        """
        try:
            # Validate file
            if not self.file_handler.validate_vcf_file(file):
                raise ValueError("Invalid VCF file format")
            
            logger.info(f"Processing VCF file: {file.filename}")
            
            # Parse VCF file
            variants = self.vcf_parser.parse_vcf_file(file)
            logger.info(f"Parsed {len(variants)} variants from VCF file")
            
            # Classify variants
            classified_variants = self.classifier.classify_variants(variants)
            logger.info(f"Classified {len(classified_variants)} variants")
            
            # Generate output
            result = self._generate_output(classified_variants)
            
            return ProcessingResponse(
                success=True,
                message=f"Successfully processed {len(variants)} variants",
                total_variants=len(variants),
                top_variants=result["top_variants"],
                summary=result["summary"]
            )
            
        except Exception as e:
            logger.error(f"Error processing VCF file: {str(e)}")
            raise

    def process_sample_vcf(self, file_path: str) -> ProcessingResponse:
        """
        Process sample VCF file for testing purposes.
        
        Args:
            file_path: Path to the sample VCF file
            
        Returns:
            ProcessingResponse: Processing results
        """
        try:
            if not self.file_handler.file_exists(file_path):
                raise FileNotFoundError(f"Sample VCF file not found: {file_path}")
            
            logger.info(f"Processing sample VCF file: {file_path}")
            
            # Read file content and create mock UploadFile
            from fastapi import UploadFile
            from io import BytesIO
            
            content = self.file_handler.read_file_content(file_path)
            file_obj = BytesIO(content.encode('utf-8'))
            upload_file = UploadFile(
                filename="sample_variants.vcf",
                file=file_obj
            )
            
            # Parse VCF file
            variants = self.vcf_parser.parse_vcf_file(upload_file)
            logger.info(f"Parsed {len(variants)} variants from sample VCF file")
            
            # Classify variants
            classified_variants = self.classifier.classify_variants(variants)
            logger.info(f"Classified {len(classified_variants)} variants")
            
            # Generate output
            result = self._generate_output(classified_variants)
            
            return ProcessingResponse(
                success=True,
                message=f"Successfully processed {len(variants)} variants from sample file",
                total_variants=len(variants),
                top_variants=result["top_variants"],
                summary=result["summary"]
            )
            
        except Exception as e:
            logger.error(f"Error processing sample VCF: {str(e)}")
            raise

    def _generate_output(self, classified_variants: List[VariantWithClassification]) -> Dict[str, Any]:
        """
        Generate output with top variants and summary.
        
        Args:
            classified_variants: List of classified variants
            
        Returns:
            Dict[str, Any]: Output structure
        """
        try:
            # Get top 10 variants by significance
            top_variants = self.classifier.get_top_variants(classified_variants, limit=10)
            
            # Generate processing summary
            summary = self.classifier.generate_processing_summary(classified_variants)
            
            # Create output structure
            output = {
                "top_variants": [variant.dict() for variant in top_variants],
                "summary": summary.dict()
            }
            
            logger.info(f"Generated output with {len(top_variants)} top variants")
            return output
            
        except Exception as e:
            logger.error(f"Error generating output: {str(e)}")
            raise

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the service.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        return {
            "status": "healthy",
            "service": "genomic-vcf-processor",
            "version": "1.0.0",
            "components": {
                "file_handler": "operational",
                "vcf_parser": "operational",
                "classifier": "operational",
                "data_repository": "operational"
            }
        }

    def get_classification_rules(self) -> Dict[str, Any]:
        """
        Get the classification rules used by the system.
        
        Returns:
            Dict[str, Any]: Classification rules and thresholds
        """
        return self.classifier.get_classification_rules()

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported VCF file formats.
        
        Returns:
            List[str]: List of supported file extensions
        """
        return self.file_handler.get_supported_formats()
