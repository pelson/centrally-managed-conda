# TODO: Bring as much of this as possible into conda_build.source

import argparse
import os.path
from os.path import join, abspath, expanduser, isdir, isfile
import sys

from conda_build import external
from conda.fetch import download
import conda_build.config
from conda_build_all.resolved_distribution import ResolvedDistribution
from conda_build_all.builder import list_metas
from conda_build.utils import rm_rf, tar_xf, unzip, execute


def download_to_cache(meta, SRC_CACHE):
    ''' Download a source to the local cache. '''
    print('Source cache directory is: %s' % SRC_CACHE)
    if not isdir(SRC_CACHE):
        os.makedirs(SRC_CACHE) 

    fn = meta['fn'] 
    path = join(SRC_CACHE, fn)
    
    if isfile(path):
        print('Found source in cache: %s' % fn) 
    else:
        print('Downloading source to cache: %s' % fn)
        if not isinstance(meta['url'], list):
            meta['url'] = [meta['url']]

        for url in meta['url']:
            print("Downloading %s" % url)
            download(url, path)
            break
        else: # no break
            raise RuntimeError("Could not download %s" % fn)


def git_source(meta, recipe_dir, GIT_CACHE):
    if not isdir(GIT_CACHE):
        os.makedirs(GIT_CACHE)

    git = external.find_executable('git')
    if not git:
        sys.exit("Error: git is not installed")
    git_url = meta['git_url']
    if git_url.startswith('.'):
        # It's a relative path from the conda recipe
        os.chdir(recipe_dir)
        git_dn = abspath(expanduser(git_url))
        git_dn = "_".join(git_dn.split(os.path.sep)[1:])
    else:
        git_dn = git_url.split(':')[-1].replace('/', '_')
    cache_repo = cache_repo_arg = join(GIT_CACHE, git_dn)

    # update (or create) the cache repo
    print('Fetch {}'.format(git_url))
    if isdir(cache_repo):
        execute([git, 'fetch'], cwd=cache_repo, check_exit_code=True)
    else:
        execute([git, 'clone', '--mirror', git_url, cache_repo_arg],
                cwd=recipe_dir, check_exit_code=True)
        assert isdir(cache_repo)


def svn_source(meta, SVN_CACHE):
    ''' Download a source from SVN repo. '''
    def parse_bool(s):
        return str(s).lower().strip() in ('yes', 'true', '1', 'on')

    svn = external.find_executable('svn')
    if not svn:
        sys.exit("Error: svn is not installed")
    svn_url = meta['svn_url']
    svn_revision = meta.get('svn_rev') or 'head'
    svn_ignore_externals = parse_bool(meta.get('svn_ignore_externals') or 'no')
    if not isdir(SVN_CACHE):
        os.makedirs(SVN_CACHE)
    svn_dn = svn_url.split(':', 1)[-1].replace('/', '_').replace(':', '_')
    cache_repo = join(SVN_CACHE, svn_dn)
    if svn_ignore_externals:
        extra_args = ['--ignore-externals']
    else:
        extra_args = []
    if isdir(cache_repo):
        execute([svn, 'up', '-r', svn_revision] + extra_args,
                cwd=cache_repo, check_exit_code=True)
    else:
        execute([svn, 'co', '-r', svn_revision] + extra_args +
                [svn_url, cache_repo], check_exit_code=True)
        assert isdir(cache_repo)


def fetch_to_source_cache(meta, source_cache_root):
    orig_meta = meta
    meta = meta.get_section('source')
    if 'fn' in meta:
        download_to_cache(meta, join(source_cache_root, 'src_cache'))
    elif 'git_url' in meta:
        git_source(meta, os.path.dirname(orig_meta.meta_path),
                   join(source_cache_root, 'git_cache'))
    elif 'hg_url' in meta:
        raise NotImplementedError('hg source not yet implemented.')
    elif 'svn_url' in meta:
        svn_source(meta, join(source_cache_root, 'svn_cache'))
    elif 'path' in meta:
        pass
    else: # no source
        pass


def main():
    parser = argparse.ArgumentParser(description='Fetch the source for all of the recipes in the given directory.')
    parser.add_argument('--recipes-directory', help='The directory to look for recipes.',
                        default='recipes')
    parser.add_argument('cache_directory', help='The directory to store the source cache (aka the conda build root).')
    args = parser.parse_args()

    source_cache = os.path.abspath(args.cache_directory)
    recipes_directory = os.path.join(args.recipes_directory)
    if not os.path.exists(source_cache):
        os.makedirs(source_cache)

    # We import conda_build.config, set a value, remove conda_build.config, and re-import it.
    # We do this because conda_build has import time resolution on some of the conda_build.source
    # variables (e.g. SRC_CACHE).
    import conda_build.config
    conda_build.config.config.croot = source_cache
    sys.modules.pop('conda_build.source', None)
    import conda_build.source

    visited_sources = set()
    for meta in list_metas(recipes_directory):
        fetch_to_source_cache(meta, source_cache)


if __name__ == '__main__':
    main()
