<a id="markdown-SecDev Check" name="SecDev Check"></a>
# SecDev Workstation Check - A simple workstation setup tool

<https://github.com/asecurityteam/secdev-check>

<a id="markdown-overview" name="overview"></a>
## Workstation Check

Workstation check (stationcheck) allows your team to automate workstation setup for new hires. All it takes is writing a configuration file, creating a branch for your team on the stationcheck github repository, and then directing users to follow the steps below.

#### Quick Start

Note: If you are a new hire, you will need access to our internal bitbucket. These instructions should be in your onboarding Trello board, or you can navigate directly to go/iwantbitbucket.

1. If you don't have Homebrew installed, go ahead and run:

```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

2. Next, you'll most likely need xcode tools installed, if you haven't needed to use them before.

```bash
xcode-select --install
```

3. Finally, to use pip and a few key python libraries, you'll need python 3.7 installed. Luckily, Homebrew bundles pip and python together.

```bash
brew install python3
```
Note if you don't have at least python 3.7 installed, you'll need to run:

```bash
brew upgrade python3
```

4. Finally, you need to install stationcheck from whichever branch your team uses. For the default workstation (SecDev's) you can run:

```bash
pip3 install --upgrade git+git://github.com/asecurityteam/stationcheck
```

5. Run stationcheck:

```bash
stationcheck
```

If you want to run stationcheck with your own personal config file (instead of
  the one in the repo), simply run:

```bash
stationcheck <Path to your config file>
```


## Configuration

###### requirements.yaml

```yaml
version: "Your Team's Name" # Changes the title line of stationcheck
requirements:
  python: "3.6" # Dictates a minimum requirement of python 3.6
  go: "1.12"
  vscode: "1.0"
packages: # More detailed information for each requirement
  default: # Default configurations for our packages
    installer: brew # For now, default only replaces the installer field
  python:
    display: Python # For terminal reporting
    command: python3 # The command used for both version extraction and
    # installation
    version_extraction: "--version | cut -d ' ' -f2 2>&1" # string manipulations
    # that extract the version number from the stdout out of python's version
    # command
  go:
    display: Golang
    command: go
    version_extraction: "version | cut -d ' ' -f3 | tr -d 'go'"
  vscode:
    display: VScode
    command: code # command for version extraction
    install_command: visual-studio-code # name used for installation, in this
    # case: "brew cask install visual-studio-code"
    installer: brew-cask # overrides default installer
    version_extraction: "--version cut -d ' ' -f1 | sed -n 1p"
installers: # More detailed information on package installers
  brew:
    command: brew install # the first half of the install command
    configurations: # These run before any requirement installations. Usually,
    # these will be configuring non-standard packages to be installed, but they
    # can be any commands you wish
      - "brew tap atlassian/micros ssh://git@stash.atlassian.com:7997/micros/micros-cli-homebrew-tap.git" # taps Atlassian's tap for micros-cli
  brew-cask:
    command: brew cask install
```

## Adding new Requirements

Let's say your team is using the requirements.yaml file from the configuration section and you want to add a requirement for your team's workstations to have at least Git 2.2.

1. First, you'll want to add git under the requirements section like so:

```yaml
requirements:
  python: "3.6" # Dictates a minimum requirement of python 3.6
  go: "1.12"
  vscode: "1.0"
  git: "2.2"
```

2. Then you'll add the following to the packages section, under a new block entitled "git":

command - This is the command that calls your package from the command line. It makes up the first half of your version check command, and if no install command is listed in the config, it will double as the installation name (as in, it would be the second half of "brew install <installation name>").

display - The name you want displayed in the terminal report. This is useful for packages that have convoluted or otherwise confusing command names.

install_command - In cases where the installation name is different from the terminal command for a package, this will be used. For instance, VScode is called by the code command in the terminal, but to install it via brew, you'd type "brew install visual-studio-code".

installer - Overrides the default installer. This can be useful if your pacakage either an entirely different package installer or a slightly different installation method (like brew install versus brew cask install).

version_extraction - This is the most difficult field to determine, as you'll need to use shell string manipulations to extract the version number (x.y.z) from the stdout out of running the version command. For instance, when you run "go version", you get something like

```sh
go version go1.12.7 darwin/amd64
```

Since we're interested only in the version number (without any characters, so that we can compare them), we need to figure out the string manipulations to extract it. In this case we use the command:

```sh
go version | cut -d ' ' -f3 | tr -d 'go'
```

"cut -d ' ' -f3" splits the version output into a list, split by the empty spaces between the words: [go, version, go1.12.7, darwin/amd64], and -f3 denotes that we should select the third field in that list, which leaves us with: go1.12.7. Then we pipe that output into "tr -d 'go'". This command trims off the 'go' string, leaving us with an easily comparable version number: 1.12.7

So, with that in mind, we make the following changes to requirements.yaml to add git:

```yaml
packages: # More detailed information for each requirement
  default: # Default configurations for our packages
    installer: brew # For now, default only replaces the installer field
  python:
    display: Python # For terminal reporting
    command: python3 # The command used for both version extraction and
    # installation
    version_extraction: "--version | cut -d ' ' -f2 2>&1" # string manipulations
    # that extract the version number from the stdout out of python's version
    # command
  go:
    display: Golang
    command: go
    version_extraction: "version | cut -d ' ' -f3 | tr -d 'go'"
  vscode:
    display: VScode
    command: code # command for version extraction
    install_command: visual-studio-code # name used for installation, in this
    # case: "brew cask install visual-studio-code"
    installer: brew-cask # overrides default installer
    version_extraction: "--version cut -d ' ' -f1 | sed -n 1p"
  git:
    display: Git
    command: git
    version_extraction: "--version | cut -d ' ' -f3"
```

Since we plan on using the default installer (brew) and since git uses the same name for its command and installation, we don't need to include the install_command and installer fields.

3. Add an installer (if needed)

While we can install git with brew, let's say we decided to switch to uses a linux system, and wanted to setup apt-get as an installer.

We would set it up like so:

```yaml
installers: # More detailed information on package installers
  brew:
    command: brew install # the first half of the install command
    configurations: # These run before any requirement installations. Usually,
    # these will be configuring non-standard packages to be installed, but they
    # can be any commands you wish
      - "brew tap atlassian/micros ssh://git@stash.atlassian.com:7997/micros/micros-cli-homebrew-tap.git" # taps Atlassian's tap for micros-cli
  apt-get:
    command: apt-get install # the first half of the installation command
    configurations:
      - apt-get update # this ensures that apt-get is up to date before any
      # installations begin
```



Setting up workstation check for your team
