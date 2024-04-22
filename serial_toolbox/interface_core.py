import threading
import queue
import time
from .connect import port_manager

import logging
from .log_init import log_init

class serial_interface:
    """
    Class for continuously reading from a serial port in a separate thread.

    Attributes
    ----------
    serial_port : serial.Serial
        Instance of the serial port to read from.
    thread : threading.Thread
        Thread used to continuously read from the serial port.
    stop_flag : bool
        Flag used to stop the thread.
    data_queue : queue.Queue
        Thread-safe queue to store incoming data.
    terminal : bool
        If True, print incoming data to console.
    data_index : int
        A counter for received data.
    max_queue_size : int
        Maximum size for the data_queue.

    Methods
    -------
    read_from_port(serial_port)
        Continuously reads data from the serial port.
    process_data(data)
        Processes incoming data and add to the queue.
    write_to_port(data)
        Writes data to the serial port.
    """

    def __init__(self, serial_port, terminal: bool = True, max_queue_size: int = 100, format: str = 'STR', logger: logging.Logger=None):
        """
        Parameters
        ----------
        serial_port : serial.Serial
            Instance of the serial port to read from.
        terminal : bool, optional
            If True, print incoming data to console. Defaults to True.
        max_queue_size : int, optional
            Maximum size for data_queue. Older data will be discarded when max is reached. Defaults to 100.
        format : str, optional
            TBD
        """
        if logger is None:
            logger = log_init()

        self.serial_port = serial_port
        self.thread = threading.Thread(target=self.read_from_port)
        self.thread.daemon = True
        self.stop_flag = False
        self.data_queue = queue.Queue()
        self.terminal = terminal
        self.data_index = 0
        self.max_queue_size = max_queue_size
        self.format = format
        self.thread.start()

    def read_from_port(self):
        """
        Continuously reads data from the serial port until stop_flag is set to True.

        Parameters
        ----------
        serial_port : serial.Serial
            Instance of the serial port to read from.
        """
        try:
            while not self.stop_flag:
                if self.serial_port.in_waiting:
                    if self.format == 'STR':
                        line = self.serial_port.readline().decode('utf-8').strip()
                        self.process_data(line)
                    elif self.format == 'HEX':
                        raw_data = self.serial_port.readline()
                        self.process_data(raw_data)
        except Exception as e:
            logging.ERROR(e)
            return
        self.serial_port.close()

    def print_queue(self):
        for _ in range(self.data_queue.qsize()):
            serial_data = self.data_queue.get()

            if self.format == 'HEX':
                print(str(serial_data['index']) + ': ' + str(serial_data['data'].hex()))

            if self.format == 'STR':
                print(str(serial_data['index']) + ': ' + serial_data['data'])
        
            self.data_queue.put(serial_data)
            
    def process_data(self, data):
        """
        Processes incoming data by adding the data to the data_queue.

        Parameters
        ----------
        data : str
            The data read from the serial port.
        """

        logging.info('RECV: ' + str(data))

        data_dict = {
            'index': self.data_index, 
            'time': time.time(), 
            'data': data
        }

        if self.data_queue.qsize() >= self.max_queue_size:
            self.data_queue.get()

        self.data_queue.put(data_dict)
        self.data_index += 1

        if self.terminal:
            print(data)

    def write_to_port(self, data_str):
        """
        Writes data to the serial port.

        Parameters
        ----------
        data : str
            The data to write to the serial port.
        """
        if self.format == 'STR':
            self.serial_port.write((data_str+"\n").encode())
            return
        elif self.format == 'HEX':
            try:
                data_bin = bytes.fromhex(data_str)
                self.serial_port.write(data_bin)
            except ValueError:
                logging.WARNING('\'' + data_str + '\' includes non-hexadecimal number')

        logging.info('SENT: ' + data_str)

def serial_monitor_cli(interactive: bool = True):
    """
    Command-line interface for serial port monitor.
    
    Prompts the user to select a port, then starts the SerialReader on that port. 
    Reading operation can be stopped by a KeyboardInterrupt (Ctrl+C).
    
    The function creates and manages one thread for reading.
    
    The reading thread continuously reads data from the serial port and prints to the console
    until KeyboardInterrupt is caught.
    
    The thread is closed properly by setting its stop_flag to True and waiting for
    the thread to finish execution before returning from the function.    
    """

    logger = log_init()

    port = port_manager.select_port(interactive, portname="serial monitor", logger=logger)
    if not port:
        return
    
    format_input = input("format ('STR', 'HEX') ['STR'] >> ")
    if format_input.strip():
        format = format_input
    else:
        format = 'STR'
    
    interface = serial_interface(port, format, logger = logger)

    logger.info('\nSerial port monitor started. Press Ctrl+C to stop.\n')

    try:
        while True: 
            pass
    except KeyboardInterrupt:
        logger.info('\nSerial port monitor stopping...\n')
        interface.stop_flag = True  
        interface.thread.join()
        logger.info('\nSerial port monitor stopped.\n')
