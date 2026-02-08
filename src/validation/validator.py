from typing import List, Dict
from src.schemas import CR1Row, CR1Template

class CR1Validator:
    """Validates CR1 data for completeness and consistency"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_row(self, row: CR1Row) -> List[str]:
        """Validate a single CR1 row"""
        errors = []
        
        # Check required fields
        if row.original_exposure_value <= 0:
            errors.append(f"Invalid exposure value: {row.original_exposure_value}")
        
        if row.risk_weight_percent < 0 or row.risk_weight_percent > 1250:
            errors.append(f"Invalid risk weight: {row.risk_weight_percent}%")
        
        # Validate RWA calculation
        expected_rwa = row.calculate_rwa()
        if abs(row.risk_weighted_assets - expected_rwa) > 0.01:
            errors.append(
                f"RWA mismatch: declared {row.risk_weighted_assets}, "
                f"calculated {expected_rwa}"
            )
        
        # Check for regulatory references
        if not row.regulatory_references:
            self.warnings.append(f"No regulatory references for {row.exposure_class.value}")
        
        return errors
    
    def validate_template(self, template: CR1Template) -> Dict:
        """Validate complete CR1 template"""
        all_errors = []
        
        # Validate each row
        for i, row in enumerate(template.rows):
            row_errors = self.validate_row(row)
            if row_errors:
                all_errors.extend([f"Row {i+1}: {err}" for err in row_errors])
        
        # Validate totals
        total_errors = template.validate_totals()
        all_errors.extend(total_errors)
        
        return {
            'is_valid': len(all_errors) == 0,
            'errors': all_errors,
            'warnings': self.warnings
        }
    
    def generate_audit_trail(self, rows: List[CR1Row]) -> str:
        """Generate audit trail showing regulatory basis for each field"""
        trail = "AUDIT TRAIL - REGULATORY JUSTIFICATION\n"
        trail += "=" * 70 + "\n\n"
        
        for i, row in enumerate(rows, 1):
            trail += f"Row {i}: {row.exposure_class.value}\n"
            trail += f"  Exposure: £{row.original_exposure_value:,.0f}\n"
            trail += f"  Risk Weight: {row.risk_weight_percent}%\n"
            trail += f"  RWA: £{row.risk_weighted_assets:,.0f}\n"
            trail += f"\n  Regulatory Basis:\n"
            
            for ref in row.regulatory_references:
                trail += f"    • {ref.source}\n"
                trail += f"      {ref.excerpt}\n"
            
            trail += "\n" + "-" * 70 + "\n\n"
        
        return trail


def test_validator():
    """Test the validator"""
    from src.generation.llm_generator import COREPGenerator
    
    generator = COREPGenerator()
    validator = CR1Validator()
    
    # Generate some rows
    queries = [
        "£50M unrated corporates",
        "£100M residential mortgages"
    ]
    
    rows = []
    for query in queries:
        result = generator.generate_cr1_row(query)
        rows.append(result['cr1_row'])
    
    # Create template
    total_exposure = sum(row.original_exposure_value for row in rows)
    total_rwa = sum(row.risk_weighted_assets for row in rows)
    
    template = CR1Template(
        rows=rows,
        total_exposure=total_exposure,
        total_rwa=total_rwa
    )
    
    # Validate
    validation_result = validator.validate_template(template)
    
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(f"✓ Valid: {validation_result['is_valid']}")
    
    if validation_result['errors']:
        print("\n❌ Errors:")
        for error in validation_result['errors']:
            print(f"  • {error}")
    
    if validation_result['warnings']:
        print("\n⚠️  Warnings:")
        for warning in validation_result['warnings']:
            print(f"  • {warning}")
    
    # Generate audit trail
    print("\n" + validator.generate_audit_trail(rows))

if __name__ == "__main__":
    test_validator()