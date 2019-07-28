'''Runs unit tests on stationcheck'''
from pkg.stationcheck.stationcheck import station_check

TEST_COMMAND = "pip3 install pylint"
TEST_EXTRACTOR = "--version 2>&1 | sed -n 2p | cut -d ' ' -f2 | sed -n 1p | tr -d ','"
TEST_REQ = "1.9"
CONFIG = "pkg/config/requirements.yaml"
CONFIG_LIST = ["pip3 install pylint", "pip3 install pyyaml"]
TEST_SC = station_check(CONFIG)

def test_print_results():
    '''Tests workstation results printing method'''
    assert TEST_SC.print_results(8, 4, 3) is not False

def test_bash():
    '''Tests stationcheck's bash wrapper'''
    stdout, err = TEST_SC.bash(TEST_COMMAND)
    assert err is 0

def test_load_yaml():
    '''Tests whether or not our yaml will raise an error when loaded'''
    TEST_SC.load_yaml(CONFIG)

def test_version_check():
    '''Tests that version comparison returns expected results'''
    assert TEST_SC.version_check(TEST_COMMAND, TEST_EXTRACTOR, TEST_REQ)

def test_version_compare():
    '''Tests that version comparison returns expected results'''
    assert TEST_SC.version_compare("2.22", "2.21")

def test_install_package():
    '''Tests that pip installs work'''
    stdout, err = TEST_SC.install_package("pylint", "pip3 install")

def test_install_configs():
    '''Tests that configurations run successfully'''
    assert TEST_SC.install_configs(CONFIG_LIST)
