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

## Serial I/O like Arduino IDE
### Serial plotter
Interactively select serial port and plot values
```bash
>serial_plotter
Setup port (serial monitor). [] is default value.
baudrate [9600] >> 9600
timeout [0.1] >> 0.1
======================
index  | device
0      | COM1
1      | COM2
device index [0] >> 0
format ('STR', 'HEX') ['STR'] >>  'HEX'
```

### Serial monitor
Interactively select serial port and monitor values
```bash
> serial_monitor
```
