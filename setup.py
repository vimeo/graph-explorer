from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from glob import glob
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup_params = dict(
    setup_requires=["setuptools_git >= 0.3",],
    name="graph-explorer",
    description="Graph-Explorer",
    packages=find_packages(),
    scripts=glob("bin/*.py"),
    install_requires=[
        "bottle==0.11.6",
        "urllib3==1.7.1", # 71f84f9ab29b9a2818a138fa000bcf75bb05812a
        "elasticsearch==0.4.3",  # 422d43f4f8c981a5d93b06eefc3ce8f261cfb48c
        "paste==1.7.5.1",
        "wtforms",
    ],
    tests_require=[
        "pytest>=2.5.2",
    ],
    cmdclass={"test": PyTest},
    include_package_data=True,
)

if __name__ == '__main__':
    setup(**setup_params)
