from packaging import version #setuptools
import yaml
import subprocess
import platform

REQ_FILE = "pkg/config/requirements.yaml"

class station_check:
    '''Checks, updates, and otherwise sets up a SecDev workstation to meet our requirements'''

    def __init__(self, config_file, verbose=False, test=False):
        '''Reads in requirements YAML file, checks versions, and installs
        out-of-date or missing packages.'''

        config = self.load_yaml(config_file)

        for installer in config["installers"]:
            print(installer + " " + config["requirements"][installer] + " check: ")
            v_check = self.version_check(installer,
                                config["installers"][installer]["version_extraction"],
                                config["requirements"][installer])

            if not v_check and not v_check == "invalid":
                stdout, err = self.install_installer(config["installers"][installer]["setup"],
                                    config["installers"][installer]["configurations"])
                if err == 0:
                    print("Success!\n")
                else:
                    print("Installation failed.\n")

        for package in config["packages"]:
            if package != "default":
                print(package + " " + config["requirements"][package] + " check: ")
                v_check = self.version_check(config["packages"][package]["command"],
                                    config["packages"][package]["version_extraction"],
                                    config["requirements"][package])

                if not v_check and not v_check == "invalid":

                    print("Installing newer version of " + package + "...")

                    if "installer" not in config["packages"][package]:
                        installer = config["packages"]["default"]["installer"]
                    else:
                        installer = config["packages"][package]["installer"]

                    stdout, err = self.install_package(config["packages"][package]["command"],
                                        config["installers"][installer]["command"])

                    if err == 0:
                        print("Success!\n")
                    else:
                        print("Installation failed.\n")


    def bash(self, command):
        '''Evaluates a string as a bash command.'''
        run = subprocess.run(command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            executable='/bin/bash')

        if run.returncode is not 0:
            print ("Exit code: " + str(run.returncode) + "\n")
            print ("Failed to run:\n" + command)

        # print(run.stdout)

        return run.stdout, run.returncode

    def load_yaml(self, yaml_file):
        '''Loads a yaml file as a dict.'''
        config_file = open(yaml_file, 'r')
        return yaml.safe_load(config_file)

    def version_check(self, command, extractor, version_req):
        '''Checks if the install version of a package meets requirement'''

        extracted_version, err = self.bash(command + " " + extractor)
        return self.version_compare(extracted_version, version_req)

    def version_compare(self, extracted, requirement):
        '''Compares two versions'''

        try:
            version.parse(extracted)
        except (version.InvalidVersion, TypeError):
            print (str(extracted) + " is an invalid version.")
            return "invalid"

        print ("Found version " + extracted)

        return version.parse(extracted) >= version.parse(requirement)

    def install_package(self, install_name, install_script):
        '''Installs a package'''

        return self.bash(install_script + " " + install_name)

    def install_installer(self, setup, config_list):
        '''Installs an installer and its list of setup instructions'''

        setup_script = ""

        os = platform.system()

        if os == "Darwin":
            setup_script = setup["mac"]
        elif os == "Linux":
            setup_script = setup["linux"]
        elif os == "Windows":
            print ("Windows is currently not supported")
            return False
        else:
            print ("OS not recognized.")
            return False

        return self.bash(setup_script)

s = station_check(REQ_FILE)


