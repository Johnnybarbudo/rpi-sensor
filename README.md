# Raiz Sensor Driver

The code in this repository runs in a Raspberry Pi, collects and aggregates data, then logs it to a cloud database.

### Install the package

For the imports to work properly

```
python3 -m pip install -e .
```

### Run locally

```
export GOOGLE_APPLICATION_CREDENTIALS="serviceaccount_pubsub.json"
python3 main.py
```
If you don't want to run the export command every time, you can add it to the bottom of `~/.bashrc`, so then it will be executed any time the Pi boots up.
To make it pick up the change right away (without rebooting), you can execute `source ~/.bashrc`. 
NOTE: if the bashrc file doesn't exist, you can just create it with `touch ~/.bashrc`.

## Using tmux

In case you want to run the remote RPI and disconnect from it after the intialization of the process, tmux should be used.

1. Connect to the RPI with the standard ssh procedure
2. If the RPI has no tmux installed, install it by using the command `sudo apt install tmux`
3. Start tmux by typing `tmux` into the shell
4. Start the process you want inside the started tmux session
5. Leave/detach the tmux session by typing `Ctrl+b` and then `d`. When you come back again and want to check the status of your process you can use `tmux attach` to attach to your tmux session.
6. You can now safely log off from the remote RPI by tying `exit`.

### Find Raspberry Pi on local network

1. `arp -a` to list all IPs on LAN
2. Find IPs where the first 3 blocks are the same, then run `sudo nmap -sP 192.168.43.0/24` (change the first 3 blocks as needed). This will show you which one is the RPi

### Connect to RPi

1. `ssh pi@192.168.43.201` (change IP to the one you found above, only works on local network) or alternatively `ssh pi@raspberrypi` (when the SSH username is still on default)
2. The Password for the connection can be found in the Raiz Notion Page under the subsection: Raspberry Remote Access

## Set up RPi from scratch for deployment

1. Execute the commands below(leave Filename and PW at SSH-Keygen empty, just press Enter):
   ```sh
   sudo apt update -y && \
   sudo apt full-upgrade -y && \
   sudo apt install git python3-pip autossh -y
   ```
2. Create an SSH key pair, then add public key to GitHub SSH keys and GCP Jumpbox Instance
   ```
   ssh-keygen
   cat ~/.ssh/id_rsa.pub
   ```
3. Clone repo and install dependencies:
   ```sh
   git clone git@github.com:raiz-lisbon/rpi-sensor.git && \
   cd rpi-sensor && \
   pip3 install -r requirements.txt && \
   touch serviceaccount_pubsub.json
   ```
4. Create a service account in GCP with 'Pub/Sub Publisher' role and add it to `serviceaccount_pubsub.json`
5. Update values in `/home/pi/rpi-sensor/device_config.yaml` as needed
6. `sudo raspi-config` Interface Options > Enable I2C Interface
7. Install gcloud:
   ```sh
   echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
   sudo apt-get install apt-transport-https ca-certificates gnupg -y && \
   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
   sudo apt-get update && sudo apt-get install google-cloud-sdk -y && \
   gcloud init
   ```
   On a Rpi Zero running on armv6 atchitecture, to avoid 'Illegal instruction' error caused by a GCP dependency (grpcio), reinstall grpcio from source:
   ```
   pip3 install --upgrade --no-binary :all: grpcio
   ```
   This might take a while. To avoid losing progress if the SSH session disconnects, install tmux (`apt install tmux`), start the install, then press CMD+B+D Now you can quit the SSH session. If you log back in, you can run `tmux attach` to connect to the previous session.
8. To make sure SSH keys are picked up, execute:
   ```sh
   eval `ssh-agent`
   ssh-add
   ```
9. Add Jumpbox public key to authorized_keys on RPi:
   On Jumpbox:
   ```sh
   cat ~/.ssh/id_rsa.pub
   ```
   Copy output, then paste below. On Raspberry Pi:
   ```sh
   nano ~/.ssh/authorized_keys
   ```
10. Add following line to crontab (open with `crontab -e`):
    ```sh
    @reboot source /home/pi/rpi-sensor/startup.sh
    ```
11. Connect to jumpbox:
    ```sh
    ssh simon@130.211.204.106
    ```
12. From Jumpbox, connect to RPi:
    ```sh
    ssh localhost -p 10001 -l pi
    ```

## Troubleshooting

1. If SSH authentication for cloning git repo fails (Step 3 in Set up of the RPI): The ssh-keygen will ask for a file to store the key and password. These inputs should be skipped by pressing Enter so the key will be stored in the default file which is called by the `cat` command afterwards.
2. If initialization of gcloud with the command `gcloud init` fails on the RPI (In step 7). The command can be replaced by `gcloud init --console-only`. In that case a link will occur in the console which should be copied in the browser of your computer. Give back the authentication key to the RPI.

### Create OS Image

1. Insert the set up MicroSD to the computer, then find its mount path:
   ```sh
   sudo diskutil list
   ```
2. Create a block-by-block image of the SD card using it's mount path. Specify an output file as well, for example:
   ```sh
   sudo dd if=/dev/disk2 of=rpi.img
   ```
   This might take a while.
3. Install pishrink, then compress the image:
   ```sh
   pishrink rpi.img rpi-sm.img
   ```
4. Now you can write the image to another MicroSD card using Balena Etcher
