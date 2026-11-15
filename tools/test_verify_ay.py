"""Regression checks for package metadata inspection in the legacy verifier."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.verify_ay import packages_positive, require_package_assets


class PackageAssetChecks(unittest.TestCase):
    def test_current_packages(self):
        packages_positive()

    def test_optional_package_cannot_replace_missing_core(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('carrier_control', 'carrier_controller_testbed'):
                package = root / 'src' / name
                package.mkdir(parents=True)
                (package / 'package.xml').write_text('<package/>')
            with patch('tools.verify_ay.ROOT', root):
                with self.assertRaisesRegex(AssertionError, 'missing core ROS package'):
                    packages_positive()

    def test_unexpected_package_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('carrier_control', 'carrier_description', 'unexpected'):
                package = root / 'src' / name
                package.mkdir(parents=True)
                (package / 'package.xml').write_text('<package/>')
            with patch('tools.verify_ay.ROOT', root):
                with self.assertRaisesRegex(AssertionError, 'unexpected ROS package'):
                    packages_positive()

    def test_helper_based_setup_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config").mkdir()
            (root / "config/plan.json").write_text("{}")
            (root / "setup.py").write_text(
                "from pathlib import Path\nfrom setuptools import setup\n"
                "def assets():\n    return [str(p) for p in Path('config').iterdir()]\n"
                "setup(data_files=[('share/example/config', assets())])\n"
            )
            previous = Path.cwd()
            require_package_assets(root, {"share/example/config/plan.json"})
            self.assertEqual(previous, Path.cwd())

    def test_omitted_asset_fails_even_with_old_glob_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "setup.py").write_text(
                "# glob('config/*')\nfrom setuptools import setup\n"
                "setup(data_files=[])\n"
            )
            with self.assertRaisesRegex(AssertionError, "missing installed assets"):
                require_package_assets(root, {"share/example/config/plan.json"})

    def test_missing_source_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "setup.py").write_text(
                "from setuptools import setup\n"
                "setup(data_files=[('share/example/config', ['config/plan.json'])])\n"
            )
            with self.assertRaisesRegex(AssertionError, "missing package source"):
                require_package_assets(root, {"share/example/config/plan.json"})

    def test_setup_exception_restores_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "setup.py").write_text("raise RuntimeError('setup failed')\n")
            previous = Path.cwd()
            with self.assertRaisesRegex(RuntimeError, "setup failed"):
                require_package_assets(root, set())
            self.assertEqual(previous, Path.cwd())


if __name__ == "__main__":
    unittest.main()
