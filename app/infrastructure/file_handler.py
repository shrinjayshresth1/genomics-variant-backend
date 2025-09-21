"""
File handling infrastructure for VCF file operations.
"""

import logging
import os
from typing import List, Dict, Any
from fastapi import UploadFile

logger = logging.getLogger(__name__)

# Valid VCF file extensions
VALID_EXTENSIONS = {'.vcf', '.vcf.gz'}

# VCF file format header
VCF_HEADER = '#CHROM'

# Maximum file size (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024


class VCFFileHandler:
    """Handles VCF file validation and operations."""
    
    @staticmethod
    def validate_vcf_file(file: UploadFile) -> bool:
        """
        Validate uploaded VCF file format and content.
        
        Args:
            file: Uploaded file object
            
        Returns:
            bool: True if file is valid VCF format, False otherwise
        """
        try:
            # Check file extension
            if not file.filename:
                logger.error("No filename provided")
                return False
                
            file_extension = '.' + file.filename.split('.')[-1].lower()
            if file_extension not in VALID_EXTENSIONS:
                logger.error(f"Invalid file extension: {file_extension}")
                return False
            
            # Check file size
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            
            if file_size > MAX_FILE_SIZE:
                logger.error(f"File too large: {file_size} bytes")
                return False
            
            # Check VCF header
            if not VCFFileHandler._validate_vcf_header(file):
                logger.error("Invalid VCF header format")
                return False
            
            logger.info(f"VCF file validation successful: {file.filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating VCF file: {str(e)}")
            return False

    @staticmethod
    def _validate_vcf_header(file: UploadFile) -> bool:
        """
        Validate VCF file header format.
        
        Args:
            file: Uploaded file object
            
        Returns:
            bool: True if header is valid, False otherwise
        """
        try:
            # Read first few lines to check header
            file.file.seek(0)
            first_lines = []
            
            for i, line in enumerate(file.file):
                if i >= 20:  # Check first 20 lines to find header
                    break
                first_lines.append(line.decode('utf-8').strip())
            
            file.file.seek(0)  # Reset to beginning
            
            # Check for VCF header
            for line in first_lines:
                if line.startswith(VCF_HEADER):
                    # Validate required columns
                    columns = line.split('\t')
                    required_columns = ['#CHROM', 'POS', 'ID', 'REF', 'ALT']
                    
                    # Check if all required columns are present
                    missing_columns = [col for col in required_columns if col not in columns]
                    if missing_columns:
                        logger.error(f"Missing required columns: {missing_columns}")
                        logger.error(f"Available columns: {columns}")
                        return False
                    
                    logger.info(f"VCF header validation passed. Columns: {columns}")
                    return True
            
            logger.error("No valid VCF header found")
            logger.error(f"First lines: {first_lines}")
            return False
            
        except Exception as e:
            logger.error(f"Error reading VCF header: {str(e)}")
            return False

    @staticmethod
    def get_supported_formats() -> List[str]:
        """
        Get list of supported VCF file formats.
        
        Returns:
            List[str]: List of supported file extensions
        """
        return list(VALID_EXTENSIONS)

    @staticmethod
    def read_file_content(file_path: str) -> str:
        """
        Read file content as string.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        Check if file exists.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return os.path.exists(file_path)
