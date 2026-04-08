from app.models.institution import Institution, InstitutionType  # noqa
from app.models.user import User, Role  # noqa
from app.models.student import Student, StudentStatus  # noqa
from app.models.program import Program  # noqa
from app.models.course import Course  # noqa
from app.models.enrollment import Enrollment  # noqa
from app.models.attendance import AttendanceRecord  # noqa
from app.models.assessment import Assessment  # noqa
from app.models.analytics import AnalyticsStudentScore, AnalyticsProgramScore, AnalyticsInstitutionKPI  # noqa
from app.models.recommendation import Recommendation  # noqa
from app.models.labour_market import LabourMarketTrend, SkillTrend  # noqa
from app.models.sync import SyncJob, SyncJobRun, SyncCheckpoint, FieldMapping, IntegrationError, AuditLog  # noqa
