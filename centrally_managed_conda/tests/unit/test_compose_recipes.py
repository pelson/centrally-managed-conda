import os
import subprocess
import sys
import unittest

from conda_build_all.tests.unit.dummy_index import DummyPackage, DummyIndex
from conda_build_all.tests.integration.test_builder import RecipeCreatingUnit

from centrally_managed_conda.compose_recipes import flatten_metas


class Test_flatten_metas(unittest.TestCase):
    def setUp(self):
        self.pkgs = {'a': DummyPackage('a', version='1.0'),
                     'b': DummyPackage('b', version='2.1'),
                     'c3': DummyPackage('c', version='3.2'),
                     'c4': DummyPackage('c', version='4.5'),
                    }

    def test(self):
        channel1 = [self.pkgs['a'], self.pkgs['c3']]
        channel2 = [self.pkgs['a'], self.pkgs['b'], self.pkgs['c4']]

        pkgs = flatten_metas([channel1, channel2])

        dists = sorted([pkg.dist() for pkg in pkgs])
        self.assertEqual(dists, ['a-1.0-0', 'b-2.1-0', 'c-3.2-0'])

        pkgs = flatten_metas([channel2, channel1])

        dists = sorted([pkg.dist() for pkg in pkgs])
        self.assertEqual(dists, ['a-1.0-0', 'b-2.1-0', 'c-4.5-0'])


class Test_cli(RecipeCreatingUnit):
    def test(self):
        a1 = self.write_meta(os.path.join('channel1', 'a'),
                             """
                             package:
                                 name: a
                                 version: 1
                             """)
        a2 = self.write_meta(os.path.join('channel2', 'a'),
                             """
                             package:
                                 name: a
                                 version: 2
                             """)
        b1 = self.write_meta(os.path.join('channel1', 'b'),
                             """
                             package:
                                 name: b
                                 version: 1
                             """)
        c1 = self.write_meta(os.path.join('channel2', 'c'),
                             """
                             package:
                                 name: c
                                 version: 1
                             """)

        channel1 = os.path.join(self.recipes_root_dir, 'channel1')
        channel2 = os.path.join(self.recipes_root_dir, 'channel2')
        output = os.path.join(self.recipes_root_dir, 'flattened_recipes')

        out = subprocess.check_output([sys.executable, '-m', 'centrally_managed_conda.compose_recipes',
                                     '--output-dir={}'.format(output),
                                     channel1, channel2])
        self.assertEqual(out.strip().decode('utf-8'),
                         '\n'.join(['Copying channel1/a',
                                    'Copying channel1/b',
                                    'Copying channel2/c']))
        if out.strip():
            print(out.decode('utf-8'))
        # Check they are all there, except for a2.
        self.assertTrue(os.path.exists(os.path.join(output, 'channel1', 'a')))
        self.assertTrue(os.path.exists(os.path.join(output, 'channel1', 'b')))
        self.assertTrue(os.path.exists(os.path.join(output, 'channel2', 'c')))
        self.assertFalse(os.path.exists(os.path.join(output, 'channel2', 'a')))


if __name__ == '__main__':
    unittest.main()
