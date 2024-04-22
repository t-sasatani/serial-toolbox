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

# Usage
## Example usage as a python module 
```python
from serial_toolbox.interface_core import serial_interface
from serial_toolbox.connect import port_manager
import time

tx_port = port_manager.select_port(interactive=False, portname="TX port", baudrate=9600, timeout=0.1)
tx_interface = serial_interface(tx_port, terminal=False, max_queue_size=200, format='HEX')

tx_interface.write_to_port('c0040105')
time.sleep(1)
tx_interface.print_queue()
```

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
