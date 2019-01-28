# packet_pushers_vdc

# Introduction

Hello! This repository was created to accompany my Packet Pushers Virtual Design Clinic 3 presentation on "CI/CD for Networking". The intent of this repo is to allow you to simply "vagrant up" the environment used for the demo, so you can get into using Ansible, NAPALM-Ansible, some Python, and Jenkins right away.

You can check out the recording of this by being a member of Ignition at Packet Pushers, or you can check out this follow up video I posted on YouTube to see what its all about: [Click Me!](https://www.youtube.com/watch?v=_O6UTUTh9so&t=1s)

In this repository you will find a Vagrantfile which describes the multi-machine vagrant environment used for the demo. This includes a Cisco Nexus 9000v instance, an Arista vEOS instance, and an Ubuntu Server instance running Jenkins.

Each of these instances has some "base" configuration in order to get things bootstrapped nice and quickly for us.

The network devices have an "admin" user, as well as a "vagrant" user already configured (vagrant user is password-less access via SSH key, see table below for access information).

The Ubuntu host has Jenkins, Docker (and a container pre-built), some Python libraries, and Ansible pre-installed. Jenkins initial configuration/plugin setup has been completed.

Following the simple steps below should allow you to re-create the demo environment quickly and easily. Note that the Nexus device is running on the bare minimum amount of memory required and sometimes gets hung (allegedly it "requires" 8GB however I have allocated only 6GB). For what its worth, I'm running this successfully on a newish MacBook Pro with 16GB of memory.

# Install VirtualBox

Download and install VirtualBox for your operating system of choice:
https://www.virtualbox.org

# Setup Vagrant

## Install Vagrant

Download and install Vagrant for your operating system of choice:
https://www.vagrantup.com/downloads.html

## Install VirtualBox Plugin

Install the Vagrant Plugin for VirtualBox:

```
vagrant plugin install virtualbox
```

## Get the Boxes

Download and "add" the Vagrant boxes for this demo. Unfortunately these boxes are pretty big, if you prefer to :

```
vagrant box add carlniger/jenkins-base
vagrant box add carlniger/nxos-base
vagrant box add carlniger/eos-base
```

## Copy my Vagrant Keys

This is a bad idea from a security perspective, but its just a demo, so it should be okay :)

Copy the private key from the "vagrant_environment" folder to your vagrant directory. This should be "~/.vagrant.d".

If you cloned this repository to your local system you can do this as follows:

```
cp vagrant_envrionment/carl_packet_pushers_insecure_private_key ~/.vagrant.d/
```

## Vagrant Up!

At this point you should be ready to "vagrant up" your environment!

From the directory where your Vagrantfile lives (vagrant_environment) if you cloned the repo you can simply run:

```
vagrant up
```

Or if you prefer to launch an individual instance:

```
vagrant up [name|id]
```

You can suspend or destroy the environment or an individual instance in the same fashion:

```
vagrant destroy [name|id]
vagrant suspend [name|id]
```

## Vagrant Connectivity Information

|Device    |SSH Port   |Addtl Port   |Addtl Port Type   |Username   |Password   |Other                |
|----------|-----------|-------------|------------------|-----------|-----------|---------------------|
|Jenkins   |2203       |8080         |Jenkins Web UI    |jenkins    |P@ssw0rd   |N/A                  |
|EOS       |2201       |2301         |EAPI              |vagrant    |N/A        |N/A                  |
|EOS       |2201       |2301         |EAPI              |admin      |P@ssw0rd   |N/A                  |
|NXOS      |2202       |2302         |NXAPI             |vagrant    |N/A        |Serial Port = 2002   |
|NXOS      |2202       |2302         |NXAPI             |admin      |P@ssw0rd   |Serial Port = 2002   |

## Internal (From Jenkins) Connectivity Information

|Device    |IP           |API Port     |Username   |Password   |
|----------|-------------|-------------|-----------|-----------|
|EOS       |10.0.1.101   |444          |admin      |P@ssw0rd   |
|NXOS      |10.0.1.102   |444          |admin      |P@ssw0rd   |

## Testing Connectivity

You can SSH to each device as follows:

```
vagrant ssh [name|id]
```

Where name is one of the following: "nxos", "veos", "jenkins". These are the hostname as described in the Vagrantfile.

If you would like to SSH using the admin users, see the table above. On a Mac/Linux system your SSH command should look something like the following to connect using the vagrant user for the vEOS box:

