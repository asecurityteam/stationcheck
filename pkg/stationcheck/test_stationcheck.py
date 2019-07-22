from pkg.stationcheck.stationcheck import station_check

test_command = "pip3 install pylint"
test_ve = "--version 2>&1 | sed -n 2p | cut -d ' ' -f2 | sed -n 1p | tr -d ','"
test_req = "1.9"
config = "pkg/config/requirements.yaml"
config_list = ["pip3 install pylint", "pip3 install pyyaml"]
s = station_check(config)

def test_print_results():
    '''Tests workstation results printing method'''
    assert s.print_results(8, 4, 3)

def test_bash():
    '''Tests stationcheck's bash wrapper'''
    stdout, err = s.bash(test_command)
    assert err is 0

def test_load_yaml():
    '''Tests whether or not our yaml will raise an error when loaded'''
    s.load_yaml(config)

def test_version_check():
    '''Tests that version comparison returns expected results'''
    assert s.version_check(test_command, test_ve, test_req)

def test_version_compare():
    '''Tests that version comparison returns expected results'''
    assert s.version_compare("2.22", "2.21")

def test_install_package():
    '''Tests that pip installs work'''
    stdout, err = s.install_package("pylint", "pip3 install")

def test_install_configs():
    '''Tests that configurations run successfully'''
    assert s.install_configs(config_list)
