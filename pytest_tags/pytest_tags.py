"""
Copyright (C) 2017 Planview, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import pytest


@pytest.fixture(scope='session')
def tags(request):
    """Return a base URL"""
    config = request.config
    tags = config.getoption('tags')
    if tags is not None:
        return tags


def pytest_addoption(parser):
    parser.addoption("--tags", action="store", nargs="+", dest="tags",
                     default=["all"], help="What tag(s) to run")
    parser.addini("exclusion_tags", "tests marked with tags in this list "
                                    "will not be included in test collection.",
                  type="args", default=[])


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "tags: mark test to run iff it has tag")


def pytest_collection_modifyitems(items, config):
    from . import tagging

    browser = get_browser(config)
    exclusion_tags = config.getini('exclusion_tags')
    tags_to_run = config.option.tags

    remaining = []
    deselected = []
    for item in items:
        tags = _get_test_tags(item)
        if tagging.should_run(tags_to_run, tags, browser, exclusion_tags):
            remaining.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = remaining


def pytest_collection_finish(session):
    """
    Print how many tests were actually selected and are going to be run.

    :param session: this py.test session
    :return: None
    """
    line = "selected " + str(len(session.items)) + " items\n"
    tr = session.config.pluginmanager.getplugin('terminalreporter')
    if tr:  # terminal reporter is not available when running with xdist
        tr.rewrite(line, bold=True)


def pytest_report_header(config):
    return 'tags: {0}'.format(', '.join(config.option.tags))


def get_browser(config):
    try:
        browser = config._capabilities['browserName']
    except (AttributeError, KeyError):
        browser = getattr(config.option, 'driver', None)
    return browser


def _get_test_tags(item):
    try:
        tags = list()
        for each in item.iter_markers('tags'):
            tags += each.args
        tags = set(tags) or 'all'
    except AttributeError:
        tags = item.get_marker('tags')
        tags = tags.args if tags else 'all'

    return list(tags)
