### Install the package
```
python3 -m pip install -e .
```

### Run locally
```
GOOGLE_APPLICATION_CREDENTIALS="serviceaccount_pubsub.json" python3 main.py
```

### Comissioning
1. Raspberry OS
2. WiFi config
3. Enable SSH, set private key, disable password auth
4. autossh to jumpbox
5. Clone RPi-Sensor repo
6. Set GCP credentials
7. Set device config