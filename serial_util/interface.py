import threading
from .connect import PortManager

class SerialReader:

    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.thread = threading.Thread(target=self.read_from_port, args=(self.serial_port,))
        self.thread.daemon = True
        self.stop_flag = False  # define a flag
        self.thread.start()

    def read_from_port(self, serial_port):
        while not self.stop_flag:  # check flag
            if serial_port.in_waiting:
                line = serial_port.readline().decode('utf-8').strip()
                self.process_data(line)
        serial_port.close()  # close the port here

    def process_data(self, data):
        print(data) # Print, or you can modify this to do something else with incoming data.
        
    def get_data(self):
        """You can add additional methods to return data if needed. But do take care about threading issues."""
        pass


def serial_monitor_cli():
    port = PortManager.select_port()
    reader = SerialReader(port)

    print("\nSerial port monitor started. Press Ctrl+C to stop.\n")

    try:
        while True: pass
    except KeyboardInterrupt:
        print("\nSerial port monitor stopping...\n")
        reader.stop_flag = True  # set flag when KeyboardInterrupt is caught
        reader.thread.join()  # wait for the thread to finish
        print("\nSerial port monitor stopped.\n")