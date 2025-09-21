"""
API endpoints for the genomic VCF processing service.
"""

import logging
import os
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.core.variant_service import VariantProcessingService
from app.presentation.api_models import (
    HealthResponse, ProcessingResponse, ClassificationRulesResponse,
    SupportedFormatsResponse, ErrorResponse
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize service
variant_service = VariantProcessingService()


@router.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    try:
        health_status = variant_service.get_health_status()
        return HealthResponse(**health_status)
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint."""
    try:
        health_status = variant_service.get_health_status()
        return HealthResponse(**health_status)
    except Exception as e:
        logger.error(f"Error in detailed health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/process-vcf", response_model=ProcessingResponse)
async def process_vcf_file(file: UploadFile = File(...)):
    """
    Process uploaded VCF file and classify genetic variants.
    
    Args:
        file: VCF file upload
        
    Returns:
        ProcessingResponse: JSON containing top 10 classified variants
    """
    try:
        result = variant_service.process_vcf_file(file)
        return ProcessingResponse(**result.dict())
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing VCF file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing VCF file: {str(e)}"
        )


@router.post("/process-vcf-sample", response_model=ProcessingResponse)
async def process_sample_vcf():
    """
    Process the included sample VCF file for testing purposes.
    """
    try:
        sample_file_path = "data/sample_variants.vcf"
        result = variant_service.process_sample_vcf(sample_file_path)
        return ProcessingResponse(**result.dict())
        
    except FileNotFoundError as e:
        logger.error(f"Sample file not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing sample VCF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing sample VCF: {str(e)}"
        )


@router.post("/process-patient-001", response_model=ProcessingResponse)
async def process_patient_001():
    """
    Process the Patient 001 VCF file (125 variants) as specified in the requirements.
    """
    try:
        patient_file_path = "data/patient_001_variants.vcf"
        result = variant_service.process_sample_vcf(patient_file_path)
        return ProcessingResponse(**result.dict())
        
    except FileNotFoundError as e:
        logger.error(f"Patient 001 file not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing Patient 001 VCF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing Patient 001 VCF: {str(e)}"
        )


@router.get("/classification-rules", response_model=ClassificationRulesResponse)
async def get_classification_rules():
    """
    Get the classification rules used by the system.
    """
    try:
        rules = variant_service.get_classification_rules()
        return ClassificationRulesResponse(**rules)
    except Exception as e:
        logger.error(f"Error retrieving classification rules: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving classification rules: {str(e)}"
        )


@router.get("/supported-formats", response_model=SupportedFormatsResponse)
async def get_supported_formats():
    """
    Get list of supported VCF file formats.
    """
    try:
        formats = variant_service.get_supported_formats()
        return SupportedFormatsResponse(supported_formats=formats)
    except Exception as e:
        logger.error(f"Error retrieving supported formats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving supported formats: {str(e)}"
        )


# Exception handlers are moved to the main app in app/main.py
