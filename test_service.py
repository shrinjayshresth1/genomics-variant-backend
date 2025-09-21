#!/usr/bin/env python3
"""
Test script for the Genomic VCF Processing Service.

This script tests the service functionality by processing the sample VCF file
and displaying the results.
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


def test_sample_vcf_processing(base_url: str) -> bool:
    """Test processing the sample VCF file."""
    try:
        response = requests.post(f"{base_url}/process-vcf-sample")
        if response.status_code == 200:
            result = response.json()
            print("PASS: Sample VCF processing")
            print(f"    Total variants: {result['totalVariants']}")
            print(f"    Top variants: {len(result['topVariants'])}")
            print(f"    Summary: {result['summary']}")
            
            # Display top 3 variants
            print("\n    Top 3 variants:")
            for i, variant in enumerate(result['topVariants'][:3], 1):
                print(f"    {i}. {variant['variantId']} ({variant['gene']}) - {variant['classification']}")
            
            return True
        else:
            print(f"FAIL: Sample VCF processing - Status: {response.status_code}")
            print(f"    Error: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Sample VCF processing - {str(e)}")
        return False


def test_file_upload(base_url: str) -> bool:
    """Test uploading a VCF file."""
    sample_file = Path("data/sample_variants.vcf")
    if not sample_file.exists():
        print("ERROR: Sample VCF file not found")
        return False
    
    try:
        with open(sample_file, "rb") as f:
            files = {'file': ('sample_variants.vcf', f, 'text/plain')}
            response = requests.post(f"{base_url}/process-vcf", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("PASS: File upload processing")
            print(f"    Total variants: {result['totalVariants']}")
            print(f"    Success: {result['success']}")
            return True
        else:
            print(f"FAIL: File upload processing - Status: {response.status_code}")
            print(f"    Error: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: File upload processing - {str(e)}")
        return False


def main():
    """Run all tests."""
    base_url = "http://localhost:8000"
    
    print("Genomic VCF Processing Service Test Suite")
    print("=" * 50)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    health_ok = test_health_endpoint(base_url)
    
    # Test sample VCF processing
    print("\n2. Testing sample VCF processing...")
    sample_ok = test_sample_vcf_processing(base_url)
    
    # Test file upload
    print("\n3. Testing file upload...")
    upload_ok = test_file_upload(base_url)
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"    Health check: {'PASS' if health_ok else 'FAIL'}")
    print(f"    Sample processing: {'PASS' if sample_ok else 'FAIL'}")
    print(f"    File upload: {'PASS' if upload_ok else 'FAIL'}")
    
    if all([health_ok, sample_ok, upload_ok]):
        print("\nAll tests passed successfully.")
        return 0
    else:
        print("\nSome tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())