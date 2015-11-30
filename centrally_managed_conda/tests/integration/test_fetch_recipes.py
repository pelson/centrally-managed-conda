import shutil
import tempfile
import unittest

from centrally_managed_conda import fetch_recipes


class Test(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(suffix='fetch_recipes')
        # TODO:
        # * Create a local repo which can be used to clone from.
        # * Put stuff in the target, and assert it is removed
        # * use different refs (i.e. not master)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_branch(self):
        defn = [{'git_url': 'git@github.com:SciTools/conda-recipes-scitools.git',
                 'git_ref': 'master'}]
        fetch_recipes.fetch_recipes(defn, self.tmp_dir) 

    def test_sha(self):
        defn = [{'git_url': 'git@github.com:SciTools/conda-recipes-scitools.git',
                 'git_ref': '01dced15fbef8c5fec492ab2602db0ea49018ab7'}]
        fetch_recipes.fetch_recipes(defn, self.tmp_dir) 


if __name__ == '__main__':
    unittest.main()
