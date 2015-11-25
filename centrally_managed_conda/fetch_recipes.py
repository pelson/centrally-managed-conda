import os
import git
import shutil


def clean_clone(repo_uri, target):
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

    # Point at origin/master, and clean the repo in case it has been modified.
    repo.head.reference = repo.remotes.origin.refs.master
    repo.git.clean('-xdf')
    return repo


def fetch_recipes(repo_urls, target):
    repos = []
    for repo_url in repo_urls:
        repo_dir = os.path.join(target, repo_name(repo_url))
        repos.append(clean_clone(repo_url, repo_dir))

    working_dirs = [repo.working_dir for repo in repos]
    # Clear out any files which aren't part of this recipes specification.
    for fname in os.listdir(target):
        fpath = os.path.abspath(os.path.join(target, fname))
        if fpath not in working_dirs:
            print('Removing {}'.format(fpath))
            shutil.rmtree(fpath)


def repo_name(repo_url):
    # Compute the name of a directory for a git repo.
    name = repo_url
    replacement_chars = [':', '/', '\\', '@']
    for char in replacement_chars:
        name = name.replace(char, '-')

    return name


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch conda recipes from git.')
    parser.add_argument('--recipes-directory', default='recipes',
                        help='The directory to put the recipes into.')
    parser.add_argument('repos', nargs='+',
                        help='The repos from which to find recipes.')

    args = parser.parse_args()
    fetch_recipes(args.repos, args.recipes_directory)


if __name__ == '__main__':
    main()
