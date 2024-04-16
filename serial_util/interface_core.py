import threading
import queue
import time
from .connect import port_manager

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

    def __init__(self, serial_port, terminal: bool = True, max_queue_size: int = 100):
        """
        Parameters
        ----------
        serial_port : serial.Serial
            Instance of the serial port to read from.
        terminal : bool, optional
            If True, print incoming data to console. Defaults to True.
        max_queue_size : int, optional
            Maximum size for data_queue. Older data will be discarded when max is reached. Defaults to 100.
        """
        self.serial_port = serial_port
        self.thread = threading.Thread(target=self.read_from_port, args=(self.serial_port,))
        self.thread.daemon = True
        self.stop_flag = False
        self.data_queue = queue.Queue()
        self.terminal = terminal
        self.data_index = 0
        self.max_queue_size = max_queue_size
        self.thread.start()

    def read_from_port(self, serial_port):
        """
        Continuously reads data from the serial port until stop_flag is set to True.

        Parameters
        ----------
        serial_port : serial.Serial
            Instance of the serial port to read from.
        """
        while not self.stop_flag:
            if serial_port.in_waiting:
                line = serial_port.readline().decode('utf-8').strip()
                self.process_data(line)
        serial_port.close()

    def process_data(self, data):
        """
        Processes incoming data by adding the data to the data_queue.

        Parameters
        ----------
        data : str
            The data read from the serial port.
        """
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

    def write_to_port(self, data):
        """
        Writes data to the serial port.

        Parameters
        ----------
        data : str
            The data to write to the serial port.
        """
        self.serial_port.write((data+"\n").encode())

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
    port = port_manager.select_port(interactive)
    interface = serial_interface(port)

    print("\nSerial port monitor started. Press Ctrl+C to stop.\n")

    try:
        while True: 
            pass
    except KeyboardInterrupt:
        print("\nSerial port monitor stopping...\n")
        interface.stop_flag = True  
        interface.thread.join()
        print("\nSerial port monitor stopped.\n")
