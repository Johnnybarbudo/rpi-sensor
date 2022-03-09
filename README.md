# Raiz Sensor Driver
The code in this repository runs in a Raspberry Pi, collects and aggregates data, then logs it to a cloud database.

### Install the package

```
python3 -m pip install -e .
```

### Run locally

```
GOOGLE_APPLICATION_CREDENTIALS="serviceaccount_pubsub.json" python3 main.py
```

## Comissioning

### Find Raspberry Pi on local network

1. `arp -a` to list all IPs on LAN
2. Find IPs where the first 3 blocks are the same, then run `sudo nmap -sP 192.168.43.0/24` (change the first 3 blocks as needed). This will show you which one is the RPi

### Connect to RPi

`ssh pi@192.168.43.201` (change IP to the one you found above, only works on local network) or alternatively `ssh pi@raspberrypi` (when the SSH username is still on default) 

### Set up RPi from scratch

1. Execute the commands below:
   ```sh
   sudo apt update -y && \
   sudo apt full-upgrade -y && \
   sudo apt install git python3-pip autossh -y
   ssh-keygen
   cat ~/.ssh/id_rsa.pub
   ```
2. Add output of above command to GitHub SSH keys and GCP Jumpbox Instance
3. Execute the commands below:
   ```sh
   git clone git@github.com:raiz-lisbon/rpi-sensor.git && \
   cd rpi-sensor && \
   pip3 install -r requirements.txt && \
   touch serviceaccount_pubsub.json
   ```
4. Create a service account with 'Pub/Sub Publisher' role and add it to `serviceaccount_pubsub.json`
5. Update values in `/home/pi/rpi-sensor/device_config.yaml` as needed
6. `sudo raspi-config` Interface Options > Enable I2C Interface
7. Install gcloud
   ```sh
   echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list &&
   sudo apt-get install apt-transport-https ca-certificates gnupg -y &&
   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - &&
   sudo apt-get update && sudo apt-get install google-cloud-sdk -y &&
   gcloud init
   ```
8. To make sure SSH keys are picked up, execute
   ```sh
   eval `ssh-agent`
   ssh-add
   ```
9. Add following line to crontab (open with `crontab -e`)
   ```sh
   @reboot /home/pi/rpi-sensor/startup.sh
   ```
10. From Jumpbox, connect to RPi
    ```sh
    ssh localhost -p 10001 -l pi
    ```
