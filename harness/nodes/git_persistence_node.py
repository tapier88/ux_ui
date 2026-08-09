"""
GitPersistenceNode - Wires the Git Persistence module (Inspector,
Persistence, Publication, Validator) into the graph execution engine.

Before this node existed, harness/core/git/* was fully implemented and
covered by unit tests, but nothing in harness/nodes/ ever called it -
so the Task Completion Lifecycle documented in README.md
(IMPLEMENTING -> ... -> COMPLETE) was not actually enforced during a
real run of the graph. External tooling could commit and push on its
own, bypassing the sensitive-file check, the commit gate, and the
publication gate entirely. This node closes that gap: it is the single
place a task goes through stage -> commit -> sync-with-main -> publish
-> verify, using the existing, already-tested classes.

Usage inside a graph:

    from harness.nodes.git_persistence_node import GitPersistenceNode

    node = GitPersistenceNode(repo_path=".", base_branch="main")
    result = node.execute(state)
    if not result["can_complete"]:
        # state.status should stay INCOMPLETE / PUBLICATION_REQUIRED;
        # surface result["reason"] to the agent or the human operator.
        ...
"""
from typing import Any, Optional

from harness.core.graph import NodeType
from harness.core.state import TaskState
from harness.core.git.inspector import GitInspector
from harness.core.git.persistence import GitPersistence
from harness.core.git.publication import LocalPublicationProvider
from harness.core.git.validator import GitValidator
from harness.nodes import BaseNode


class GitPersistenceNode(BaseNode):
    """
    Runs the full commit -> sync -> publish -> verify sequence for a
    task and reports whether the task can be marked COMPLETE.

    Expects on state.inputs (all optional, sensible defaults applied):
        commit_message (str): message for the commit, if there are
            changes to commit. Defaults to a message derived from
            state.task_id.
        tests_passed (bool): whether the task's tests passed. Defaults
            to True; pass this through explicitly from a preceding
            test-running node rather than relying on the default.
        base_branch (str): branch to sync against before publishing.
            Defaults to the value passed to the node constructor.
    """

    def __init__(
        self,
        node_id: str = "GIT_PERSISTENCE_NODE",
        name: str = "Git Persistence Node",
        repo_path: str = ".",
        base_branch: str = "main",
    ):
        super().__init__(node_id, name, NodeType.STANDARD)
        self.repo_path = repo_path
        self.base_branch = base_branch

    def execute(self, state: TaskState) -> dict:
        inspector = GitInspector(self.repo_path)
        persistence = GitPersistence(self.repo_path, inspector)
        publisher = LocalPublicationProvider(self.repo_path, inspector)
        validator = GitValidator(self.repo_path, inspector, persistence, publisher)

        task_id = state.task_id
        tests_passed = bool(state.inputs.get("tests_passed", True))
        base_branch = state.inputs.get("base_branch", self.base_branch)
        commit_message = state.inputs.get(
            "commit_message", f"Task {task_id}: harness commit"
        )

        # 1. Commit gate - sensitive files, tests passed
        gate_ok, gate_msg = validator.validate_commit_gate(task_id, tests_passed)
        if not gate_ok:
            return self._result(task_id, False, gate_msg, stage="commit_gate")

        # 2. Commit any pending changes (no-op if already clean)
        commit_info = None
        if persistence.has_changes():
            commit_info = persistence.create_commit(commit_message)
            if commit_info is None:
                return self._result(
                    task_id, False, "Commit failed", stage="commit"
                )

        commit_sha = (
            commit_info.sha if commit_info else persistence.get_current_commit_sha()
        )
        if not commit_sha:
            return self._result(
                task_id, False, "No commit available to publish", stage="commit"
            )

        # 3. Sync with base branch + publish. This is the step that was
        # previously missing entirely - see publication.py.
        prepared = publisher.prepare_publication(base_branch=base_branch)
        if not prepared:
            status = publisher.get_publication_status()
            return self._result(
                task_id,
                False,
                f"Could not sync with {base_branch} before publishing "
                f"(status={status.value}). Resolve conflicts locally and retry.",
                stage="sync",
            )

        published = publisher.publish()
        if not published:
            status = publisher.get_publication_status()
            return self._result(
                task_id,
                False,
                f"Publication did not complete (status={status.value})",
                stage="publish",
            )

        # 4. Verify + can_complete
        can_complete, reason, persistence_state = validator.can_complete_task(
            task_id, commit_sha, tests_passed
        )

        return self._result(
            task_id,
            can_complete,
            reason,
            stage="verify",
            commit_sha=commit_sha,
            persistence_state=persistence_state.value,
        )

    @staticmethod
    def _result(
        task_id: str,
        can_complete: bool,
        reason: str,
        stage: str,
        commit_sha: Optional[str] = None,
        persistence_state: Optional[str] = None,
    ) -> dict:
        return {
            "node": "GitPersistenceNode",
            "task_id": task_id,
            "can_complete": can_complete,
            "reason": reason,
            "stage": stage,
            "commit_sha": commit_sha,
            "persistence_state": persistence_state,
        }
