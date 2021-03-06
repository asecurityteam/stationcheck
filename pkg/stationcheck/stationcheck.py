#!/usr/bin/env python3
'''A workstation check for up-to-date packages and languages'''

import subprocess
import argparse
import os
from packaging import version #setuptools
import yaml


PACKAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
REQ_FILE = os.path.join(PACKAGE_DIR, "pkg/config/requirements.yaml")

#pylint: disable=too-few-public-methods
class Bcolors:
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

class StationCheck:
    '''Checks, updates, and otherwise sets up a SecDev workstation to meet our requirements'''

    #pylint: disable=unused-argument, too-many-locals, too-many-branches
    def __init__(self, config_file=REQ_FILE, verbose=False, test=False):
        '''Reads in requirements YAML file, checks versions, and installs
        out-of-date or missing packages.'''

        # Loads in the requirements.yaml file into a dict
        config = self.load_yaml(config_file)

        print("\n%s%s Workstation Setup%s\n" % (Bcolors.WARNING, config["version"], Bcolors.ENDC))

        # Tracks number of installs and whether or not they are successful
        successes = 0
        failures = 0
        installs = 0

        # Installers
        # Runs a series of configuration commands prior to beginining any installations
        for installer in config["installers"]:
            if "configurations" in config["installers"][installer].keys():
                self.install_configs(config["installers"][installer]["configurations"])

        print("--------------------")

        # Authentication Checks
        # Checks that your machine appears to hold the right authentications
        for authblock in config["authentications"]:
            self.check_authentications(config["authentications"][authblock])
        print("--------------------")

        # Packages
        # Checks package versions, and installs missing or out-of-date ones.
        for package in config["packages"]:
            if package != "default":
                print("%s%s %s%s%s check: %s" % (Bcolors.OKBLUE,
                                                 config["packages"][package]["display"],
                                                 Bcolors.VIOLET,
                                                 config["requirements"][package],
                                                 Bcolors.OKBLUE,
                                                 Bcolors.ENDC), end='')
                # Calls version check to see if package is out-of-date
                v_check = self.version_check(config["packages"][package]["command"],
                                             config["packages"][package]["version_extraction"],
                                             config["requirements"][package])

                if v_check:
                    successes += 1
                elif not v_check:

                    print("%sInstalling newer version of %s...%s" %
                          (Bcolors.WARNING,
                           config["packages"][package]["display"],
                           Bcolors.ENDC))

                    # If package description in yaml has no defined installer, uses the default one
                    if "installer" not in config["packages"][package]:
                        installer = config["packages"]["default"]["installer"]
                    else:
                        installer = config["packages"][package]["installer"]

                    # If a package has a unique install command name, use that instead
                    if "install_command" in config["packages"][package].keys():
                        command = config["packages"][package]["install_command"]
                    else:
                        command = config["packages"][package]["command"]

                    stdout, err = self.install_package(command,
                                                       config["installers"][installer]["command"])

                    if err == 0:
                        successes += 1
                        installs += 1
                        print("%sSuccess!%s" % (Bcolors.OKGREEN, Bcolors.ENDC))
                    else:
                        failures += 1
                        print("%sInstallation failed.%s" % (Bcolors.FAIL, Bcolors.ENDC))
                        print(stdout)

                print("--------------------")

        self.print_results(successes, failures, installs)

    #pylint: disable=no-self-use
    def print_results(self, successes, failures, installs):
        '''Prints outcome of workstation check'''
        total = successes + failures
        print("%sPackages installed: %s%s%s" % (Bcolors.OKGREEN,
                                                Bcolors.VIOLET,
                                                str(installs),
                                                Bcolors.ENDC))
        if failures is not 0:
            print("%sInstallations failed: %s%s" % (Bcolors.WARNING,
                                                    str(failures),
                                                    Bcolors.ENDC))
            print("%sFAIL: %s packages out of %s meet requirements.%s" % (Bcolors.FAIL,
                                                                          str(successes),
                                                                          str(total),
                                                                          Bcolors.ENDC))
            return False
        else:
            print("%sPASS: %s packages out of %s meet requirements!%s" % (Bcolors.OKGREEN,
                                                                          str(successes),
                                                                          str(total),
                                                                          Bcolors.ENDC))
            return True

    def bash(self, command):
        '''Evaluates a string as a bash command.'''
        run = subprocess.run(command,
                             shell=True,
                             text=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             executable='/bin/bash')

        if run.returncode is not 0:

            print("%sExit code: %s%s" % (Bcolors.FAIL,
                                         str(run.returncode),
                                         Bcolors.ENDC))

            print("%sFailed to run: %s%s" % (Bcolors.FAIL,
                                             command,
                                             Bcolors.ENDC))

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
                    Consider updating your version extraction command.%s" % (Bcolors.FAIL,
                                                                             str(extracted),
                                                                             Bcolors.ENDC))
            return "invalid"



        if more_recent:
            print("%sFound %s!%s" % (Bcolors.OKGREEN,
                                     extracted,
                                     Bcolors.ENDC))
        else:
            print("%sFound %s!%s" % (Bcolors.WARNING,
                                     extracted,
                                     Bcolors.ENDC))

        return more_recent

    def install_package(self, install_name, install_script):
        '''Installs a package'''

        return self.bash(install_script + " " + install_name)

    def install_configs(self, config_list):
        '''Runs configuration commands listed under an installer in the config file'''
        failed_installs = 0
        for configuration in config_list:
            stdout, err = self.bash(configuration)
            if err is not 0:
                print("%sFailed to run: %s%s" % (Bcolors.FAIL,
                                                 Bcolors.ENDC,
                                                 configuration))
                failed_installs += 1
            print("%sInstaller configuration: %s%s" % (Bcolors.OKGREEN,
                                                       Bcolors.ENDC,
                                                       configuration))
        if failed_installs != 0:
            return False
        else:
            return True

    def check_authentications(self, auth_block):
        '''Runs a series of commands listed under a permissions requirements and determines if
        permissions exist'''
        failures = 0
        for check in auth_block["checks"]:
            stdout, err = self.bash(check)
            if err is not 0:
                print("%sFailed check:%s %s" % (Bcolors.FAIL, Bcolors.ENDC, check))
                print(stdout)
                failures += 1
        if failures == 0:
            print("%s%s%s: Authentication configuration exists! %s" % (Bcolors.OKBLUE,
                                                                       auth_block["display"],
                                                                       Bcolors.OKGREEN,
                                                                       Bcolors.ENDC))
        else:
            print("%s%s%s: Authentication configuration not present. %s" % (Bcolors.OKBLUE,
                                                                            auth_block["display"],
                                                                            Bcolors.FAIL,
                                                                            Bcolors.ENDC))


if __name__ == "__main__":

    PARSER = argparse.ArgumentParser()

    PARSER.add_argument('--config_file', '-c', help="path to configuration file",
                        type=str)

    ARGS = vars(PARSER.parse_args())

    ARGDICT = dict()

    for arg in ARGS:
        if ARGS[arg] is not None:
            ARGDICT[arg] = ARGS[arg]

    StationCheck(**ARGDICT)
