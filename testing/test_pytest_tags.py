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

pytest_plugins = 'pytester'


@pytest.fixture()
def test_file(testdir):
    testdir.makepyfile("""
        import pytest
        pytestmark = pytest.mark.tags("package")
        @pytest.mark.tags('one', 'two')
        def test_tag():
            pass
        @pytest.mark.tags('two', 'three')
        def test_second_tag():
            pass
        @pytest.mark.tags('two', 'not firefox')
        def test_second_b_tag():
            pass
        @pytest.mark.tags('three', 'not Chrome')
        def test_third_tag():
            pass
        @pytest.mark.tags('four', 'not Safari')
        def test_fourth_tag():
            pass
        @pytest.mark.tags('five', 'not safari')
        def test_fifth_tag():
            pass
        @pytest.mark.tags('four', 'five', 'filter')
        def test_four_and_five_tag():
            pass
        @pytest.mark.tags('six', 'not active')
        def test_six_tag():
            pass
        def test_no_tag():
            pass
        @pytest.mark.tags('dont', 'seven')
        def test_exclusion_tags():
            pass
        @pytest.mark.tags('seven')
        def test_seven_tag():
            pass
    """)
    return testdir


@pytest.fixture()
def test_conf(test_file):
    test_file.makeconftest("""
        def pytest_addoption(parser):
            parser.addoption("--driver", action="store", default="Firefox")
    """)
    return test_file


@pytest.fixture()
def test_ini(test_file):
    test_file.makefile('.ini', pytest="""
        [pytest]
        exclusion_tags = dont
    """)
    return test_file


def assert_outcomes(result, passed=1, skipped=0, deselected=0, failed=0,
                    xfailed=0, xpassed=0):
    outcomes = result.parseoutcomes()
    assert outcomes.get('passed', 0) == passed
    assert outcomes.get('skipped', 0) == skipped
    assert outcomes.get('deselected', 0) == deselected
    assert outcomes.get('failed', 0) == failed
    assert outcomes.get('xfailed', 0) == xfailed
    assert outcomes.get('xpassed', 0) == xpassed


def test_single_tag_one_result(test_file):
    result = test_file.runpytest('--tags', 'one')
    assert_outcomes(result, deselected=10)


def test_single_tag_multiple_results(test_file):
    result = test_file.runpytest('--tags', 'two')
    assert_outcomes(result, passed=3, deselected=8)


def test_multiple_tags(test_file):
    result = test_file.runpytest('--tags', 'two', 'four')
    assert_outcomes(result, passed=5, deselected=6)


def test_no_tag(test_file):
    result = test_file.runpytest()
    assert_outcomes(result, passed=10, deselected=1)


@pytest.mark.parametrize('tag', ['not three', '~three'])
def test_not_tag(test_file, tag):
    result = test_file.runpytest('--tags', 'two', tag)
    assert_outcomes(result, passed=2, deselected=9)


def test_filter_tag(test_file):
    result = test_file.runpytest('--tags', 'two+three')
    assert_outcomes(result, deselected=10)


def test_long_filter(test_file):
    result = test_file.runpytest('--tags', 'package+one+two')
    assert_outcomes(result, deselected=10)


def test_filter_combination(test_file):
    result = test_file.runpytest('--tags', 'two+three', 'seven')
    assert_outcomes(result, passed=3, deselected=8)


def test_filter_combination_diff_order(test_file):
    result = test_file.runpytest('--tags', 'seven', 'two+three')
    assert_outcomes(result, passed=3, deselected=8)


def test_filter_with_exclusion(test_file):
    result = test_file.runpytest(
        '--tags', 'two+three', 'four+five', 'not filter')
    assert_outcomes(result, deselected=10)


def test_multiple_filters(test_file):
    result = test_file.runpytest('--tags', 'two+three', 'four+five')
    assert_outcomes(result, passed=2, deselected=9)


def test_not_active(test_file):
    result = test_file.runpytest('--tags', 'six')
    assert_outcomes(result, passed=0, deselected=11)


def test_exclude_browser_default(test_conf):
    result = test_conf.runpytest('--tags', 'two')
    assert_outcomes(result, passed=2, deselected=9)


def test_exclude_browser_specified(test_conf):
    result = test_conf.runpytest('--driver', 'Chrome', '--tags', 'three')
    assert_outcomes(result, deselected=10)


def test_exclude_browser_case_insensitive(test_conf):
    result = test_conf.runpytest('--driver', 'Safari',
                                 '--tags', 'four', 'five')
    assert_outcomes(result, deselected=10)


def test_precedence(test_file):
    result = test_file.runpytest('--tags', 'two', 'not two')
    assert_outcomes(result, passed=0, deselected=11)


def test_all_tags(test_file):
    result = test_file.runpytest('--tags', 'all')
    assert_outcomes(result, passed=10, deselected=1)


def test_exclusion_tags(test_ini):
    result = test_ini.runpytest('--tags', 'seven')
    assert_outcomes(result, passed=1, deselected=10)


def test_header_selected_deselected(test_file):
    result = test_file.runpytest('--tags', 'seven', 'two+three')
    result.stdout.fnmatch_lines(["*selected 3 items*",
                                 "*8 deselected*"])


def test_header_output_no_tags(test_file):
    result = test_file.runpytest()
    result.stdout.fnmatch_lines(["tags: all"])


def test_header_output(test_file):
    result = test_file.runpytest('--tags', 'seven', 'two+three')
    result.stdout.fnmatch_lines(["tags: seven, two+three"])
