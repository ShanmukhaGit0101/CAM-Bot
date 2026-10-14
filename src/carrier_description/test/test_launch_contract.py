"""Offline launch contract tests that do not pretend ROS is available."""

import ast
from pathlib import Path
import unittest


LAUNCH = Path(__file__).parents[1] / "launch" / "dual_arm_demo.launch.py"


class TestLaunchContract(unittest.TestCase):
    def test_positive_launch_is_python_and_starts_required_visual_nodes(self):
        text = LAUNCH.read_text(encoding="utf-8")
        ast.parse(text)
        self.assertIn('package="robot_state_publisher"', text)
        self.assertIn('executable="machine_tending_coordinator"', text)
        self.assertIn('package="rviz2"', text)
        self.assertIn('default_value="visual_simulation"', text)

    def test_negative_launch_does_not_start_competing_joint_publishers(self):
        text = LAUNCH.read_text(encoding="utf-8")
        self.assertNotIn('executable="dual_arm_cycle"', text)
        self.assertNotIn('package="joint_state_publisher"', text)
        self.assertNotIn('package="joint_state_publisher_gui"', text)


if __name__ == "__main__":
    unittest.main()
