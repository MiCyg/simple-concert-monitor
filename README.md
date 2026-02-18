# Concert SPL Monitor

Python-based SPL monitoring tool for Raspberry Pi.

## Prerequisites

- Raspberry Pi OS
- Python 3.9+ recommended
- Update system packages:
```bash
sudo apt update && sudo apt upgrade
````

* Install PortAudio:

```bash
sudo apt install portaudio19-dev
```

## Microphone setup (I2S)

1. Edit configuration file:

```bash
sudo nano /boot/firmware/config.txt
```

2. Uncomment:

```ini
dtparam=i2s=on
```

3. Add:

```ini
dtoverlay=googlevoicehat-soundcard
```

4. Reboot:

```bash
sudo reboot
```

5. Audio device check
```bash
arecord -l
```

## Setup

Create and activate virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python concert_spl_monitor.py
```

## Autostart on Boot (systemd)

Create a systemd service so the application starts automatically after boot.

### 1. Create service file

```bash
sudo nano /etc/systemd/system/concert-spl-monitor.service
```

### 2. Add configuration

Adjust paths to match your project location.

```ini
[Unit]
Description=Concert SPL Monitor
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/concert-spl-monitor
ExecStart=/home/pi/concert-spl-monitor/.venv/bin/python /home/pi/concert-spl-monitor/concert_spl_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

If your username is different than `pi`, replace it accordingly.

### 3. Reload systemd

```bash
sudo systemctl daemon-reload
```

### 4. Enable autostart

```bash
sudo systemctl enable concert-spl-monitor.service
```

### 5. Start service manually (optional)

```bash
sudo systemctl start concert-spl-monitor.service
```

### 6. Check status

```bash
sudo systemctl status concert-spl-monitor.service
```

### 7. View logs

```bash
journalctl -u concert-spl-monitor.service -f
```


