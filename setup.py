from setuptools import setup

setup(name='pytest-tags',
      use_scm_version=True,
      description='pytest plugin for taggging tests',
      long_description=open('README.rst').read(),
      author='Jim Brannlund',
      author_email='jbrannlund@planview.com',
      url='https://github.com/Projectplace/pytest-tags',
      packages=['pytest_tags'],
      entry_points={'pytest11': ['tags = pytest_tags.pytest_tags']},
      setup_requires=['setuptools_scm'],
      install_requires=['pytest>=2.9.0', 'pytest-selenium>=1.9.1'],
      license='Mozilla Public License 2.0 (MPL 2.0)',
      keywords='py.test pytest tags',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Framework :: Pytest',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
          'Operating System :: POSIX',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: MacOS :: MacOS X',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
          'Topic :: Utilities',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7'])
