# Raiz Sensor Driver

The code in this repository runs in a Raspberry Pi, collects and aggregates data, then logs it to a cloud database.

### Set up WiFi connection on the Pi
https://raspberrypi.stackexchange.com/questions/11631/how-to-setup-multiple-wifi-networks

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

1. Get a MicroSD card and format it
2. Download & Install [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
3. Open the imager, then in the settings (sprocket on bottom left):
    1. Set hostname to `raspberrypi`
    2. Enable SSH with public keys. You can add multiple keys separated by `\n`. Add your local key (get it by `cat ~/.ssh/id_rsa.pub`, or change the name of the key if you named it different), and add the pubkey of the jumphost:
        
        ```jsx
        ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDeoS0MVPlUPqrCvH2j0o346mU3Qz+myf4Pd9EDGBtTWIp6hDGRnlmOG5iSdBtp/dMq9HOrWuN9DASFeS1vqDX8HJGMBRdMGY1cBWCp+sHeAC8jucZWEZdk88iJOp2qO4DhdFs8D38xnC2JIHWprglGjwNVlzJPP0y9D+kMalumgMS/356Y+d+DTNW5G0rLqr68E4aZhwvNnUoB375L+zbx6R242JUShPFh/fc5hpVAmkfzwap8dpP7Xt4b1KT8E303+w1+pMUuzxyKCw+U4/W4FtdwzEtKXBqYHXKNq9lwxVVBPc0ZZmOrh0Mex96XNNB+wZPTmCHKkHzz7+LlTdmbj3bBRV7knJ8nRmpTb7TjefX34zPP8XGXgR4vN7Y++bFXpNlOF8rWOJXh1Ke8QQnMB7WU3Oajihmz5ZzTvYjQtMxIAUJAC14h668lc38qk7xNF3/RLbuicdM/4BPfSwzgPuNEA9irbt6cFubXozy6i2dKZx0saBEl8x7CHQIBQq0= simon@raiz-jumpbox
        ```
        
    3. Configure wireless LAN: add SSID and password
    4. Set locale settings
    5. Click WRITE
    6. Once ready, insert the SD card to the RPi and connect it to power
4. SSH into it with `ssh pi@raspberrypi.local` (this works because the hostname was configured before etching the SD card)

5. Execute the commands below(leave Filename and PW at SSH-Keygen empty, just press Enter):
   ```sh
   sudo apt update -y && \
   sudo apt full-upgrade -y && \
   sudo apt install git python3-pip autossh -y
   ```
6. Create an SSH key pair (keep everything on default, just keep pressing Enter)
   ```
   ssh-keygen
   cat ~/.ssh/id_rsa.pub
   ```
7. Add public key to 
    1. GitHub SSH keys: Settings > SSH and GPG keys > New SSH key
    2. GCP Jumpbox Instance: GCP Console > Compute Engine > Metadata > SSH Keys
8. Clone repo and install dependencies:
   ```sh
   git clone git@github.com:raiz-lisbon/rpi-sensor.git && \
   cd rpi-sensor && \
   pip3 install -r requirements.txt && \
   touch serviceaccount_pubsub.json
   ```
8. Find the `datalogger-pub@environment-data.iam.gserviceaccount.com` service account in GCP Console > IAM & Admin > Service Accounts (or create it if it doesn't exist with 'Pub/Sub Publisher' role)
    1. Click on it, go to the 'KEYS' tab
    2. Add Key > Create New Key > JSON
    3. Open the downloaded JSON file and copy its contents
    4. On the Pi, run `nano serviceaccount_pubsub.json`, paste the contents there and save the file.
`serviceaccount_pubsub.json`
9. Update values in `/home/pi/rpi-sensor/device_config.yaml` as needed
10. `sudo raspi-config` Interface Options > Enable I2C Interface
11. Install gcloud:
    NOTE: for default zone, use `eu-west-1a`
    ```sh
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    sudo apt-get install apt-transport-https ca-certificates gnupg -y && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    sudo apt-get update && sudo apt-get install google-cloud-sdk -y && \
    gcloud init
    ```
    NOTE: if you get an error (`unrecognized arguments: --remote-bootstrap`) when executing the auth command on your laptop, upgrade your gcloud with `gcloud components update`
    On a Rpi Zero running on armv6 atchitecture, to avoid 'Illegal instruction' error caused by a GCP dependency (grpcio), reinstall grpcio from source:
    ```
    pip3 install --upgrade --no-binary :all: grpcio
    ```
    This might take a while. To avoid losing progress if the SSH session disconnects, install tmux (`apt install tmux`), start the install, then press CMD+B+D Now you can quit the SSH session. If you log back in, you can run `tmux attach` to connect to the previous session.
12. To make sure SSH keys are picked up, execute:
    ```sh
    eval `ssh-agent`
    ssh-add
    ```
13. Add Jumpbox public key to authorized_keys on RPi:

    On Jumpbox:
    ```sh
    cat ~/.ssh/id_rsa.pub
    ```
    Copy output, then paste below. On Raspberry Pi:
    ```sh
    nano ~/.ssh/authorized_keys
    ```
14. Add following line to crontab (open with `crontab -e`):
    ```sh
    @reboot source /home/pi/rpi-sensor/startup.sh
    ```
15. Connect to jumpbox:
    ```sh
    ssh simon@130.211.204.106
    ```
16. From Jumpbox, connect to RPi:
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
