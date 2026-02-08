import pandas as pd
from typing import List
from datetime import datetime
from pathlib import Path
from src.schemas import CR1Row, CR1Template

class CR1Exporter:
    """Exports CR1 data to Excel template format"""
    
    def __init__(self):
        self.output_dir = Path("data/processed/outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_excel(self, template: CR1Template, filename: str = None) -> str:
        """
        Export CR1 template to Excel file
        
        Args:
            template: CR1Template with rows
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"CR1_Template_{timestamp}.xlsx"
        
        filepath = self.output_dir / filename
        
        # Prepare data for DataFrame
        data = []
        for row in template.rows:
            data.append({
                'Exposure Class': row.exposure_class.value,
                'Original Exposure (£)': f"{row.original_exposure_value:,.0f}",
                'Risk Weight (%)': row.risk_weight_percent,
                'Risk Weighted Assets (£)': f"{row.risk_weighted_assets:,.0f}",
                'Regulatory Reference': ', '.join([ref.source for ref in row.regulatory_references])
            })
        
        # Add totals row
        data.append({
            'Exposure Class': 'TOTAL',
            'Original Exposure (£)': f"{template.total_exposure:,.0f}",
            'Risk Weight (%)': '-',
            'Risk Weighted Assets (£)': f"{template.total_rwa:,.0f}",
            'Regulatory Reference': '-'
        })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Export to Excel with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='CR1 - Credit Risk', index=False)
            
            # Get worksheet for formatting
            worksheet = writer.sheets['CR1 - Credit Risk']
            
            # Set column widths
            worksheet.column_dimensions['A'].width = 50
            worksheet.column_dimensions['B'].width = 25
            worksheet.column_dimensions['C'].width = 18
            worksheet.column_dimensions['D'].width = 30
            worksheet.column_dimensions['E'].width = 30
            
            # Bold the header row
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)
            
            # Bold the totals row
            for cell in worksheet[len(data) + 1]:
                cell.font = cell.font.copy(bold=True)
        
        print(f"✓ Exported to: {filepath}")
        return str(filepath)
    
    def export_audit_trail(self, template: CR1Template, filename: str = None) -> str:
        """Export detailed audit trail to text file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"CR1_Audit_Trail_{timestamp}.txt"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("COREP CR1 - AUDIT TRAIL\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, row in enumerate(template.rows, 1):
                f.write(f"\nRow {i}: {row.exposure_class.value}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Original Exposure: £{row.original_exposure_value:,.0f}\n")
                f.write(f"Risk Weight: {row.risk_weight_percent}%\n")
                f.write(f"Risk Weighted Assets: £{row.risk_weighted_assets:,.0f}\n")
                f.write(f"\nRegulatory Justification:\n")
                
                for ref in row.regulatory_references:
                    f.write(f"\n  Source: {ref.source}\n")
                    f.write(f"  Text: {ref.excerpt}\n")
                
                f.write("\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"TOTALS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Exposure: £{template.total_exposure:,.0f}\n")
            f.write(f"Total RWA: £{template.total_rwa:,.0f}\n")
        
        print(f"✓ Audit trail exported to: {filepath}")
        return str(filepath)


def test_exporter():
    """Test the exporter"""
    from src.generation.llm_generator import COREPGenerator
    
    generator = COREPGenerator()
    exporter = CR1Exporter()
    
    # Generate rows from queries
    queries = [
        "£50M unrated corporates",
        "£100M residential mortgages",
        "£200M UK central government exposure"
    ]
    
    print("\n" + "=" * 70)
    print("GENERATING CR1 TEMPLATE")
    print("=" * 70)
    
    rows = []
    for query in queries:
        print(f"\nProcessing: {query}")
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
    
    # Export
    print("\n" + "=" * 70)
    print("EXPORTING OUTPUTS")
    print("=" * 70)
    
    excel_path = exporter.export_to_excel(template)
    audit_path = exporter.export_audit_trail(template)
    
    print(f"\n✅ Complete! Files saved in: {exporter.output_dir}")

if __name__ == "__main__":
    test_exporter()