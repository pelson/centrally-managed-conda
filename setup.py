from setuptools import setup
import versioneer


setup(
      name='centrally-managed-conda',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Tools and documentation for deploying centrally managed conda environments.',
      author='Phil Elson',
      author_email='pelson.pub@gmail.com',
      url='https://github.com/pelson/centrally-managed-conda',
      packages=['centrally_managed_conda'],
      entry_points={
          'console_scripts': [
              'fetch-conda-recipes = centrally_managed_conda.fetch_recipes:main',
          ]
      },
     )

