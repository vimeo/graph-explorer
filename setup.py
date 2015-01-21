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
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup_params = dict(
    author='Dieter Plaetinck',
    author_email='dieter@plaetinck.be',
    version='2.0.4',
    license='apache2',
    setup_requires=["setuptools_git >= 0.3", ],
    url='http://vimeo.github.io/graph-explorer/',
    description='A graphite dashboard powered by structured metrics',
    name="graph-explorer",
    packages=find_packages(),
    package_data={'graph_explorer': [
        'templates/*.tpl',
        'templates/dashboards/*.tpl',
        'assets/*.html',
        'assets/img/*',
        'assets/css/*',
        'assets/js/*',
        'timeserieswidget/*.js',
        'timeserieswidget/flot/*.js',
        'timeserieswidget/highcharts/*.js',
        'timeserieswidget/highcharts/modules/*.js',
        'timeserieswidget/rickshaw/*.css',
        'timeserieswidget/rickshaw/*.js'
    ]},
    scripts=glob("bin/*.py"),
    install_requires=[
        "bottle==0.11.6",
        "urllib3==1.7.1",  # 71f84f9ab29b9a2818a138fa000bcf75bb05812a
        "elasticsearch==0.4.3",  # 422d43f4f8c981a5d93b06eefc3ce8f261cfb48c
        "paste==1.7.5.1",
        "wtforms",
        "argparse"
    ],
    tests_require=[
        "pytest>=2.5.2",
    ],
    cmdclass={"test": PyTest},
    include_package_data=True,
)

if __name__ == '__main__':
    setup(**setup_params)
