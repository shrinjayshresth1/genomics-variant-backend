"""
VCF file parsing infrastructure.
"""

import logging
import re
from typing import List, Optional, Dict, Any
from fastapi import UploadFile

from app.core.models import Variant, VariantImpact

logger = logging.getLogger(__name__)


class VCFParser:
    """Handles VCF file parsing operations."""
    
    @staticmethod
    def parse_vcf_file(file: UploadFile) -> List[Variant]:
        """
        Parse VCF file and extract variant information.
        
        Args:
            file: Uploaded VCF file
            
        Returns:
            List[Variant]: List of parsed variants
        """
        variants = []
        
        try:
            # Read file content
            file.file.seek(0)
            content = file.file.read().decode('utf-8')
            
            # Parse VCF file line by line
            lines = content.split('\n')
            header_line = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('##'):
                    continue
                elif line.startswith('#CHROM'):
                    header_line = line
                    continue
                else:
                    # Parse variant line
                    try:
                        parsed_variant = VCFParser._parse_variant_line(line, header_line)
                        if parsed_variant:
                            variants.append(parsed_variant)
                    except Exception as e:
                        logger.warning(f"Error parsing variant line: {str(e)}")
                        continue
            
            logger.info(f"Successfully parsed {len(variants)} variants")
            
        except Exception as e:
            logger.error(f"Error parsing VCF file: {str(e)}")
            raise
        
        return variants

    @staticmethod
    def _parse_variant_line(line: str, header_line: Optional[str]) -> Optional[Variant]:
        """
        Parse individual variant line from VCF file.
        
        Args:
            line: VCF variant line
            header_line: VCF header line
            
        Returns:
            Optional[Variant]: Parsed variant or None if parsing fails
        """
        try:
            # Split line into fields
            fields = line.split('\t')
            
            if len(fields) < 8:  # Minimum required fields
                logger.warning(f"Variant line has insufficient fields: {len(fields)}")
                return None
            
            # Extract basic variant information
            chrom = fields[0]
            pos = int(fields[1])
            variant_id = fields[2] if fields[2] != '.' else f"{chrom}_{pos}_{fields[3]}_{fields[4]}"
            ref = fields[3]
            alt = fields[4]
            
            # Extract quality and filter information
            quality = float(fields[5]) if fields[5] != '.' else None
            filter_status = fields[6] if fields[6] != '.' else "PASS"
            
            # Parse INFO field
            info_fields = VCFParser._parse_info_field(fields[7])
            
            # Extract gene and impact information from INFO field
            gene = info_fields.get('GENE')
            impact = VCFParser._parse_impact(info_fields.get('IMPACT'))
            clinical = info_fields.get('CLINICAL')
            
            return Variant(
                chrom=chrom,
                pos=pos,
                variant_id=variant_id,
                ref=ref,
                alt=alt,
                gene=gene,
                impact=impact,
                quality=quality,
                filter_status=filter_status,
                clinical=clinical
            )
            
        except Exception as e:
            logger.warning(f"Error parsing variant line: {str(e)}")
            return None

    @staticmethod
    def _parse_info_field(info_string: str) -> Dict[str, str]:
        """
        Parse INFO field string into key-value pairs.
        
        Args:
            info_string: INFO field string from VCF
            
        Returns:
            Dict[str, str]: Parsed INFO fields
        """
        info_fields = {}
        
        if not info_string or info_string == '.':
            return info_fields
        
        # Split by semicolon and parse key=value pairs
        for field in info_string.split(';'):
            if '=' in field:
                key, value = field.split('=', 1)
                info_fields[key] = value
            else:
                # Flag fields without values
                info_fields[field] = True
        
        return info_fields

    @staticmethod
    def _parse_impact(impact_str: Optional[str]) -> Optional[VariantImpact]:
        """
        Parse impact string to VariantImpact enum.
        
        Args:
            impact_str: Impact string from VCF
            
        Returns:
            Optional[VariantImpact]: Impact level if available
        """
        if not impact_str:
            return None
        
        impact_mapping = {
            'HIGH': VariantImpact.HIGH,
            'MODERATE': VariantImpact.MODERATE,
            'MOD': VariantImpact.MODERATE,
            'LOW': VariantImpact.LOW,
            'MODIFIER': VariantImpact.MODIFIER
        }
        
        return impact_mapping.get(impact_str.upper())

    @staticmethod
    def get_vcf_metadata(file: UploadFile) -> Dict[str, Any]:
        """
        Extract metadata from VCF file header.
        
        Args:
            file: Uploaded VCF file
            
        Returns:
            Dict[str, Any]: VCF metadata information
        """
        metadata = {}
        
        try:
            file.file.seek(0)
            
            for line in file.file:
                line_str = line.decode('utf-8').strip()
                
                if line_str.startswith('##'):
                    # Parse header lines
                    if line_str.startswith('##fileformat='):
                        metadata['fileformat'] = line_str.split('=')[1]
                    elif line_str.startswith('##fileDate='):
                        metadata['fileDate'] = line_str.split('=')[1]
                    elif line_str.startswith('##source='):
                        metadata['source'] = line_str.split('=')[1]
                    elif line_str.startswith('##reference='):
                        metadata['reference'] = line_str.split('=')[1]
                elif line_str.startswith('#CHROM'):
                    # Column header line
                    metadata['columns'] = line_str.split('\t')
                    break
            
            file.file.seek(0)  # Reset file pointer
            
        except Exception as e:
            logger.error(f"Error extracting VCF metadata: {str(e)}")
        
        return metadata
