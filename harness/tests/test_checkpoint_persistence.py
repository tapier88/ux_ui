"""
Tests for persistent checkpoint storage (CRITICAL-003 fix).

Run with: python -m unittest harness.tests.test_checkpoint_persistence -v
"""
import shutil
import tempfile
import unittest
from pathlib import Path

from harness.core.state import StateManager
from harness.core.state.storage import FileCheckpointStorage, InMemoryCheckpointStorage


class TestFileCheckpointStorage(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="harness_ckpt_test_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_checkpoint_survives_new_state_manager_instance(self):
        """Simulates a process restart: a fresh StateManager, same storage
        backend on disk, should be able to recover the task."""
        storage = FileCheckpointStorage(base_dir=self.tmp_dir)

        manager_before_restart = StateManager()
        manager_before_restart.attach_checkpoint_storage(storage)

        state = manager_before_restart.create_state(
            task_id="crash_recovery_task", status="running"
        )
        state.outputs["STEP_A"] = {"result": "done"}
        manager_before_restart.save_checkpoint(state, "STEP_A")
        state.outputs["STEP_B"] = {"result": "also done"}
        manager_before_restart.save_checkpoint(state, "STEP_B")

        # --- simulate process restart: brand new manager, no in-memory state ---
        manager_after_restart = StateManager()
        manager_after_restart.attach_checkpoint_storage(storage)

        self.assertIsNone(manager_after_restart.get_state("crash_recovery_task"))

        recovered = manager_after_restart.restore_task_from_persistent_storage(
            "crash_recovery_task"
        )

        self.assertIsNotNone(recovered)
        self.assertEqual(recovered.outputs.get("STEP_A"), {"result": "done"})
        self.assertEqual(recovered.outputs.get("STEP_B"), {"result": "also done"})
        self.assertEqual(len(recovered.checkpoints), 2)

    def test_checkpoint_files_written_to_disk(self):
        storage = FileCheckpointStorage(base_dir=self.tmp_dir)
        manager = StateManager()
        manager.attach_checkpoint_storage(storage)

        state = manager.create_state(task_id="disk_write_task")
        manager.save_checkpoint(state, "NODE_1")

        task_dir = Path(self.tmp_dir) / "disk_write_task"
        self.assertTrue(task_dir.exists())
        files = list(task_dir.glob("*.json"))
        self.assertEqual(len(files), 1)

    def test_restore_full_state_fields_med003(self):
        """MED-003 fix: restore must bring back inputs/current_node/status/errors,
        not just outputs/metadata/history."""
        storage = FileCheckpointStorage(base_dir=self.tmp_dir)
        manager = StateManager()
        manager.attach_checkpoint_storage(storage)

        state = manager.create_state(task_id="full_restore_task", inputs={"x": 1})
        state.current_node = "NODE_A"
        state.status = "running"
        state.add_error("NODE_A", "transient issue")
        manager.save_checkpoint(state, "NODE_A")

        checkpoint = state.get_last_checkpoint()

        # mutate state after the checkpoint to prove restore overwrites it
        state.inputs = {}
        state.current_node = None
        state.status = "unknown"
        state.errors = []

        state.restore_from_checkpoint(checkpoint)

        self.assertEqual(state.inputs, {"x": 1})
        self.assertEqual(state.current_node, "NODE_A")
        self.assertEqual(state.status, "running")
        self.assertEqual(len(state.errors), 1)

    def test_checkpoint_ids_are_unique_med007(self):
        manager = StateManager()
        state = manager.create_state(task_id="unique_id_task")
        c1 = manager.save_checkpoint(state, "NODE_X")
        c2 = manager.save_checkpoint(state, "NODE_X")
        self.assertNotEqual(c1.checkpoint_id, c2.checkpoint_id)


class TestInMemoryCheckpointStorageIsDefault(unittest.TestCase):
    """Confirms backward compatibility: StateManager with no storage
    attached behaves exactly as it did before (in-memory only)."""

    def test_no_storage_attached_by_default(self):
        manager = StateManager()
        state = manager.create_state(task_id="default_behavior_task")
        manager.save_checkpoint(state, "NODE_1")
        self.assertIsNone(manager.restore_task_from_persistent_storage("default_behavior_task"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
