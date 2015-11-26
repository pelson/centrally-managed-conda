import argparse
import os.path
import sys

import conda.api
import conda.resolve

import conda_build.config
from conda_build_all.resolved_distribution import ResolvedDistribution
from conda_build_all.builder import list_metas


def main():
    parser = argparse.ArgumentParser(description='Resolve the URIs of the dependnencies of a distribution.')
    parser.add_argument('specs', nargs="+", help='The distributuion(s) to resolve.')
    parser.add_argument('--output', help='The file to output.', default='packages.txt')
    parser.add_argument('--channels', '-c', help='The channels to use when looking for distributions (defaults is not added automatically).',
                        default=[], action='append')
    args = parser.parse_args()
    print(args)
    index = conda.api.get_index(channel_urls=args.channels,
                                prepend=False)
    resolver = conda.resolve.Resolve(index)
    solved_pkgs = resolver.solve(args.specs)

    with open(args.output, 'w') as fh:
        for pkg in sorted(solved_pkgs):
            fh.write('{}{}\n'.format(index[pkg]['channel'], pkg))


if __name__ == '__main__':
    main()
