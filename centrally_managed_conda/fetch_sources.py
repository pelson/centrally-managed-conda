import argparse
import os.path
import sys

import conda_build.config
from conda_build_all.resolved_distribution import ResolvedDistribution
from conda_build_all.builder import list_metas


def main():
    parser = argparse.ArgumentParser(description='Fetch the source for all of the recipes in the given directory.')
    parser.add_argument('--recipes-directory', help='The directory to look for recipes.',
                        default='recipes')
    parser.add_argument('cache_directory', help='The directory to store the source cache.')
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
        conda_build.source.provide(os.path.dirname(meta.meta_path),
                                   meta.get_section('source'),
                                   patch=False)


if __name__ == '__main__':
    main()
