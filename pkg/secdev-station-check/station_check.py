from packaging import version #setuptools
import yaml
import subprocess
import platform
from os import system

REQ_FILE = "pkg/config/requirements.yaml"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    VIOLET = '\033[35m'

class station_check:
    '''Checks, updates, and otherwise sets up a SecDev workstation to meet our requirements'''

    def __init__(self, config_file, verbose=False, test=False):
        '''Reads in requirements YAML file, checks versions, and installs
        out-of-date or missing packages.'''

        config = self.load_yaml(config_file)

        print("\n%s%s Workstation Setup%s\n" % (bcolors.WARNING, config["version"], bcolors.ENDC))

        successes = 0
        failures = 0
        installs = 0

        for installer in config["installers"]:
            print("%s%s %s%s%s check: %s" % (bcolors.OKBLUE,
                                         config["installers"][installer]["display"],
                                         bcolors.VIOLET,
                                         config["requirements"][installer],
                                         bcolors.OKBLUE,
                                         bcolors.ENDC), end='')

            v_check = self.version_check(installer,
                                         config["installers"][installer]["version_extraction"],
                                         config["requirements"][installer])

            if v_check:
                successes += 1
            elif not v_check and not v_check == "invalid":
                stdout, err = self.install_installer(config["installers"][installer]["setup"])
                if err == 0:
                    successes += 1
                    installs += 1
                    print("%sInstall successful!%s" % (bcolors.OKGREEN, bcolors.ENDC))
                else:
                    failures += 1
                    print("%sInstallation failed.%s" % (bcolors.FAIL, bcolors.ENDC))

            if v_check is not "invalid":
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

                    print("%sInstalling newer version of %s...%s" % (bcolors.WARNING,
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

                print("--------------------")

        self.print_results(successes, failures, installs)


    def print_results(self, successes, failures, installs):
        '''Prints outcome of workstation check'''
        total = successes + failures
        print("%sPackages installed: %s%s%s" % (bcolors.OKGREEN,
                                          bcolors.VIOLET,
                                          str(installs),
                                          bcolors.ENDC))
        if failures is not 0:
            print("%sInstallations failed: %s%s" % (bcolors.WARNING,
                                                   str(failures),
                                                   bcolors.ENDC))
            print("%sFAIL: %s packages out of %s meet requirements.%s" % (bcolors.FAIL,
                                                                          str(successes),
                                                                          str(total),
                                                                          bcolors.ENDC))
        else:
            print("%sPASS: %s packages out of %s meet requirements!%s" % (bcolors.OKGREEN,
                                                                          str(successes),
                                                                          str(total),
                                                                          bcolors.ENDC))

    def bash(self, command):
        '''Evaluates a string as a bash command.'''
        run = subprocess.run(command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            executable='/bin/bash')

        if run.returncode is not 0:

            print ("%sExit code: %s%s" % (bcolors.FAIL,
                                          str(run.returncode),
                                          bcolors.ENDC))

            print ("%sFailed to run: %s%s" % (bcolors.FAIL,
                                              command,
                                              bcolors.ENDC))

        # print(run.stderr)

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
            print ("%sExtracted version number (%s) appears to be an invalid format. \
                    Consider updating your version extraction command.%s" % (bcolors.FAIL,
                                                                             str(extracted),
                                                                             bcolors.ENDC))
            return "invalid"



        if more_recent:
            print ("%sFound %s!%s" % (bcolors.OKGREEN,
                                              extracted,
                                              bcolors.ENDC))
        else:
            print ("%sFound %s!%s" % (bcolors.WARNING,
                                              extracted,
                                              bcolors.ENDC))

        return more_recent

    def install_package(self, install_name, install_script):
        '''Installs a package'''

        return self.bash(install_script + " " + install_name)

    def install_installer(self, setup):
        '''Installs an installer and its list of setup instructions'''

        setup_script = ""

        os = platform.system()

        if os == "Darwin":
            setup_script = setup["mac"]
        elif os == "Linux":
            setup_script = setup["linux"]
        elif os == "Windows":
            print ("%sWindows is currently not supported%s" % (bcolors.FAIL, bcolors.ENDC))
            return False
        else:
            print ("%sOS not recognized.%s" % (bcolors.FAIL, bcolors.ENDC))
            return False

        return self.bash(setup_script)

    def install_configs(self, config_list):
        for configuration in config_list:
            stdout, err = self.bash(configuration)
            if err is not 0:
                print ("%sFailed to run: %s%s" % (bcolors.FAIL,
                                                  bcolors.ENDC,
                                                  configuration))
                return False
            print ("%sSuccessfully ran: %s%s" % (bcolors.OKGREEN,
                                                 bcolors.ENDC,
                                                 configuration))
        return True

s = station_check(REQ_FILE)


