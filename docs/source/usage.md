# Usage

## Command line interface (CLI)
See [Command Line interface](cli.rst)

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