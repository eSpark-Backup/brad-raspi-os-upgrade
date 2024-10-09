
import os
import subprocess
import time

def run_command(command):
    """Run a shell command and check for errors."""
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        exit(1)
    print(f"Command completed: {command}")

def check_and_install_apt_fast():
    """Check if apt-fast is installed, and install it if not."""
    print("Checking for apt-fast...")
    try:
        result = subprocess.run("apt-fast --version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("apt-fast is not installed. Installing apt-fast...")
            run_command("sudo DEBIAN_FRONTEND=noninteractive apt update -y")
            run_command("sudo DEBIAN_FRONTEND=noninteractive apt install -y software-properties-common")
            run_command("echo 'deb http://ppa.launchpad.net/apt-fast/stable/ubuntu bionic main' | sudo tee /etc/apt/sources.list.d/apt-fast.list")
            run_command("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 1E2824A7F22B44BD")
            run_command("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 1EE2FF37CA8DA16B")
            run_command("sudo DEBIAN_FRONTEND=noninteractive apt update -y")
            run_command("sudo DEBIAN_FRONTEND=noninteractive apt install apt-fast -y")
        else:
            print("apt-fast is already installed.")
    except Exception as e:
        print(f"Error checking apt-fast: {e}")
        exit(1)

def modify_sources_list(from_version, to_version):
    """Modify the sources list to upgrade from one version to another."""
    print(f"Modifying sources.list from {from_version} to {to_version}")
    run_command(f"sudo sed -i 's/{from_version}/{to_version}/g' /etc/apt/sources.list")
    run_command(f"sudo sed -i 's/{from_version}/{to_version}/g' /etc/apt/sources.list.d/raspi.list")

    if to_version == 'bullseye':
        run_command("sudo sed -i 's#/debian-security bullseye/updates# bullseye-security#g' /etc/apt/sources.list")
    
    elif to_version == 'bookworm':
        run_command("sudo sed -i 's#/debian-security bookworm/updates# bookworm-security#g' /etc/apt/sources.list")

def upgrade_system():
    """Run the system upgrade commands."""
    run_command("sudo DEBIAN_FRONTEND=noninteractive apt update -y")
    time.sleep(2)
    run_command("sudo DEBIAN_FRONTEND=noninteractive apt-fast upgrade -y")
    time.sleep(2)
    run_command("sudo dpkg --configure -a")
    time.sleep(2)
    run_command("sudo DEBIAN_FRONTEND=noninteractive apt update -y")
    time.sleep(2)
    run_command("sudo DEBIAN_FRONTEND=noninteractive apt-fast dist-upgrade -y")
    time.sleep(2)
    run_command("sudo apt autoremove -y")
    time.sleep(2)
    run_command("sudo apt clean")

def upgrade_system2():
    """Run the system upgrade commands."""
    run_command("sudo DEBIAN_FRONTEND=noninteractive apt update -y")
    time.sleep(2)
    run_command("sudo DEBIAN_FRONTEND=noninteractive apt-fast upgrade -y")
    time.sleep(2)
    run_command("sudo DEBIAN_FRONTEND=noninteractive apt remove libgcc-8-dev -y")
    time.sleep(2)
    run_command("sudo DEBIAN_FRONTEND=noninteractive apt-fast dist-upgrade -y")
    time.sleep(2)
    run_command("sudo apt autoremove -y")
    time.sleep(2)
    run_command("sudo apt clean")


def reboot_system():
    """Reboot the system."""
    print("Rebooting the system...")
    run_command("sudo reboot")

# def write_state(state):
#     """Write the current state to the state file."""
#     with open(STATE_FILE, "w") as f:
#         f.write(state)

# def read_state():
#     """Read the current state from the state file."""
#     if os.path.exists(STATE_FILE):
#         with open(STATE_FILE, "r") as f:
#             return f.read().strip()
#     return "buster"  # Default state is starting from Buster

def read_state():
    try:
        # Run the command to fetch VERSION_CODENAME from /etc/os-release
        result = subprocess.run(
            ["grep", "VERSION_CODENAME=", "/etc/os-release"],
            capture_output=True, text=True, check=True
        )
        # Extract the codename by splitting the output
        version_codename = result.stdout.split('=')[1].strip()

        # Save the codename in the State variable
        return version_codename
        
    except subprocess.CalledProcessError as e:
        print("Error while fetching version_codename:", e)
        return None
    
def main():
 
    check_and_install_apt_fast()
 
    state = read_state()
    print(f"Version_codename: {state}")

    if state == "buster":
        # Step 1: Upgrade from Buster to Bullseye
        print("Upgrading from Buster to Bullseye...")
        upgrade_system()
        modify_sources_list('buster', 'bullseye')
        upgrade_system2()
        print("Upgrade to Bullseye complete. Rebooting...")
        # write_state("bullseye_done")  # Mark this step as completed
        time.sleep(2)
        reboot_system()

    elif state == "bullseye":
        # Step 2: Upgrade from Bullseye to Bookworm
        print("Upgrading from Bullseye to Bookworm...")
        modify_sources_list('bullseye', 'bookworm')
        upgrade_system()
        print("Upgrade to Bookworm complete. Rebooting...")
        # write_state("bookworm_done")  # Mark this step as completed
        time.sleep(2)
        reboot_system()

    elif state == "bookworm":
        print("System is already upgraded to Bookworm. No further actions needed.")
    else:
        print("Unknown state. Exiting.")

if __name__ == "__main__":
    main()
