<a id="markdown-SecDev Check" name="SecDev Check"></a>
# SecDev Workstation Check - A simple workstation setup tool

<https://github.com/asecurityteam/secdev-check>

<a id="markdown-overview" name="overview"></a>
## Workstation Check

Workstation check (stationcheck) allows your team to automate workstation setup for new hires. All it takes is writing a configuration file, creating a branch for your team on the stationcheck github repository, and then directing users to follow the steps below.

#### Quick Start

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
pip3 install --upgrade git+git://github.com/aslape/stationcheck
```

#### Configuration