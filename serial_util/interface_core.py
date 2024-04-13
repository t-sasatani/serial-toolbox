import threading
from .connect import PortManager

class SerialInterface:
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

    Methods
    -------
    read_from_port(serial_port)
        Continuously reads data from the serial port.
    process_data(data)
        Processes incoming data (default is print to console).
    """

    def __init__(self, serial_port, terminal: bool = True):
        """
        Parameters
        ----------
        serial_port : serial.Serial
            Instance of the serial port to read from.
        """
        self.serial_port = serial_port
        self.thread = threading.Thread(target=self.read_from_port, args=(self.serial_port,))
        self.thread.daemon = True
        self.stop_flag = False  # define a flag
        self.data_list = []  # Add this line to create the data_list attribute
        self.terminal = terminal
        self.thread.start()

    def read_from_port(self, serial_port):
        """
        Continuously reads data from the serial port until stop_flag is set to True.

        Parameters
        ----------
        serial_port : serial.Serial
            Instance of the serial port to read from.
        """
        while not self.stop_flag:  # check flag
            if serial_port.in_waiting:
                line = serial_port.readline().decode('utf-8').strip()
                self.process_data(line)
        serial_port.close()  # close the port here

    def process_data(self, data):
        """
        Processes incoming data. Default is print to console.

        Parameters
        ----------
        data : str
            The data read from the serial port.
        """
        self.data_list.append(float(data))
        if self.terminal == True:
            print(data)

    def write_to_port(self, data):
        """
        Continuously writes data to the serial port until stop_flag is set to True.

        Parameters
        ----------
        serial_port : serial.Serial
            Instance of the serial port to write to.
        data : str
            The data to write to the serial port.
        """
        self.serial_port.write(data.encode())

def serial_monitor_cli():
    """
    Command line interface for serial port monitor.
    
    Prompts the user to select a port, then starts the SerialReader and SerialWriter
    on that port. Reading and writing operations can be stopped by a KeyboardInterrupt (Ctrl+C).
    
    The function creates and manages two threads, one for reading and one for writing.
    
    The reading thread continuously reads data from the serial port and prints to the console
    until KeyboardInterrupt is caught.
    
    The writing thread continuously writes a string "Hello" to the serial port until
    KeyboardInterrupt is caught.
    
    Both threads are closed properly by setting their stop_flag to True and waiting for
    the threads to finish execution before returning from the function.    
    """    
    port = PortManager.select_port()
    interface = SerialInterface(port)

    print("\nSerial port monitor started. Press Ctrl+C to stop.\n")

    try:
        while True: 
            pass
    except KeyboardInterrupt:
        print("\nSerial port monitor stopping...\n")
        interface.stop_flag = True  
        interface.thread.join()
        print("\nSerial port monitor stopped.\n")