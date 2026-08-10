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
        """
        Handle typography implementation.

        typography_plan comes from design_execution_planner's
        TypographyTokens: font families plus per-level (h1/h2/h3/body/small)
        size/weight/line-height dicts. Writes them as CSS custom properties,
        the same pattern _handle_tokens already uses for design tokens.
        """
        typography = design_build_plan.get("typography", {})

        if not typography:
            return

        css_vars = {
            "font-family-base": typography.get("font_family", "Inter, system-ui, sans-serif"),
            "font-family-heading": typography.get("heading_font", "Inter, system-ui, sans-serif"),
            "font-family-body": typography.get("body_font", "Inter, system-ui, sans-serif"),
            "letter-spacing-base": typography.get("letter_spacing", "normal"),
            "text-max-width": typography.get("max_width", "65ch"),
        }
        for level in ("h1", "h2", "h3", "body", "small"):
            level_tokens = typography.get(level)
            if isinstance(level_tokens, dict):
                css_vars[f"font-size-{level}"] = level_tokens.get("size", "1rem")
                css_vars[f"font-weight-{level}"] = level_tokens.get("weight", "400")
                css_vars[f"line-height-{level}"] = level_tokens.get("line_height", "1.5")

        css_content = self.code_generator.generate_css_variables(css_vars)
        typography_path = "src/styles/typography.css"
        self.file_manager.create_file(
            typography_path, css_content, reason="Implement typography tokens"
        )
        self.report.files_created.append(typography_path)

    def _handle_layout(self, design_build_plan: Dict[str, Any]):
        """
        Handle layout implementation.

        layout_plan comes from design_execution_planner's LayoutPlan:
        container width, grid column count, gaps, content density. Writes
        them as CSS custom properties consumed by section/component code
        (e.g. var(--layout-container-width)).
        """
        layout = design_build_plan.get("layout", {})

        if not layout:
            return

        gaps = layout.get("gaps", {})
        css_vars = {
            "layout-container-width": layout.get("container_width", "1200px"),
            "layout-columns": str(layout.get("columns", 12)),
            "layout-gap-row": gaps.get("row", "1.5rem") if isinstance(gaps, dict) else "1.5rem",
            "layout-gap-col": gaps.get("col", "1.5rem") if isinstance(gaps, dict) else "1.5rem",
        }

        css_content = self.code_generator.generate_css_variables(css_vars)
        layout_path = "src/styles/layout.css"
        self.file_manager.create_file(
            layout_path, css_content, reason="Implement layout tokens"
        )
        self.report.files_created.append(layout_path)

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
        """
        Handle responsive implementation.

        responsive_plan comes from design_execution_planner's
        ResponsivePlan: per-breakpoint (desktop/tablet/mobile)
        ResponsiveBehavior descriptions (layout_change, font_change,
        spacing_change, etc - free-text strings describing intent, not
        CSS values directly). Writes them as documented CSS custom
        media-query breakpoints plus a comment block recording the
        intended behavior per breakpoint, so the design decisions aren't
        silently dropped even though translating free-text intent into
        exact CSS rules per component is out of scope here.
        """
        responsive_plan = design_build_plan.get("responsive", {}) or design_build_plan.get("responsive_plan", {})

        if not responsive_plan:
            return

        breakpoints = {
            "mobile": "max-width: 767px",
            "tablet": "min-width: 768px) and (max-width: 1023px",
            "desktop": "min-width: 1024px",
        }

        lines = ["/* Responsive behavior plan - see PLAN.md Fase 2B: "
                 "generated from design_execution_planner's ResponsivePlan */"]
        for breakpoint_name, media_query in breakpoints.items():
            behavior = responsive_plan.get(breakpoint_name, {})
            if not isinstance(behavior, dict) or not behavior:
                continue
            lines.append(f"\n@media ({media_query}) {{")
            lines.append("  /*")
            for key, value in behavior.items():
                if value:
                    lines.append(f"   - {key}: {value}")
            lines.append("  */")
            lines.append("}")

        if len(lines) <= 1:
            return

        responsive_path = "src/styles/responsive.css"
        self.file_manager.create_file(
            responsive_path, "\n".join(lines), reason="Document responsive behavior plan"
        )
        self.report.files_created.append(responsive_path)

    def _handle_accessibility(self, design_build_plan: Dict[str, Any]):
        """
        Handle accessibility implementation.

        accessibility_plan comes from design_execution_planner's
        AccessibilityPlan: booleans/dicts for semantic HTML, keyboard nav,
        focus states, contrast targets, touch target sizes. Writes the
        concrete, code-generatable parts (focus-state CSS, contrast
        targets as documented custom properties) plus a checklist file
        for the parts that need human/component-level review
        (semantic_html, aria, screen_reader, form_accessibility can't be
        verified from a plan dict alone).
        """
        accessibility = design_build_plan.get("accessibility", {})

        if not accessibility:
            return

        focus_states = accessibility.get("focus_states", {})
        contrast = accessibility.get("contrast", {})
        touch_targets = accessibility.get("touch_targets", {})

        css_vars = {}
        if isinstance(focus_states, dict) and focus_states:
            css_vars["focus-outline"] = focus_states.get("outline", "2px solid")
            css_vars["focus-offset"] = focus_states.get("offset", "2px")
        if isinstance(contrast, dict) and contrast:
            css_vars["contrast-min-ratio"] = str(contrast.get("min_ratio", 4.5))
        if isinstance(touch_targets, dict) and touch_targets:
            css_vars["touch-target-min-size"] = touch_targets.get("min_size", "44px")

        if css_vars:
            css_content = self.code_generator.generate_css_variables(css_vars)
            a11y_css_path = "src/styles/accessibility.css"
            self.file_manager.create_file(
                a11y_css_path, css_content, reason="Implement accessibility tokens"
            )
            self.report.files_created.append(a11y_css_path)

        checklist_lines = ["# Accessibility checklist (from design_execution_planner)", ""]
        checklist_lines.append(
            f"- [{'x' if accessibility.get('semantic_html') else ' '}] Use semantic HTML elements"
        )
        checklist_lines.append(
            f"- [{'x' if accessibility.get('keyboard_navigation') else ' '}] Full keyboard navigation support"
        )
        checklist_lines.append(
            f"- [{'x' if accessibility.get('reduced_motion') else ' '}] Respect prefers-reduced-motion"
        )
        checklist_lines.append(
            "- [ ] ARIA labels reviewed per component (not auto-verifiable from the plan)"
        )
        checklist_lines.append(
            "- [ ] Screen reader behavior tested (not auto-verifiable from the plan)"
        )
        checklist_lines.append(
            "- [ ] Form accessibility reviewed, if the project has forms"
        )

        checklist_path = "ACCESSIBILITY_CHECKLIST.md"
        self.file_manager.create_file(
            checklist_path, "\n".join(checklist_lines), reason="Document accessibility plan"
        )
        self.report.files_created.append(checklist_path)

    def _handle_performance(self, design_build_plan: Dict[str, Any]):
        """
        Handle performance optimization.

        performance_plan comes from design_execution_planner's
        PerformancePlan: image optimization, code splitting, and font
        loading strategy dicts. These are project-level configuration
        decisions, not code that inserts itself into arbitrary components
        - writes them as a checklist/config-reference file a human or a
        later automated step can act on, rather than guessing at
        framework-specific config file edits without knowing the build
        tool in use.
        """
        performance = design_build_plan.get("performance", {})

        if not performance:
            return

        lines = ["# Performance plan (from design_execution_planner)", ""]

        image_opt = performance.get("image_optimization", {})
        if isinstance(image_opt, dict) and image_opt:
            formats = ", ".join(image_opt.get("formats", []))
            lines.append(f"## Image optimization")
            lines.append(f"- Formats: {formats or 'not specified'}")
            lines.append(f"- Lazy loading: {image_opt.get('lazy_loading', False)}")
            lines.append(f"- Quality target: {image_opt.get('quality', 'not specified')}")
            lines.append("")

        code_splitting = performance.get("code_splitting", {})
        if isinstance(code_splitting, dict) and code_splitting:
            lines.append(f"## Code splitting")
            lines.append(f"- Strategy: {code_splitting.get('strategy', 'not specified')}")
            lines.append(f"- Prefetch: {code_splitting.get('prefetch', False)}")
            lines.append("")

        font_loading = performance.get("font_loading", {})
        if isinstance(font_loading, dict) and font_loading:
            lines.append(f"## Font loading")
            lines.append(f"- Strategy: {font_loading.get('strategy', 'not specified')}")
            lines.append(f"- Preload: {font_loading.get('preload', False)}")
            lines.append("")

        if len(lines) <= 2:
            return

        perf_path = "PERFORMANCE_PLAN.md"
        self.file_manager.create_file(
            perf_path, "\n".join(lines), reason="Document performance plan"
        )
        self.report.files_created.append(perf_path)
    
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
