"""Check task routing rejects the wrong checkout and preserves failures/arguments."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WorkbenchTests(unittest.TestCase):
    def run_script(self, *args, env=None):
        return subprocess.run(['bash', str(ROOT / 'tools/workbench.sh'), *args],
                              cwd='/tmp', env=env, text=True, capture_output=True)

    def test_help_and_unknown_command_need_no_ros(self):
        self.assertEqual(self.run_script('--help').returncode, 0)
        self.assertEqual(self.run_script('unknown').returncode, 2)

    def test_missing_trial_does_not_create_an_output(self):
        before = set((ROOT / '.cambot-runs').glob('*'))
        result = self.run_script('analyze-run', '/definitely-missing/trials.csv')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(before, set((ROOT / '.cambot-runs').glob('*')))

    def test_container_mount_guard_and_exit_propagation(self):
        with tempfile.TemporaryDirectory() as temp:
            docker = Path(temp) / 'docker'
            docker.write_text('''#!/usr/bin/env python3
import os, sys, json
if sys.argv[1] == 'inspect':
    print('true' if '.State.Running' in sys.argv[3] else os.environ['FAKE_MOUNT'])
else:
    print(json.dumps(sys.argv[1:]))
    sys.exit(17)
''')
            docker.chmod(0o755)
            env = dict(os.environ, PATH=temp + os.pathsep + os.environ['PATH'],
                       CAMBOT_CONTAINER='test container', CAMBOT_WORKBENCH_INSIDE='0',
                       FAKE_MOUNT='/tmp')
            refused = self.run_script('build', env=env)
            self.assertEqual(refused.returncode, 2, refused.stderr)
            self.assertIn('different checkout', refused.stderr)
            env['FAKE_MOUNT'] = str(ROOT)
            passed = self.run_script('build', env=env)
            self.assertEqual(passed.returncode, 17, passed.stderr)
            args = json.loads(passed.stdout)
            self.assertIn('test container', args)
            self.assertEqual(args[-3:], ['bash', 'tools/workbench.sh', 'build'])

    def test_tasks_have_no_automatic_motion_dependency(self):
        tasks = json.loads((ROOT / '.vscode/tasks.json').read_text())['tasks']
        self.assertEqual(len(tasks), len({t['label'] for t in tasks}))
        for task in tasks:
            self.assertEqual(task['type'], 'process')
            self.assertNotIn('dependsOn', task)
            self.assertNotIn('runOptions', task)
        start = [t for t in tasks if t['args'][1] == 'start']
        self.assertEqual(len(start), 1)


if __name__ == '__main__':
    unittest.main()
