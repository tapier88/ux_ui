"""
Site Builder Skill - Executes design plans and converts them into real code modifications

The Site Builder takes WebsiteDesignProfile, RedesignStrategy, DesignResourceReport,
and DesignBuildPlan as inputs and produces actual code changes on a project.
"""
from .models import (
    Framework,
    PackageManager,
    BuildTool,
    FileOperation,
    FileOwnership,
    ErrorType,
    ErrorSeverity,
    ValidationStatus,
    ProjectSnapshot,
    CodeChange,
    BuildError,
    CheckpointInfo,
    RollbackResult,
    DiffResult,
    ValidationResult,
    VisualValidationResult,
    AIQualityResult,
    DesignFidelityReport,
    BuildReport,
    GenerationTask,
)

from .project_inspector import (
    ProjectInspector,
    inspect_project,
)

from .builder import (
    SiteBuilder,
)

from .file_manager import (
    FileManager,
)

from .code_generator import (
    CodeGenerator,
)

from .code_modifier import (
    CodeModifier,
)

from .component_builder import (
    ComponentBuilder,
)

from .section_builder import (
    SectionBuilder,
)

from .asset_manager import (
    AssetManager,
)

from .dependency_manager import (
    DependencyManager,
)

from .validation import (
    Validator,
)

from .rollback import (
    RollbackManager,
)

from .diff_analyzer import (
    DiffAnalyzer,
)


def load_site_builder_skill():
    """Load the site builder skill into the registry"""
    from harness.skills import load_skill
    
    def site_builder_func(data: dict) -> dict:
        """Site builder skill function"""
        project_path = data.get("project_path", ".")
        design_build_plan = data.get("design_build_plan")
        
        if not design_build_plan:
            return {
                "error": "design_build_plan is required",
                "status": "failed"
            }
        
        builder = SiteBuilder(project_path)
        report = builder.execute_build(design_build_plan)
        
        return {
            "status": "completed",
            "report": report.to_dict(),
        }
    
    load_skill(
        name="site-builder",
        func=site_builder_func,
    )


__all__ = [
    # Models
    "Framework",
    "PackageManager",
    "BuildTool",
    "FileOperation",
    "FileOwnership",
    "ErrorType",
    "ErrorSeverity",
    "ValidationStatus",
    "ProjectSnapshot",
    "CodeChange",
    "BuildError",
    "CheckpointInfo",
    "RollbackResult",
    "DiffResult",
    "ValidationResult",
    "VisualValidationResult",
    "AIQualityResult",
    "DesignFidelityReport",
    "BuildReport",
    "GenerationTask",
    # Classes
    "ProjectInspector",
    "SiteBuilder",
    "FileManager",
    "CodeGenerator",
    "CodeModifier",
    "ComponentBuilder",
    "SectionBuilder",
    "AssetManager",
    "DependencyManager",
    "Validator",
    "RollbackManager",
    "DiffAnalyzer",
    # Functions
    "inspect_project",
    "load_site_builder_skill",
]
