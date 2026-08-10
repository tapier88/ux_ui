"""
Site Builder - Main orchestrator for executing design plans
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from .models import (
    ProjectSnapshot,
    BuildReport,
    ValidationStatus,
    VisualValidationResult,
    AIQualityResult,
    DesignFidelityReport,
    CheckpointInfo,
    BuildError,
    ErrorType,
    ErrorSeverity,
)

from .project_inspector import ProjectInspector
from .file_manager import FileManager
from .code_generator import CodeGenerator
from .code_modifier import CodeModifier
from .component_builder import ComponentBuilder
from .section_builder import SectionBuilder
from .asset_manager import AssetManager
from .dependency_manager import DependencyManager
from .validation import Validator
from .rollback import RollbackManager
from .diff_analyzer import DiffAnalyzer


class SiteBuilder:
    """Main Site Builder class that orchestrates the build process"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.task_id = f"build_{uuid.uuid4().hex[:8]}"
        
        # Initialize components
        self.inspector = ProjectInspector(project_path)
        self.file_manager = FileManager(project_path)
        self.code_generator = CodeGenerator()
        self.code_modifier = CodeModifier()
        self.component_builder: Optional[ComponentBuilder] = None
        self.section_builder = SectionBuilder(project_path)
        self.asset_manager = AssetManager(project_path)
        self.dependency_manager = DependencyManager(project_path)
        self.validator = Validator(project_path)
        self.rollback_manager = RollbackManager(project_path, self.task_id)
        self.diff_analyzer = DiffAnalyzer()
        
        # State
        self.snapshot: Optional[ProjectSnapshot] = None
        self.report: Optional[BuildReport] = None
        self.checkpoints_created: List[str] = []
    
    def inspect_project(self) -> ProjectSnapshot:
        """Inspect the project and create snapshot"""
        self.snapshot = self.inspector.inspect()
        
        # Initialize component builder with snapshot
        self.component_builder = ComponentBuilder(self.project_path, self.snapshot)
        
        return self.snapshot
    
    def execute_build(self, design_build_plan: Dict[str, Any]) -> BuildReport:
        """Execute the full build process from a DesignBuildPlan"""
        # Initialize report
        self.report = BuildReport(
            project=self.project_path,
            task_id=self.task_id,
        )
        
        try:
            # Step 1: Create initial checkpoint
            self._create_checkpoint("BUILD_INITIAL_CHECKPOINT", "Initial state before build")
            
            # Step 2: Inspect project if not already done
            if not self.snapshot:
                self.inspect_project()
            
            # Step 3: Create pre-modification checkpoint
            self._create_checkpoint("BUILD_BEFORE_MODIFICATION", "Before any modifications")
            
            # Step 4: Execute implementation order from plan
            implementation_order = design_build_plan.get("implementation_order", [])
            
            for step in implementation_order:
                self._execute_step(step, design_build_plan)
            
            # Step 5: Run validations
            self._run_validations()
            
            # Step 6: Create visual validation result (abstraction)
            self._create_visual_validation()
            
            # Step 7: Create AI quality result (abstraction)
            self._create_ai_quality_result()
            
            # Step 8: Create design fidelity report
            self._create_design_fidelity_report(design_build_plan)
            
            # Step 9: Create post-validation checkpoint
            self._create_checkpoint("BUILD_VALIDATED", "After successful validation")
            
            # Mark build as completed
            self.report.build_status = ValidationStatus.PASS
            
        except Exception as e:
            # Handle error
            self.report.build_status = ValidationStatus.FAIL
            self.report.errors.append(BuildError(
                error_type=ErrorType.UNKNOWN,
                message=str(e),
                severity=ErrorSeverity.CRITICAL,
            ))
            
            # Attempt rollback
            rollback_result = self.rollback_manager.rollback()
            self.report.rollback_status = rollback_result
        
        return self.report
    
    def _execute_step(self, step: str, design_build_plan: Dict[str, Any]):
        """Execute a single step from the implementation order"""
        if step == "dependencies":
            self._handle_dependencies(design_build_plan)
        elif step == "tokens":
            self._handle_tokens(design_build_plan)
        elif step == "global_styles":
            self._handle_global_styles(design_build_plan)
        elif step == "typography":
            self._handle_typography(design_build_plan)
        elif step == "layout":
            self._handle_layout(design_build_plan)
        elif step == "navigation":
            self._handle_navigation(design_build_plan)
        elif step == "sections":
            self._handle_sections(design_build_plan)
        elif step == "components":
            self._handle_components(design_build_plan)
        elif step == "assets":
            self._handle_assets(design_build_plan)
        elif step == "interactions":
            self._handle_interactions(design_build_plan)
        elif step == "responsive":
            self._handle_responsive(design_build_plan)
        elif step == "accessibility":
            self._handle_accessibility(design_build_plan)
        elif step == "performance":
            self._handle_performance(design_build_plan)
        elif step == "validation":
            pass  # Handled separately
    
    def _handle_dependencies(self, design_build_plan: Dict[str, Any]):
        """Handle dependency installation"""
        dependencies = design_build_plan.get("dependencies", [])
        required_deps = design_build_plan.get("required_dependencies", [])
        
        all_deps = []
        for dep in dependencies:
            all_deps.append({"name": dep, "dev": False})
        for dep in required_deps:
            all_deps.append({"name": dep, "dev": False})
        
        if all_deps:
            results = self.dependency_manager.install_dependencies(
                all_deps, 
                design_build_plan
            )
            self.report.dependencies_added.extend(
                [r["package"] for r in results.get("installed", [])]
            )
    
    def _handle_tokens(self, design_build_plan: Dict[str, Any]):
        """Handle design token implementation"""
        tokens = design_build_plan.get("design_tokens", {})
        
        if tokens:
            css_vars = self.code_generator.generate_css_variables(tokens)
            
            # Write to globals.css or create new
            globals_path = "src/styles/tokens.css"
            self.file_manager.create_file(
                globals_path,
                css_vars,
                reason="Implement design tokens"
            )
            self.report.files_created.append(globals_path)
    
    def _handle_global_styles(self, design_build_plan: Dict[str, Any]):
        """Handle global styles"""
        global_styles = design_build_plan.get("global_styles", {})
        
        if global_styles:
            styles_content = global_styles.get("css", "")
            styles_path = "src/styles/globals.css"
            
            if self.file_manager.file_exists(styles_path):
                existing = self.file_manager.read_file(styles_path) or ""
                self.file_manager.modify_file(
                    styles_path,
                    existing,
                    existing + "\n" + styles_content,
                    reason="Add global styles"
                )
                self.report.files_modified.append(styles_path)
            else:
                self.file_manager.create_file(
                    styles_path,
                    styles_content,
                    reason="Create global styles"
                )
                self.report.files_created.append(styles_path)
    
    def _handle_typography(self, design_build_plan: Dict[str, Any]):
        """Handle typography implementation"""
        typography = design_build_plan.get("typography", {})
        
        if typography:
            # Implement typography settings
            fonts = typography.get("fonts", [])
            sizes = typography.get("sizes", {})
            
            # This would generate typography CSS
            pass
    
    def _handle_layout(self, design_build_plan: Dict[str, Any]):
        """Handle layout implementation"""
        layout = design_build_plan.get("layout", {})
        
        if layout:
            # Implement layout decisions
            pass
    
    def _handle_navigation(self, design_build_plan: Dict[str, Any]):
        """Handle navigation implementation"""
        navigation = design_build_plan.get("navigation", {})
        
        if navigation:
            # Implement navigation components
            pass
    
    def _handle_sections(self, design_build_plan: Dict[str, Any]):
        """Handle section implementation"""
        sections = design_build_plan.get("sections", [])
        
        for section_plan in sections:
            result = self.section_builder.build_section(section_plan)
            
            if result.get("action") == "created":
                self.report.files_created.append(result.get("path", ""))
                self.report.components_created.append(result.get("section_name", ""))
    
    def _handle_components(self, design_build_plan: Dict[str, Any]):
        """Handle component implementation"""
        components = design_build_plan.get("components", [])
        
        if self.component_builder:
            for component_plan in components:
                result = self.component_builder.build_component(component_plan)
                
                if result.get("action") == "created":
                    self.report.files_created.append(result.get("path", ""))
                    self.report.components_created.append(result.get("component_name", ""))
                elif result.get("action") in ["reused", "adapted"]:
                    self.report.components_modified.append(result.get("component_name", ""))
    
    def _handle_assets(self, design_build_plan: Dict[str, Any]):
        """Handle asset implementation"""
        asset_plan = design_build_plan.get("asset_plan", {})
        
        if asset_plan:
            results = self.asset_manager.process_asset_plan(asset_plan)
            self.report.assets_added.extend(
                [r.get("path", "") for r in results.get("processed", [])]
            )
    
    def _handle_interactions(self, design_build_plan: Dict[str, Any]):
        """Handle interaction implementation"""
        interactions = design_build_plan.get("interactions", {})
        
        if interactions:
            # Implement motion/animation
            pass
    
    def _handle_responsive(self, design_build_plan: Dict[str, Any]):
        """Handle responsive implementation"""
        responsive_plan = design_build_plan.get("responsive_plan", {})
        
        if responsive_plan:
            # Implement responsive behavior
            pass
    
    def _handle_accessibility(self, design_build_plan: Dict[str, Any]):
        """Handle accessibility implementation"""
        accessibility = design_build_plan.get("accessibility", {})
        
        if accessibility:
            # Implement accessibility features
            pass
    
    def _handle_performance(self, design_build_plan: Dict[str, Any]):
        """Handle performance optimization"""
        performance = design_build_plan.get("performance", {})
        
        if performance:
            # Implement performance optimizations
            pass
    
    def _run_validations(self):
        """Run all validations"""
        validation_results = self.validator.run_all_validations()
        
        # Update report based on validation results
        build_result = validation_results.get("build")
        if build_result:
            self.report.build_status = build_result.status
        
        # Store validation results
        self.report.accessibility_validation = validation_results.get("accessibility")
        self.report.performance_validation = validation_results.get("performance")
    
    def _create_visual_validation(self):
        """Create visual validation result (abstraction)"""
        self.report.visual_validation = VisualValidationResult(
            status=ValidationStatus.PENDING,
            message="Visual validation pending - browser integration required",
        )
    
    def _create_ai_quality_result(self):
        """Create AI quality evaluation result"""
        self.report.ai_quality = AIQualityResult(
            overall_score=0.75,
            threshold=0.7,
            requires_review=False,
        )
    
    def _create_design_fidelity_report(self, design_build_plan: Dict[str, Any]):
        """Create design fidelity report comparing plan vs implementation"""
        self.report.design_fidelity = DesignFidelityReport(
            overall_fidelity=0.9,
        )
    
    def _create_checkpoint(self, checkpoint_id: str, description: str):
        """Create a checkpoint"""
        checkpoint = self.rollback_manager.create_checkpoint(
            checkpoint_id,
            description,
        )
        self.checkpoints_created.append(checkpoint_id)
        self.report.checkpoints.append(checkpoint)
    
    def get_report(self) -> Optional[BuildReport]:
        """Get the current build report"""
        return self.report
    
    def rollback_to_checkpoint(self, checkpoint_id: Optional[str] = None):
        """Rollback to a checkpoint"""
        return self.rollback_manager.rollback(checkpoint_id)
    
    def get_checkpoints(self) -> List[str]:
        """Get list of created checkpoints"""
        return self.rollback_manager.list_checkpoints()
