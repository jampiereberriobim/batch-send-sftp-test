#from dataclasses import dataclass
#from datetime import datetime
#
#
#@dataclass(frozen=True)
#class ExecutionMetadata:
#    integration: str
#    dataset: str
#    execution_date: datetime
#    processed_files: int
#    uploaded_files: int
#    success: bool

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ExecutionMetadata:
    execution_id: str
    integration: str
    dataset: str
    report_name: str
    processed_date: datetime
    start_time: datetime
    end_time: Optional[datetime]
    execution_time_seconds: float
    sent_time_utc: Optional[datetime]
    file_name: Optional[str]
    file_size_mb: float
    sha256: Optional[str]
    user_role: Optional[str]
    status: str
    error_message: Optional[str]