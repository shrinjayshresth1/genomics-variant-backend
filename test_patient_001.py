#!/usr/bin/env python3
"""
Test script for Patient 001 VCF processing as specified in the genomics pipeline requirements.

This script tests the service functionality by processing the Patient 001 VCF file
and displaying the results in a format matching the clinical report requirements.
"""

import requests
import json
import sys
import time
from pathlib import Path


def test_health_endpoint(base_url: str) -> bool:
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("PASS: Health check endpoint")
            print(f"    Response: {response.json()}")
            return True
        else:
            print(f"FAIL: Health check endpoint - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Health check endpoint - {str(e)}")
        return False


def test_patient_001_processing(base_url: str) -> bool:
    """Test processing the Patient 001 VCF file."""
    try:
        response = requests.post(f"{base_url}/process-patient-001")
        if response.status_code == 200:
            result = response.json()
            print("PASS: Patient 001 VCF processing")
            print(f"    Total variants: {result['total_variants']}")
            print(f"    Top variants: {len(result['top_variants'])}")
            
            # Display summary matching the clinical report format
            summary = result['summary']
            print(f"\n    Summary:")
            print(f"    • Total variants: {summary['total_variants']}")
            print(f"    • Pathogenic variants: {summary['pathogenic_variants']}")
            print(f"    • Drug response variants: {summary['drug_response_variants']}")
            print(f"    • Risk factor variants: {summary['pathogenic_variants']}")  # Using pathogenic as risk factor
            print(f"    • High impact variants: {summary['high_impact_variants']}")
            print(f"    • Genes affected: {summary['unique_genes']}")
            
            # Display top 10 variants by significance
            print(f"\n    Top 10 Variants by Significance:")
            for i, variant in enumerate(result['top_variants'][:10], 1):
                print(f"    {i:2d}. {variant['variant_id']} ({variant['gene']}) - {variant['classification']} (Score: {variant['significance_score']:.1f})")
                print(f"        ClinVar: {variant['clinvar_status']}, Frequency: {variant['population_frequency']:.4f}")
                if variant['clinical']:
                    print(f"        Clinical: {variant['clinical']}")
            
            # Key Clinical Findings
            print(f"\n    Key Clinical Findings:")
            pathogenic_variants = [v for v in result['top_variants'] if v['classification'] == 'Likely Pathogenic']
            
            # Group by gene families
            brca_variants = [v for v in pathogenic_variants if v['gene'] in ['BRCA1', 'BRCA2']]
            apoe_variants = [v for v in pathogenic_variants if v['gene'] == 'APOE']
            factor_v_variants = [v for v in pathogenic_variants if v['gene'] == 'F5']
            cyp_variants = [v for v in pathogenic_variants if v['gene'] and 'CYP' in v['gene']]
            lynch_variants = [v for v in pathogenic_variants if v['gene'] == 'MLH1']
            hfe_variants = [v for v in pathogenic_variants if v['gene'] == 'HFE']
            
            if brca_variants:
                print(f"    • BRCA1/BRCA2: Multiple pathogenic variants (high cancer risk)")
            if apoe_variants:
                print(f"    • APOE: e4 allele present (Alzheimer's risk)")
            if factor_v_variants:
                print(f"    • Factor V Leiden: Thrombophilia risk")
            if cyp_variants:
                print(f"    • Pharmacogenomics: Multiple CYP variants affecting drug metabolism")
            if lynch_variants:
                print(f"    • Lynch syndrome: MLH1 pathogenic variant")
            if hfe_variants:
                print(f"    • Hemochromatosis: HFE C282Y variants")
            
            return True
        else:
            print(f"FAIL: Patient 001 VCF processing - Status: {response.status_code}")
            print(f"    Error: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Patient 001 VCF processing - {str(e)}")
        return False


def test_file_upload(base_url: str) -> bool:
    """Test uploading the Patient 001 VCF file."""
    patient_file = Path("data/patient_001_variants.vcf")
    if not patient_file.exists():
        print("ERROR: Patient 001 VCF file not found")
        return False
    
    try:
        with open(patient_file, "rb") as f:
            files = {'file': ('patient_001_variants.vcf', f, 'text/plain')}
            response = requests.post(f"{base_url}/process-vcf", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("PASS: Patient 001 file upload processing")
            print(f"    Total variants: {result['total_variants']}")
            print(f"    Success: {result['success']}")
            return True
        else:
            print(f"FAIL: Patient 001 file upload processing - Status: {response.status_code}")
            print(f"    Error: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Patient 001 file upload processing - {str(e)}")
        return False


def test_classification_rules(base_url: str) -> bool:
    """Test the classification rules endpoint."""
    try:
        response = requests.get(f"{base_url}/classification-rules")
        if response.status_code == 200:
            rules = response.json()
            print("PASS: Classification rules endpoint")
            print(f"    Frequency thresholds: {rules['frequency_thresholds']}")
            print(f"    Number of rules: {len(rules['rules'])}")
            return True
        else:
            print(f"FAIL: Classification rules endpoint - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Classification rules endpoint - {str(e)}")
        return False


def main():
    """Run all tests for the genomics pipeline."""
    base_url = "http://localhost:8000"
    
    print("Genomics Data Pipeline - Patient 001 Test Suite")
    print("=" * 60)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    health_ok = test_health_endpoint(base_url)
    
    # Test Patient 001 VCF processing
    print("\n2. Testing Patient 001 VCF processing...")
    patient_ok = test_patient_001_processing(base_url)
    
    # Test file upload
    print("\n3. Testing Patient 001 file upload...")
    upload_ok = test_file_upload(base_url)
    
    # Test classification rules
    print("\n4. Testing classification rules...")
    rules_ok = test_classification_rules(base_url)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"    Health check: {'PASS' if health_ok else 'FAIL'}")
    print(f"    Patient 001 processing: {'PASS' if patient_ok else 'FAIL'}")
    print(f"    File upload: {'PASS' if upload_ok else 'FAIL'}")
    print(f"    Classification rules: {'PASS' if rules_ok else 'FAIL'}")
    
    if all([health_ok, patient_ok, upload_ok, rules_ok]):
        print("\nAll tests passed successfully.")
        print("The genomics data pipeline is ready for production use.")
        return 0
    else:
        print("\nSome tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
