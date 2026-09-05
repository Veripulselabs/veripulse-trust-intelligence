from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TrustScoreRequest(BaseModel):
    email: Optional[str] = Field(None, description="Email address to evaluate", json_schema_extra={"example": "jane.doe@company.com"})
    phone: Optional[str] = Field(None, description="Phone number to evaluate (E.164 or national format)", json_schema_extra={"example": "+14155552671"})
    country_code: Optional[str] = Field("US", description="Default ISO 3166-1 alpha-2 country code for phone validation", json_schema_extra={"example": "US"})

class CarrierInfo(BaseModel):
    name: str = Field(..., description="Telecom carrier name")
    line_type: str = Field(..., description="Line classification: MOBILE, FIXED_LINE, VOIP, TOLL_FREE, PAGER, UNKNOWN")
    is_virtual: bool = Field(..., description="True if provider is a known virtual VoIP service (Twilio, Google Voice, TextNow)")
    mcc: Optional[str] = Field(None, description="Mobile Country Code")
    mnc: Optional[str] = Field(None, description="Mobile Network Code")

class PhoneIntelligence(BaseModel):
    phone_input: str = Field(..., description="Input phone string")
    is_valid: bool = Field(..., description="True if phone number conforms to ITU-T E.164")
    country_code: str = Field(..., description="Resolved ISO 2-letter country code")
    e164_format: Optional[str] = Field(None, description="Canonical E.164 representation")
    international_format: Optional[str] = Field(None, description="Human-readable international format")
    national_format: Optional[str] = Field(None, description="Standard local format")
    carrier: Optional[CarrierInfo] = Field(None, description="Telecom carrier and line type intelligence")
    risk_score: int = Field(..., ge=0, le=100, description="Phone-specific fraud risk score (0-100)")
    signals: List[str] = Field(default_factory=list, description="Specific risk and validity signals detected")

class EmailIntelligence(BaseModel):
    email: str = Field(..., description="Input email string")
    is_valid: bool = Field(..., description="True if RFC 5322 syntax is strictly compliant")
    is_disposable: bool = Field(..., description="True if domain is a temporary/burner email provider")
    is_role_account: bool = Field(..., description="True if address is a shared role (admin@, support@, sales@)")
    is_free_provider: bool = Field(..., description="True if address belongs to public webmail (Gmail, Yahoo, Outlook)")
    has_mx_records: bool = Field(..., description="True if DNS MX records exist and are routable")
    did_you_mean: Optional[str] = Field(None, description="Typo suggestion for common misspelled domains")
    domain: str = Field(..., description="Extracted domain")
    risk_score: int = Field(..., ge=0, le=100, description="Email-specific fraud risk score (0-100)")
    signals: List[str] = Field(default_factory=list, description="Specific email signals detected")

class TrustScoreResponse(BaseModel):
    trust_score: int = Field(..., ge=0, le=100, description="Definitive 0-100 Trust Score. 100 = Highly Verified, 0 = High Fraud")
    risk_score: int = Field(..., ge=0, le=100, description="Composite risk score (100 - trust_score)")
    risk_level: str = Field(..., description="LOW, MEDIUM, or HIGH risk classification")
    recommended_action: str = Field(..., description="ALLOW, FLAG_FOR_REVIEW, or BLOCK policy action")
    signals: List[str] = Field(default_factory=list, description="Consolidated audit signals across both vectors")
    email_intelligence: Optional[EmailIntelligence] = Field(None, description="Detailed email validation breakdown")
    phone_intelligence: Optional[PhoneIntelligence] = Field(None, description="Detailed phone line intelligence breakdown")
    execution_time_ms: float = Field(..., description="Total engine evaluation latency in milliseconds")

class BatchTrustScoreRequest(BaseModel):
    items: List[TrustScoreRequest] = Field(..., max_length=50, description="List of up to 50 email/phone pairs")

class BatchTrustScoreResponse(BaseModel):
    total_processed: int
    results: List[TrustScoreResponse]
