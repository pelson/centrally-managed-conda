import argparse
from collections import OrderedDict
import itertools
import os.path
import shutil
import sys

import conda_build.config
from conda_build_all.resolved_distribution import ResolvedDistribution
from conda_build_all.builder import list_metas


def flatten_metas(meta_iterables):
    """
    Take a collection of metas, and compose/flatten/project into a single list.

    For example:

        A: pkg1, pkg2a
        B: pkg2b, pkg3

        Flattened([A, B]) => [pkg1, pkg2a, pkg3]
        Flattened([B, A]) => [pkg1, pkg2b, pkg3]

    The resulting list of metas will not be ordered in any particular way.

    """
    visited = {}
    for metas in meta_iterables:
        visited_this_depth = {}
        for meta in metas:
            if meta.name() not in visited:
                visited_this_depth.setdefault(meta.name(), []).append(meta)
        for name, metas in visited_this_depth.items():
            visited.setdefault(name, []).extend(metas)
    return itertools.chain.from_iterable(visited.values())


def main():
    parser = argparse.ArgumentParser(description='Removing duplicate recipes which are lower down the pecking order.')
    parser.add_argument('recipes_dirs', nargs="+",
                        help=("The directories containing recipes which should be 'flattened'."))
    parser.add_argument('--output-dir', help='Directory which should be created containing flattened recipes.',
                        default='flattened_recipes')
    args = parser.parse_args()

    meta_collections = OrderedDict([(recipes_dir, list_metas(recipes_dir))
                                    for recipes_dir in args.recipes_dirs])

    flattened = list(flatten_metas(meta_collections.values()))

    flattened_collections = OrderedDict()
    for recipe_dir, metas in meta_collections.items():
        for meta in metas:
            if meta in flattened:
                flattened_collections.setdefault(recipe_dir, []).append(meta)
 
    for recipe_dir, metas in flattened_collections.items():
        recipes_parent_dir = os.path.dirname(os.path.abspath(recipe_dir))
        for meta in metas:
            # Figure out where the recipe is, relative to the recipe dir
            meta_dir = os.path.relpath(os.path.abspath(meta.path), recipes_parent_dir)
            target_locn = os.path.join(args.output_dir, meta_dir)
            shutil.copytree(meta.path, target_locn)
            print('Copying {}'.format(meta_dir))
       

if __name__ == '__main__':
    main()
