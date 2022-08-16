"""
Provides a framework for creating unit tests for projects based on 
py-gtfs-loader. All test suites must follow a common structure:

test_something/ - A test case must begin with test_.
    input/ - An input GTFS feed to be loaded into the tool.
    expected_default/ - The output the tool is expected to produce.
    expected_abc/ - The same input data can be used for several related tests with different expected outputs.
        A test runner can use `tag='abc'` to compare against the `abc` data for example.

See tests/ in this repo for a simple example of the framework in use.
"""


from pathlib import Path
import tempfile
import shutil
import os


def init(caller_location):
    """
    Prepare to run tests by setting up paths and creating temporary directories.
    """

    global TEST_DIR
    global WORK_DIR

    TEST_DIR = Path(caller_location).parent.resolve()
    WORK_DIR = TEST_DIR / '.work'
    WORK_DIR.mkdir(exist_ok=True)


def find_tests(tag='default'):
    """
    Discover directories containing test feeds with a certain tag.
    """

    test_dirs = []
    for dirent in TEST_DIR.iterdir():
        if dirent.is_dir() and dirent.name.startswith('test_'):
            if not any(dirent.glob(f'expected_{tag}')):
                continue

            test_dirs.append(dirent)

    return test_dirs


def create_test_data(feed_dir):
    """
    Combine the base files from the feed (common to all tests) with the input
    files for a particular test case, in a temporary directory. The name of 
    this directory is returned.
    """

    work_dir = Path(tempfile.mkdtemp(prefix='', dir=WORK_DIR))

    for filename in (TEST_DIR / 'base').iterdir():
        shutil.copy2(filename, work_dir / filename.name)

    for filename in (feed_dir / 'input').iterdir():
        shutil.copy2(filename, work_dir / filename.name)

    print(f'Testing feed in {work_dir}')
    return work_dir


def check_expected_output(feed_dir, work_dir, tag='default'):
    """
    Check whether work_dir contains the expected output. If successful, work_dir
    will be removed at the end of the test.
    """

    expected_dir = feed_dir / f'expected_{tag}'
    
    for expected_filename in (feed_dir / expected_dir).iterdir():
        actual_filename = work_dir / expected_filename.name
        check_file(expected_filename, actual_filename)

    shutil.rmtree(work_dir)


def check_file(expected_filename, actual_filename):
    """
    Check that two files are identical and print a readable diff if not.
    Works best on CSV files
    """

    with open(actual_filename) as actual_fp:
        actual_text = [line.strip() for line in actual_fp.readlines()]

    with open(expected_filename) as expected_fp:
        expected_text = [line.strip() for line in expected_fp.readlines()] 

    check_snapshot_update(expected_filename, expected_text, actual_text)
    assert actual_text == expected_text


def check_snapshot_update(expected_filename, expected_text, actual_text):
    """
    If UPDATE_SNAPSHOTS=1 and the test fails because the expected output files
    are obsolete, update the expected files to match the test.
    """

    if not int(os.environ.get('UPDATE_SNAPSHOTS', 0)):
        return

    if actual_text == expected_text:
        return

    with open(expected_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(actual_text))
        print(f'Updated {expected_filename}')
