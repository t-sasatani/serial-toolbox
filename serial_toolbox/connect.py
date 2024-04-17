import serial
from serial.tools import list_ports
import time
import logging

from .log_init import log_init

class port_manager:
    """
    A utility class for managing asynchronous communication over serial ports.
    """
    
    @classmethod
    def select_port(cls, interactive: bool=False, portname: str=None, baudrate: int=115200, timeout: float=0.1,
                    logger: logging.Logger=None) -> serial.Serial:
        """
        Class method for selecting the port for serial communication.
        
        Parameters
        ----------
        interactive : bool, optional
            User interactive mode switch, default is False
        portname : str, optional
            User identifier for port, default is None
        baudrate : int, optional
            The baudrate, default is 9600
        timeout : float, optional
            The timeout, default is 0.1
        logger : logging.Logger, optional
            The logger object, default is None

        Returns
        -------
        serial.Serial
            Initialized serial port.
        """
        if logger is None:
            logger = log_init()
        
        ser = serial.Serial()
        
        if portname:
            print("Setup port (" + portname + "). [] is default value.")
        else:
            print("Setup port. [] is default value.")

        if interactive:
            baudrate_input = input("baudrate [115200] >> ")
            if baudrate_input.strip():
                baudrate = int(baudrate_input)
            timeout_input = input("timeout [0.1] >> ")
            if timeout_input.strip():
                timeout = float(timeout_input)  # convert input to float
            print("======================")
                
        ser.baudrate = baudrate
        ser.timeout = timeout
        
        ports = list_ports.comports()
        devices = [info.device for info in ports]

        if len(devices) > 0:
            ser.port = cls._user_serial_select(devices=devices)
        else:
            print("device not found")
            return None

        cls._reset_serial(ser=ser, logger=logger)
        return cls._open_serial(ser=ser, logger=logger)

    @classmethod
    def _user_serial_select(cls, devices):
        """
        Class method for selecting a serial port from a user input.

        Parameters
        ----------
        devices : List[str]
            The list of all available serial ports.

        Returns
        -------
        str
            The selected serial port.
        """
        for i, device in enumerate(devices):
            print(f"index\t|  device")
            print("----------------------")
            print(f"{i:2d}\t|  {device}")

        
        while True:
            try:
                port_index = 0
                port_index_input = input("port index [0] >> ")
                if port_index_input.strip():
                    port_index = int(port_index_input)
                return devices[port_index]
            except (ValueError, IndexError):
                print('Invalid input. Please enter a number corresponding to a device.')
        
    @classmethod
    def _open_serial(cls, ser: serial.Serial, logger: logging.Logger) -> serial.Serial:
        """
        Class method for opening a serial port.

        Parameters
        ----------
        ser : Serial
            The serial object on which to open the port.
        logger : logging.Logger
            The logger object.

        Returns
        -------
        Serial
            The opened serial object if any, else None.
        """
        try:
            ser.open()
            logger.info('Port opened: %s' % ser.port)
            return ser
        except Exception as e:
            print(e)
            return None

    @classmethod
    def _reset_serial(cls, ser: serial.Serial, logger: logging.Logger):
        """
        Class method for resetting a serial port by closing it if it is already open.

        Parameters
        ----------
        ser : Serial
            The serial object to reset.
        logger : logging.Logger
            The logger object.
        """
        try:
            if ser.isOpen() == True:
                logger.info('Serial port was already open')
                ser.close()

                logger.info('Closing serial port')

                while ser.isOpen() == True:
                    logger.info('waiting for closing serial port')
                    time.sleep(1)
                logger.info('Finished closing serial port.')
            else:
                logger.info('Serial port is available')
        except Exception as e:
            logger.error(e)
            return None