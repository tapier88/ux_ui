"""
Models for Site Builder Skill
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from harness.core.time import utc_now_iso


class Framework(Enum):
    """Supported frameworks"""
    REACT = "react"
    NEXT_JS = "nextjs"
    VITE = "vite"
    VUE = "vue"
    ASTRO = "astro"
    HTML_CSS_JS = "html_css_js"
    OTHER = "other"
    UNKNOWN = "unknown"


class PackageManager(Enum):
    """Package managers"""
    NPM = "npm"
    PNPM = "pnpm"
    YARN = "yarn"
    BUN = "bun"
    NONE = "none"
    UNKNOWN = "unknown"


class BuildTool(Enum):
    """Build tools"""
    WEBPACK = "webpack"
    VITE_BUILD = "vite"
    NEXT_BUILD = "next"
    CRA = "cra"
    ASTRO_BUILD = "astro"
    NONE = "none"
    UNKNOWN = "unknown"


class FileOperation(Enum):
    """File operations"""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    RENAME = "rename"
    PRESERVE = "preserve"


class FileOwnership(Enum):
    """File ownership classification"""
    PRESERVE = "preserve"
    MODIFY = "modify"
    REPLACE = "replace"
    CREATE = "create"
    REMOVE = "remove"


class ErrorType(Enum):
    """Error types"""
    SYNTAX_ERROR = "syntax_error"
    TYPE_ERROR = "type_error"
    IMPORT_ERROR = "import_error"
    DEPENDENCY_ERROR = "dependency_error"
    BUILD_ERROR = "build_error"
    ROUTING_ERROR = "routing_error"
    ASSET_ERROR = "asset_error"
    STYLE_ERROR = "style_error"
    RUNTIME_ERROR = "runtime_error"
    ACCESSIBILITY_ERROR = "accessibility_error"
    PERFORMANCE_ERROR = "performance_error"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationStatus(Enum):
    """Validation status"""
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"
    WARNING = "warning"


@dataclass
class ProjectSnapshot:
    """Snapshot of the project structure"""
    framework: Framework = Framework.UNKNOWN
    language: str = "typescript"
    package_manager: PackageManager = PackageManager.UNKNOWN
    build_tool: BuildTool = BuildTool.UNKNOWN
    entry_points: List[str] = field(default_factory=list)
    routes: List[str] = field(default_factory=list)
    components: List[Dict[str, Any]] = field(default_factory=list)
    pages: List[str] = field(default_factory=list)
    styles: List[str] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    dev_dependencies: Dict[str, str] = field(default_factory=dict)
    scripts: Dict[str, str] = field(default_factory=dict)
    existing_design_system: Optional[Dict[str, Any]] = None
    existing_architecture: Optional[Dict[str, Any]] = None
    root_path: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "framework": self.framework.value,
            "language": self.language,
            "package_manager": self.package_manager.value,
            "build_tool": self.build_tool.value,
            "entry_points": self.entry_points,
            "routes": self.routes,
            "components": self.components,
            "pages": self.pages,
            "styles": self.styles,
            "assets": self.assets,
            "dependencies": self.dependencies,
            "dev_dependencies": self.dev_dependencies,
            "scripts": self.scripts,
            "existing_design_system": self.existing_design_system,
            "existing_architecture": self.existing_architecture,
            "root_path": self.root_path,
        }


@dataclass
class CodeChange:
    """Represents a code modification"""
    file: str
    operation: FileOperation
    reason: str
    before: Optional[str] = None
    after: Optional[str] = None
    risk: str = "LOW"  # LOW, MEDIUM, HIGH
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "operation": self.operation.value,
            "reason": self.reason,
            "before": self.before,
            "after": self.after,
            "risk": self.risk,
            "line_number": self.line_number,
        }


@dataclass
class BuildError:
    """Represents a build error"""
    error_type: ErrorType
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    possible_fix: Optional[str] = None
    stack_trace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "possible_fix": self.possible_fix,
            "stack_trace": self.stack_trace,
        }


@dataclass
class CheckpointInfo:
    """Checkpoint information"""
    checkpoint_id: str
    task_id: str
    timestamp: str
    description: str
    files_snapshot: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "description": self.description,
            "files_snapshot": self.files_snapshot,
        }


@dataclass
class RollbackResult:
    """Result of a rollback operation"""
    success: bool
    checkpoint_id: str
    files_restored: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "checkpoint_id": self.checkpoint_id,
            "files_restored": self.files_restored,
            "errors": self.errors,
        }


@dataclass
class DiffResult:
    """Result of diff analysis"""
    file: str
    changes: List[Dict[str, Any]] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    is_safe: bool = True
    risk_level: str = "LOW"
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "changes": self.changes,
            "additions": self.additions,
            "deletions": self.deletions,
            "is_safe": self.is_safe,
            "risk_level": self.risk_level,
            "warnings": self.warnings,
        }


@dataclass
class ValidationResult:
    """Generic validation result"""
    validation_type: str
    status: ValidationStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_type": self.validation_type,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass
class VisualValidationResult:
    """Visual validation result (abstraction for future browser integration)"""
    status: ValidationStatus = ValidationStatus.PENDING
    message: str = "Visual validation pending - browser integration required"
    alignment_check: Optional[bool] = None
    spacing_check: Optional[bool] = None
    overflow_check: Optional[bool] = None
    responsive_layout_check: Optional[bool] = None
    missing_assets: List[str] = field(default_factory=list)
    visual_hierarchy_notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "message": self.message,
            "alignment_check": self.alignment_check,
            "spacing_check": self.spacing_check,
            "overflow_check": self.overflow_check,
            "responsive_layout_check": self.responsive_layout_check,
            "missing_assets": self.missing_assets,
            "visual_hierarchy_notes": self.visual_hierarchy_notes,
        }


@dataclass
class AIQualityResult:
    """AI quality evaluation result"""
    originality: float = 0.5
    composition: float = 0.5
    typography: float = 0.5
    hierarchy: float = 0.5
    brand_fit: float = 0.5
    genericness: float = 0.5
    repetition: float = 0.5
    effect_overuse: float = 0.5
    visual_quality: float = 0.5
    overall_score: float = 0.5
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    requires_review: bool = False
    threshold: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "originality": self.originality,
            "composition": self.composition,
            "typography": self.typography,
            "hierarchy": self.hierarchy,
            "brand_fit": self.brand_fit,
            "genericness": self.genericness,
            "repetition": self.repetition,
            "effect_overuse": self.effect_overuse,
            "visual_quality": self.visual_quality,
            "overall_score": self.overall_score,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "requires_review": self.requires_review,
            "threshold": self.threshold,
        }


@dataclass
class DesignFidelityReport:
    """Report comparing implementation against DesignBuildPlan"""
    layout_match: float = 1.0
    component_match: float = 1.0
    typography_match: float = 1.0
    color_match: float = 1.0
    motion_match: float = 1.0
    responsive_match: float = 1.0
    asset_match: float = 1.0
    accessibility_match: float = 1.0
    overall_fidelity: float = 1.0
    deviations: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "layout_match": self.layout_match,
            "component_match": self.component_match,
            "typography_match": self.typography_match,
            "color_match": self.color_match,
            "motion_match": self.motion_match,
            "responsive_match": self.responsive_match,
            "asset_match": self.asset_match,
            "accessibility_match": self.accessibility_match,
            "overall_fidelity": self.overall_fidelity,
            "deviations": self.deviations,
        }


@dataclass
class BuildReport:
    """Final build report"""
    project: str
    task_id: str
    timestamp: str = field(default_factory=utc_now_iso)
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_removed: List[str] = field(default_factory=list)
    components_created: List[str] = field(default_factory=list)
    components_modified: List[str] = field(default_factory=list)
    assets_added: List[str] = field(default_factory=list)
    dependencies_added: List[str] = field(default_factory=list)
    dependencies_removed: List[str] = field(default_factory=list)
    build_status: ValidationStatus = ValidationStatus.PENDING
    tests_status: ValidationStatus = ValidationStatus.PENDING
    visual_validation: Optional[VisualValidationResult] = None
    accessibility_validation: Optional[ValidationResult] = None
    performance_validation: Optional[ValidationResult] = None
    ai_quality: Optional[AIQualityResult] = None
    design_fidelity: Optional[DesignFidelityReport] = None
    rollback_status: Optional[RollbackResult] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[BuildError] = field(default_factory=list)
    checkpoints: List[CheckpointInfo] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project": self.project,
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "files_removed": self.files_removed,
            "components_created": self.components_created,
            "components_modified": self.components_modified,
            "assets_added": self.assets_added,
            "dependencies_added": self.dependencies_added,
            "dependencies_removed": self.dependencies_removed,
            "build_status": self.build_status.value,
            "tests_status": self.tests_status.value,
            "visual_validation": self.visual_validation.to_dict() if self.visual_validation else None,
            "accessibility_validation": self.accessibility_validation.to_dict() if self.accessibility_validation else None,
            "performance_validation": self.performance_validation.to_dict() if self.performance_validation else None,
            "ai_quality": self.ai_quality.to_dict() if self.ai_quality else None,
            "design_fidelity": self.design_fidelity.to_dict() if self.design_fidelity else None,
            "rollback_status": self.rollback_status.to_dict() if self.rollback_status else None,
            "warnings": self.warnings,
            "errors": [e.to_dict() for e in self.errors],
            "checkpoints": [c.to_dict() for c in self.checkpoints],
        }


@dataclass
class GenerationTask:
    """Task for asset generation (Higgsfield abstraction)"""
    task_id: str
    generator: str = "higgsfield"
    asset_type: str = "image"
    creative_direction: str = ""
    style: str = ""
    composition: str = ""
    aspect_ratio: str = "16:9"
    duration: Optional[float] = None
    purpose: str = ""
    status: str = "pending"  # pending, queued, generating, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "generator": self.generator,
            "asset_type": self.asset_type,
            "creative_direction": self.creative_direction,
            "style": self.style,
            "composition": self.composition,
            "aspect_ratio": self.aspect_ratio,
            "duration": self.duration,
            "purpose": self.purpose,
            "status": self.status,
            "metadata": self.metadata,
        }
