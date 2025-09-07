from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ScenarioType(str, Enum):
    """Available crash simulation scenarios"""
    PAYSTACK_TIMEOUT = "paystack_timeout"
    MIGRATION_TYPE_MISMATCH = "migration_type_mismatch"
    TASKQ_OVERSELL = "taskq_oversell"
    VERIFY_PAYMENT_TIMEOUT = "verify_payment_timeout"
    DB_STARTUP_FAILURE = "db_startup_failure"
    STRIPE_SIGNATURE_ERROR = "stripe_signature_error"


class LogFormat(str, Enum):
    """Log output format options"""
    PLAIN = "plain"
    JSON = "json"


class SimulateCrashRequest(BaseModel):
    """Request schema for crash simulation"""
    scenario: ScenarioType = Field(..., description="Type of crash scenario to simulate")
    format: LogFormat = Field(default=LogFormat.JSON, description="Log output format")
    min_logs: int = Field(default=120, ge=0, le=1000, description="Minimum number of prelude log lines")
    no_jitter: bool = Field(default=False, description="Disable network/processing jitter")
    users_impacted: Optional[int] = Field(None, ge=1, le=10000, description="Number of users impacted (random if not provided)")
    repository_id: str = Field(..., description="Repository ID to associate with the crash")
    comment: Optional[str] = Field(None, max_length=500, description="Additional comments about the simulation")


class ErrorDetails(BaseModel):
    """Error details extracted from simulation"""
    title: str
    description: str
    severity: str
    component: str
    error_type: str


class SimulateCrashResponse(BaseModel):
    """Response schema for crash simulation"""
    success: bool
    crash_id: str
    scenario: str
    error_details: ErrorDetails
    users_impacted: int
    logs_generated: int
    log_file_url: Optional[str] = None
    s3_key: Optional[str] = None
    sample_link: str
    slack_notification_sent: bool = False
    database_entry_created: bool = False
    message: str
