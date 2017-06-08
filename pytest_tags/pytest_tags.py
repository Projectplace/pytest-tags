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


def pytest_addoption(parser):
    parser.addoption("--tags", action="store", nargs="+", dest="tags",
                     default=["all"], help="What tag(s) to run")


def pytest_configure(config):
    from . import tagging

    config.addinivalue_line("markers",
                            "tags: mark test to run iff it has tag")

    # Create tags container based on command line parameters
    browser = None
    if hasattr(config.option, 'driver'):
        browser = config.option.driver.lower()

    config.parameter_tags = tagging.TagsParameter(browser,
                                                  config.option.tags)


def pytest_collection_modifyitems(items, config):
    """
    py.test hook for modifying collected items

    :param items: list of collected test
    :param config: py.test config module
    :return: None
    """
    from . import tagging

    remaining = []
    deselected = []
    for item in items:
        # Get all tags for this test (includes tags on class level if present)
        tags = item.get_marker("tags")

        if config.option.collectonly:
            info = item.parent.name.split("/")
            print({"name": item.name, "folder": info[3],
                   "module": info[4][:-3], "tags": tags.args})

        # This line fills two purposes. Handle the cases where '--tags'
        # 1) was omitted, this will run all tests except 'not active' and
        # 'awaiting_fix' ones.
        # 2) has no arguments (a case that can occur when running in Docker).
        tags = tags.args + ('all',) if tags else ['all']

        # Create a list of the tags
        tags_list = tagging.TagsCollection.build_tags_list(tags)

        # Determine if test should be run depending on the parameter tags
        # See also: pytest_configure hook
        if config.parameter_tags.should_pick_up(tags_list):
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
