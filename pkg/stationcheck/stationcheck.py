'''A workstation check for up-to-date packages and languages'''
#!/usr/bin/env python3

import subprocess
import argparse
import os
from packaging import version #setuptools
import yaml


PACKAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
REQ_FILE = os.path.join(PACKAGE_DIR, "pkg/config/requirements.yaml")

#pylint: disable=too-few-public-methods, invalid-name
class bcolors:
    '''A strucut for commonly used terminal colors'''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    VIOLET = '\033[35m'

#pylint: disable=invalid-name
class station_check:
    '''Checks, updates, and otherwise sets up a SecDev workstation to meet our requirements'''

    #pylint: disable=unused-argument
    def __init__(self, config_file=REQ_FILE, verbose=False, test=False):
        '''Reads in requirements YAML file, checks versions, and installs
        out-of-date or missing packages.'''

        config = self.load_yaml(config_file)

        print("\n%s%s Workstation Setup%s\n" % (bcolors.WARNING, config["version"], bcolors.ENDC))

        successes = 0
        failures = 0
        installs = 0

        for installer in config["installers"]:
            if "configurations" in config["installers"][installer].keys():
                self.install_configs(config["installers"][installer]["configurations"])
        print("--------------------")
        for package in config["packages"]:
            if package != "default":
                print("%s%s %s%s%s check: %s" % (bcolors.OKBLUE,
                                                 config["packages"][package]["display"],
                                                 bcolors.VIOLET,
                                                 config["requirements"][package],
                                                 bcolors.OKBLUE,
                                                 bcolors.ENDC), end='')
                v_check = self.version_check(config["packages"][package]["command"],
                                             config["packages"][package]["version_extraction"],
                                             config["requirements"][package])

                if v_check:
                    successes += 1
                elif not v_check and not v_check == "invalid":

                    print("%sInstalling newer version of %s...%s" %
                          (bcolors.WARNING,
                           config["packages"][package]["display"],
                           bcolors.ENDC))

                    if "installer" not in config["packages"][package]:
                        installer = config["packages"]["default"]["installer"]
                    else:
                        installer = config["packages"][package]["installer"]

                    if "install_command" in config["packages"][package].keys():
                        command = config["packages"][package]["install_command"]
                    else:
                        command = config["packages"][package]["command"]

                    stdout, err = self.install_package(command,
                                                       config["installers"][installer]["command"])

                    if err == 0:
                        successes += 1
                        installs += 1
                        print("%sSuccess!%s" % (bcolors.OKGREEN, bcolors.ENDC))
                    else:
                        failures += 1
                        print("%sInstallation failed.%s" % (bcolors.FAIL, bcolors.ENDC))
                        print(stdout)

                print("--------------------")

        self.print_results(successes, failures, installs)

    #pylint: disable=no-self-use
    def print_results(self, successes, failures, installs):
        '''Prints outcome of workstation check'''
        total = successes + failures
        print("%sPackages installed: %s%s%s" % (bcolors.OKGREEN,
                                                bcolors.VIOLET,
                                                str(installs),
                                                bcolors.ENDC))
        #pylint: disable=literal-comparison
        if failures is not 0:
            print("%sInstallations failed: %s%s" % (bcolors.WARNING,
                                                    str(failures),
                                                    bcolors.ENDC))
            print("%sFAIL: %s packages out of %s meet requirements.%s" % (bcolors.FAIL,
                                                                          str(successes),
                                                                          str(total),
                                                                          bcolors.ENDC))
            return False
        else:
            print("%sPASS: %s packages out of %s meet requirements!%s" % (bcolors.OKGREEN,
                                                                          str(successes),
                                                                          str(total),
                                                                          bcolors.ENDC))
            return True

    def bash(self, command):
        '''Evaluates a string as a bash command.'''
        run = subprocess.run(command,
                             shell=True,
                             text=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             executable='/bin/bash')

        #pylint: disable=literal-comparison
        if run.returncode is not 0:

            print("%sExit code: %s%s" % (bcolors.FAIL,
                                         str(run.returncode),
                                         bcolors.ENDC))

            print("%sFailed to run: %s%s" % (bcolors.FAIL,
                                             command,
                                             bcolors.ENDC))

        return run.stdout, run.returncode

    def load_yaml(self, yaml_file):
        '''Loads a yaml file as a dict.'''
        config_file = open(yaml_file, 'r')
        return yaml.safe_load(config_file)

    def version_check(self, command, extractor, version_req):
        '''Checks if the install version of a package meets requirement'''

        extracted_version, err = self.bash(command + " " + extractor)
        return self.version_compare(extracted_version.rstrip('\n'), version_req)

    def version_compare(self, extracted, requirement):
        '''Compares two versions'''

        more_recent = False

        try:
            version.Version(extracted)
            more_recent = version.parse(extracted) >= version.parse(requirement)
        except (version.InvalidVersion, TypeError):

            if str(extracted) == "":
                return False
            print("%sExtracted version number (%s) appears to be an invalid format. \
                    Consider updating your version extraction command.%s" % (bcolors.FAIL,
                                                                             str(extracted),
                                                                             bcolors.ENDC))
            return "invalid"



        if more_recent:
            print("%sFound %s!%s" % (bcolors.OKGREEN,
                                     extracted,
                                     bcolors.ENDC))
        else:
            print("%sFound %s!%s" % (bcolors.WARNING,
                                     extracted,
                                     bcolors.ENDC))

        return more_recent

    def install_package(self, install_name, install_script):
        '''Installs a package'''

        return self.bash(install_script + " " + install_name)

    def install_configs(self, config_list):
        '''Runs configuration commands listed under an installer in the config file'''
        failed_installs = 0
        for configuration in config_list:
            stdout, err = self.bash(configuration)
            #pylint: disable=literal-comparison
            if err is not 0:
                print("%sFailed to run: %s%s" % (bcolors.FAIL,
                                                 bcolors.ENDC,
                                                 configuration))
                failed_installs += 1
            print("%sInstaller configuration: %s%s" % (bcolors.OKGREEN,
                                                       bcolors.ENDC,
                                                       configuration))
        if failed_installs != 0:
            return False
        else:
            return True

if __name__ == "__main__":

    PARSER = argparse.ArgumentParser()

    PARSER.add_argument('--config_file', '-c', help="path to configuration file",
                        type=str)

    ARGS = vars(PARSER.parse_args())

    ARGDICT = dict()

    for arg in ARGS:
        if ARGS[arg] is not None:
            ARGDICT[arg] = ARGS[arg]

    station_check(**ARGDICT)