```
ssh -l vagrant -i ~/.vagrant.d/insecure_private_key -p 2201 localhost
```

Or, as follows for the admin host (using the password as defined in the table above):

```
ssh -l admin -p 2201 localhost
```

# Getting Started

Once you've successfully launched your demo environment and validated that your devices are up and reachable, you're ready to start running some builds.

Connect to the Jenkins host on localhost:8080.

The initial Jenkins setup and plugin installation has been done for you. Upon log in you should arrive at the home page where you can create a new job/build.

# Setup a Jenkins Build

Click on "create new jobs".

Enter a project name -- this can be whatever you want.

Click on "Pipeline", then click "OK".

The only thing we really need to fill out to get our job working is to "point" Jenkins to our github repository so it knows where to find the "Jenkinsfile" included in the repo.

Scroll down to the "Pipeline" section and select "Pipeline script from SCM" from the drop down menu. Select "Git" from the SCM drop down menu.

In the "Repository URL" field, enter this repository's URL, or your own URL if you forked this. If you are pointing to a private repository, you will need to enter appropriate credentials for access.

That's it! You've already got the build set up; because the Jenkinsfile is actually describing the steps Jenkins needs to take, we don't need to do anymore in Jenkins.

# Start a Build

Clicking "build now" will fire off a build. Because Jenkins is just doing whatever is in the Jenkinsfile, you need to take a look at that to see whats going on.

For this build, Jenkins will fire up a container (image pre-built in the Jenkins box), and execute shell scripts in that instance. The shell scripts are all very straightforward one-liners in this case -- run a Playbook, run a syntax-check on a Playbook, run a Python script, etc..

Click on "Console Output" on the left side of the screen to take a look at what's happening live. This has been tested a bajillion times, so it *should* just run. The overall work-flow is as follows:

1. Fire up the "my_networK_as_code" container
2. Clone the Github repository
3. Run syntax checks on all Playbooks in the repo
4. Run the basic Python script to validate user inputs (this is limited and pretty simple just for demo purposes)
5. "Render" the configurations for the devices from the Jinja2 templates
6. Backup the existing device configurations (Note: right now these get backed up into the workspace directory in Jenkins (which is mounted to the container), this gets destroyed at the end of the build so it will disappear, you can rsync these off to an S3 bucket or whatever you want in real life!)
7. Deploy the configurations -- this is using NAPALM-Ansible config REPLACE (not merge!)
8. Sleep for 30 seconds to allow the configs to chill out, then run the validate playbook. If its all good, continue, if we get a non-zero exit code, we rollback and mark the build as failed.
9. Clean up the workspace (delete everything so we don't leave any cruft sitting around)

# Caveats/Notes

I'll start by saying: RTFM! I've spent far far far too much time hacking at things when I could have read the manual!

In general the Nexus is *very* touchy... be smart, generate a checkpoint file with NAPALM and then modify that and test as you go to make sure the config replace still works as you would want it to. If you are ok with "merge" efforts the Nexus is much much less difficult.

Another strange thing with the Nexus -- the base box originally had only the "internal" management and the regular management (mgmt0) ports up and configured. NAPALM config replaces failed every single time. It seems that this is because upon bringing the interface up NX-OS would create a "mac address XXXXXXX" command on the interfaces which would fail the checkpoint/rollback stuff. To work around this I simply put "no shut" and "no switchport" onto the base box. This would almost certainly be a non-issue on real gear, but was highly annoying for the virtual stuff!!

I'm unsure why, but if the Nexus device doesn't come up before the other devices it seems to fail to get DHCP on the managment port, and thus Vagrant can't connect. This shouldn't matter much since Jenkins will poke the device via the internal networks, but it is annoying! **Update** I was having issues with this again and have updated to latest VirtualBox, Vagrant, and Vagrant VirtualBox plugin and it *seems* to have sorted this out... I'm holding my breath :) As another crappy alternative if you're still having issues (and it seems that I still am, but maybe less?) you can set an IP address, then set the IP back to DHCP on the mgmt0 interface once the device is booted. This seems to allow the Nexus to figure it's life out and actually accept the DHCP offer from VirtualBox. It may be possible to set the base box to use the 10.0.2.15/24 IP address as the mgmt0 IP, but I've not tested that.

# Issues/Questions

Please feel free to open an issue if you've got any issues/questions. I probably won't do much anything else with this, but will try to assist with anything that pops up for folks time permitting!
