from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ExposureClass(str, Enum):
    """Standardized exposure classes from COREP CR1"""
    CENTRAL_GOVERNMENTS = "Central governments or central banks"
    INSTITUTIONS = "Institutions"
    CORPORATES = "Corporates"
    RETAIL = "Retail"
    RESIDENTIAL_MORTGAGES = "Exposures secured by mortgages on residential property"
    COMMERCIAL_REAL_ESTATE = "Exposures secured by mortgages on commercial immovable property"
    
class RegulatoryReference(BaseModel):
    """Citation to PRA Rulebook article"""
    article_number: int
    source: str
    excerpt: str

class CR1Row(BaseModel):
    """Single row in COREP CR1 template"""
    exposure_class: ExposureClass
    original_exposure_value: float = Field(description="Original exposure value before risk weighting")
    risk_weight_percent: int = Field(ge=0, le=1250, description="Risk weight percentage")
    risk_weighted_assets: float = Field(description="Calculated RWA")
    
    regulatory_references: List[RegulatoryReference] = Field(
        default_factory=list,
        description="PRA Rulebook articles used to determine this classification"
    )
    
    def calculate_rwa(self) -> float:
        """Calculate RWA from exposure and risk weight"""
        return self.original_exposure_value * (self.risk_weight_percent / 100)
    
class CR1Template(BaseModel):
    """COREP CR1 - Credit Risk Standardised Approach"""
    rows: List[CR1Row]
    total_exposure: float
    total_rwa: float
    
    def validate_totals(self) -> List[str]:
        """Validate that totals match sum of rows"""
        errors = []
        
        calculated_exposure = sum(row.original_exposure_value for row in self.rows)
        calculated_rwa = sum(row.risk_weighted_assets for row in self.rows)
        
        if abs(calculated_exposure - self.total_exposure) > 0.01:
            errors.append(f"Total exposure mismatch: declared {self.total_exposure}, calculated {calculated_exposure}")
            
        if abs(calculated_rwa - self.total_rwa) > 0.01:
            errors.append(f"Total RWA mismatch: declared {self.total_rwa}, calculated {calculated_rwa}")
            
        return errors

class UserQuery(BaseModel):
    """User input for the assistant"""
    question: str
    context: Optional[str] = None