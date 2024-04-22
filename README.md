Utility functions for pySerial. This project is still at very early development stages and not guaranteed to work.
- [Docs](https://serial-toolbox.readthedocs.io)
- [Github](https://github.com/t-sasatani/serial-toolbox)
- [PyPI](https://pypi.org/project/serial_toolbox/)

# Install
## PyPI
```bash
pip install serial_toolbox
```

## Poetry (for development)
```bash
git clone <repo url>
cd <clone directory>
poetry shell
poetry install
```

# Scripts

## Serial port I/O inspired by Arduino IDE
### Serial monitor application
Interactively select serial port and monitor values
```bash
serial_monitor
```

### Serial plotter application
Interactively select serial port and plot values
```bash
serial_plotter
```
