import serial
from serial.tools import list_ports
import time
import logging

from .log_init import log_init

class port_manager:
    """
    A utility class for serial communication.
    """ 
    @classmethod
    def select_port(cls,
                    baudrate: int = 9600,
                    timeout: float = 0.1,
                    logger: logging.Logger = None) -> serial.Serial:
        """
        Class method to select the port for serial communication.

        Parameters
        ----------
        baudrate : int, optional
            The baudrate, by default 9600
        timeout : float, optional
            The timeout, by default 0.1
        logger : logging.Logger, optional
            The logger object, by default None

        Returns
        -------
        serial.Serial
            Initialized serial port.

        """
        if logger is None:
            logger = log_init()
        
        ser = serial.Serial()
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
        Class method to ask user to select a serial device from the list.

        Parameters
        ----------
        devices : List[str]
            The list of all available serial port device names.

        Returns
        -------
        str
            The device name of the user-selected device.
        """
        for i, device in enumerate(devices):
            print(f"input {i:2d}: {device}")
        
        while True:
            try:
                print("input number of target port >> ", end="")
                num = int(input())
                print(f"Detected input: {num:2d}")
                return devices[num]
            except (ValueError, IndexError):
                print('Invalid input. Please enter a number corresponding to a device.')
        
    @classmethod
    def _open_serial(cls,
                     ser: serial.Serial,
                     logger: logging.Logger
                     ) -> serial.Serial:
        """
        Class method to open serial port.

        Parameters
        ----------
        ser : Serial
            The serial object, which contains the port specifications to open.
        logger : logging.Logger
            The logger object.

        Returns
        -------
        Serial
            The serial object representing the opened serial port if successful, else None.

        Raises
        ------
        SerialException
            If there is an error opening the port.
        """
        try:
            ser.open()
            logger.info('Port opened: %s' % ser.port)
            return ser
        except Exception as e:
            print(e)
            return None

    @classmethod
    def _reset_serial(cls,
                      ser: serial.Serial,
                      logger: logging.Logger
                      ) -> None:
        """
        Class method to reset the serial port, closing it if it is open.

        Parameters
        ----------
        ser : Serial
            The serial object representing the port to reset.
        logger : logging.Logger
            The logger object.

        Raises
        ------
        SerialException
            If there is an error closing the port.
        """
        try:
            if(ser.isOpen() == True):
                logger.info('Serial port was already open')
                ser.close()

                logger.info('Closing serial port')

                while ser.isOpen() == True:
                    logger.info('waiting for closing serial port')
                    time.sleep(1)
                logger.info('finished closing serial')
            else:
                logger.info('Serial port is available')
        except Exception as e:
            logger.error(e)
            return None
