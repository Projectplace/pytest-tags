import pytest

pytest_plugins = 'pytester'


@pytest.fixture()
def test_file(testdir):
    testdir.makepyfile("""
            import pytest
            @pytest.mark.tags('one', 'two')
            def test_tag():
                pass
            @pytest.mark.tags('two', 'three')
            def test_second_tag():
                pass
            @pytest.mark.tags('two')
            def test_second_b_tag():
                pass
            @pytest.mark.tags('three')
            def test_third_tag():
                pass
            @pytest.mark.tags('four')
            def test_fourth_tag():
                pass
            @pytest.mark.tags('five')
            def test_fifth_tag():
                pass
            @pytest.mark.tags('four', 'five')
            def test_four_and_five_tag():
                pass
            def test_no_tag():
                pass
    """)
    return testdir


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
    assert_outcomes(result, deselected=7)


def test_single_tag_multiple_results(test_file):
    result = test_file.runpytest('--tags', 'two')
    assert_outcomes(result, passed=3, deselected=5)


def test_multiple_tags(test_file):
    result = test_file.runpytest('--tags', 'two', 'four')
    assert_outcomes(result, passed=5, deselected=3)


def test_no_tag(test_file):
    result = test_file.runpytest()
    assert_outcomes(result, passed=8)


@pytest.mark.parametrize('tag', ['not three', '~three'])
def test_not_tag(test_file, tag):
    result = test_file.runpytest('--tags', 'two', tag)
    assert_outcomes(result, passed=2, deselected=6)


def test_filter_tag(test_file):
    result = test_file.runpytest('--tags', 'two+three')
    assert_outcomes(result, deselected=7)


def test_multiple_filters(test_file):
    result = test_file.runpytest('--tags', 'two+three', 'four+five')
    assert_outcomes(result, passed=2, deselected=6)
