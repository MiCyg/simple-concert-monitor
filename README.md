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
