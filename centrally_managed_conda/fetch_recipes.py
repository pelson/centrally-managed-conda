import os
import git
import shutil

import yaml


def clean_clone(repo_uri, target, remote_ref='master'):
    if os.path.exists(target):
        repo = git.Repo(target)
        remote_names = [remote.name for remote in repo.remotes]
        if 'origin' in remote_names and repo.remotes.origin.url != repo_uri:
            repo.delete_remote('origin')
            repo.create_remote('origin', repo_uri)
        elif 'origin' not in remote_names:
            repo.create_remote('origin', repo_uri)
        repo.remotes.origin.fetch()
    else:
        repo = git.Repo.clone_from(repo_uri, target)

    # Point at <remote_ref>, and clean the repo in case it has been modified.
    if remote_ref in repo.remotes.origin.refs:
        repo.head.reference = repo.remotes.origin.refs[remote_ref]
    else:
        repo.git.checkout(remote_ref)
    repo.git.clean('-xdf')
    return repo


def fetch_recipes(repo_defns, target):
    repo_directories = []
    for repo in repo_defns:
        if 'git_url' in repo:
            url = repo['git_url']
            ref = repo.get('git_ref', 'origin/master')
            repo_dir = os.path.join(target, repo_name(url, ref))
            repo_directories.append(clean_clone(url, repo_dir, ref).working_dir)
        else:
            raise ValueError('The repo definition {} is not '
                             'supported.'.format(repo))

    # Clear out any files which aren't part of repo_defns.
    for fname in os.listdir(target):
        fpath = os.path.abspath(os.path.join(target, fname))
        if fpath not in repo_directories:
            print('Removing {}'.format(fpath))
            shutil.rmtree(fpath)


def repo_name(repo_url, repo_ref='master'):
    # Compute the name of a directory for a git repo.
    name = repo_url
    ref = repo_ref
    replacement_chars = [':', '/', '\\', '@']
    for char in replacement_chars:
        name = name.replace(char, '-')
        ref = ref.replace(char, '-')

    return name + '__' + ref


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch conda recipes from git.')
    parser.add_argument('--recipes-directory', default='recipes',
                        help='The directory to put the recipes into.')
    parser.add_argument('recipes_sources',
                        help=("The source.yaml file describing the recipe "
                              "sources."))

    args = parser.parse_args()
    with open(args.recipes_sources, 'r') as fh:
        repo_definitions = yaml.safe_load(fh)
    fetch_recipes(repo_definitions, args.recipes_directory)


if __name__ == '__main__':
    main()
