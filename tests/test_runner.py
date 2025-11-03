import pytest
import gtfs_loader
from gtfs_loader import test_support


test_support.init(__file__)


@pytest.mark.parametrize('feed_dir',
                         test_support.find_tests(),
                         ids=lambda test_dir: test_dir.name)
def test_default(feed_dir):
    do_test(feed_dir)


def do_test(feed_dir):
    itineraries = 'itineraries' in feed_dir.name
    work_dir = test_support.create_test_data(feed_dir)

    gtfs = gtfs_loader.load(work_dir, verbose=False, itineraries=itineraries)
    gtfs_loader.patch(gtfs, work_dir, work_dir, verbose=False, itineraries=itineraries)
    test_support.check_expected_output(feed_dir, work_dir)
