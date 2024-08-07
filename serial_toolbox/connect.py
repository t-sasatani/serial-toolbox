import threading
import time
import logging
import serial
from serial.tools import list_ports

from .log_init import log_init

class port_manager:
    """
    A utility class for managing asynchronous communication over serial ports.
    """
    
    @classmethod
    def select_port(cls, interactive: bool = False, portname: str = None, baudrate: int = 9600, timeout: float = 0.1,
                    logger: logging.Logger = None) -> serial.Serial:
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
            logger.info("Setup port (%s). [] is default value.", portname)
        else:
            logger.info("Setup port. [] is default value.")

        if interactive:
            baudrate_input = input(f"baudrate [{baudrate}] >> ")
            if baudrate_input.strip():
                baudrate = int(baudrate_input)
            timeout_input = input(f"timeout [{timeout}] >> ")
            if timeout_input.strip():
                timeout = float(timeout_input)  # convert input to float
            logger.info("======================")
                
        ser.baudrate = baudrate
        ser.timeout = timeout
        
        ports = list_ports.comports()
        devices = [info.device for info in ports]

        if len(devices) > 0:
            ser.port = cls._user_serial_select(devices, logger)
        else:
            logger.error("Device not found")
            return None

        cls._reset_serial(ser, logger)
        return cls._open_serial(ser, logger)

    @classmethod
    def _user_serial_select(cls, devices, logger):
        """
        Class method for selecting a serial port from a user input.

        Parameters
        ----------
        devices : list[str]
            The list of all available serial ports.
        logger : logging.Logger
            The logger object.

        Returns
        -------
        str
            The selected serial port.
        """
        logger.info("index\t|  device")
        logger.info("----------------------")

        for i, device in enumerate(devices):
            logger.info("%2d\t|  %s", i, device)
        time.sleep(0.1)
        
        while True:
            try:
                port_index = 0
                port_index_input = input("port index [0] >> ")
                if port_index_input.strip():
                    port_index = int(port_index_input)
                return devices[port_index]
            except (ValueError, IndexError):
                logger.error('Invalid input. Please enter a number corresponding to a device.')
        
    @classmethod
    def _open_serial(cls, ser: serial.Serial, logger: logging.Logger) -> serial.Serial:
        """
        Class method for opening a serial port.

        Parameters
        ----------
        ser : serial.Serial
            The serial object on which to open the port.
        logger : logging.Logger
            The logger object.

        Returns
        -------
        serial.Serial
            The opened serial object if any, else None.
        """
        try:
            ser.open()
            logger.info('Port opened: %s', ser.port)
            return ser
        except Exception as e:
            logger.error("Error opening port: %s", e)
            return None

    @classmethod
    def _reset_serial(cls, ser: serial.Serial, logger: logging.Logger):
        """
        Class method for resetting a serial port by closing it if it is already open.

        Parameters
        ----------
        ser : serial.Serial
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