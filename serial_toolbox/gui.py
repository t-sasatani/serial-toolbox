import threading
import time
import queue
import cmd
import readline  # or for Windows: from pyreadline import Readline
import logging
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from .interface_core import serial_interface
from .connect import port_manager
from .log_init import log_init

class SerialMonitor(cmd.Cmd):
    intro = 'Welcome to the Serial Monitor. Type help or ? to list commands.\n'
    prompt = '(serial monitor) '

    def __init__(self, interface, plotting=True, print_numbers=False):
        super().__init__()
        self.interface = interface
        self.plotting = plotting
        self.print_numbers = print_numbers  # Flag to control numeric data printing
        self.data_lock = threading.Lock()

        # Initialize plotting parameters
        self.traces = []
        self.plot_queue = queue.Queue()
        self.print_queue = queue.Queue()
        self.window_size = 200

        if self.plotting:
            self.figure, self.ax = plt.subplots()
            self.animation = FuncAnimation(self.figure, self.update_plot, interval=100)
            plt.ion()  # Turn on interactive mode
            self.figure.show()

        # Start the RXD update thread
        self.running = True
        self.update_thread = threading.Thread(target=self.rxd_update)
        self.update_thread.daemon = True
        self.update_thread.start()

        # Start the print update thread
        self.print_thread = threading.Thread(target=self.print_rxd)
        self.print_thread.daemon = True
        self.print_thread.start()

    def rxd_update(self):
        """ Continuously update received data. """
        while self.running:
            data_queue_size = self.interface.data_queue.qsize()
            if data_queue_size > 0:
                for _ in range(data_queue_size):
                    data_dict = self.interface.data_queue.get()

                    if self.interface.format == 'HEX':
                        self.print_queue.put("RXD: 0x" + data_dict['data'].hex())
                    elif self.interface.format == 'STR':
                        data_dict['data'] = data_dict['data'].strip()
                        if self.is_comma_separated_numbers(data_dict['data']):
                            values = [float(x) for x in data_dict['data'].split(',')]
                            with self.data_lock:
                                self.update_traces(values)
                            if self.print_numbers:  # Check the flag before printing
                                self.print_queue.put("RXD: " + data_dict['data'])
                        else:
                            self.print_queue.put("RXD: " + data_dict['data'])
            time.sleep(0.1)

    def is_comma_separated_numbers(self, data_str):
        """ Check if the given string is a comma-separated string of numbers. """
        try:
            [float(x) for x in data_str.split(',')]
            return True
        except ValueError:
            return False

    def update_traces(self, values):
        """ Update the traces with new values. """
        while len(self.traces) < len(values):
            self.traces.append([])
        
        for i, value in enumerate(values):
            self.traces[i].append(value)
        
        for trace in self.traces:
            if len(trace) > self.window_size:
                trace.pop(0)

    def update_plot(self, frame):
        """ Update the plot with the received data """
        with self.data_lock:
            self.ax.clear()
            for trace in self.traces:
                self.ax.plot(trace)
            self.ax.relim()
            self.ax.autoscale_view()
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

    def print_rxd(self):
        """ Print the received data without interrupting the CLI. """
        while self.running:
            try:
                message = self.print_queue.get_nowait()
                # Save the current prompt line
                current_input = readline.get_line_buffer()
                saved_line_pos = readline.get_begidx()
                # Clear the prompt line
                sys.stdout.write('\r' + ' ' * (len(self.prompt) + len(current_input)) + '\r')
                sys.stdout.flush()
                # Print the new message
                print(message)
                # Restore the prompt line
                sys.stdout.write(self.prompt + current_input)
                sys.stdout.flush()
                readline.redisplay()
            except queue.Empty:
                pass
            time.sleep(0.1)

    def do_send(self, arg):
        "Send a command: send <command>"
        command = arg.strip()
        if self.interface.format == 'STR':        
            print("TXD: " + command)
        elif self.interface.format == 'HEX':
            try:
                _ = bytes.fromhex(command)
            except ValueError:
                print(f"'{command}' includes non-hexadecimal number")
                return
            print("TXD: 0x" + command)

        self.interface.write_to_port(command)

    def do_plot(self, arg):
        "Show the plot window"
        if self.plotting:
            plt.show()

    def do_exit(self, arg):
        "Exit the serial monitor"
        print('Exiting Serial Monitor.')
        self.running = False
        return True

    def cmdloop(self, intro=None):
        """A replacement for the standard cmdloop with additional processing."""
        self.preloop()  # Hook after initialization before looping
        if intro is not None:
            self.intro = intro
        if self.intro:
            self.stdout.write(str(self.intro) + "\n")
        stop = None
        while self.running:
            if self.cmdqueue:
                line = self.cmdqueue.pop(0)
            else:
                line = input(self.prompt)
            try:
                stop = self.onecmd(line)
            except Exception as e:
                print('Exception:', e)
            if stop:
                break
        self.postloop()  # Hook before exiting
    
    def preloop(self):
        """Hook method executed once when the cmdloop() method is called."""
        pass

    def postloop(self):
        """Hook method executed once when the cmdloop() method is about to return."""
        self.running = False

def serial_monitor_cli():
    """
    Start and run the CLI application. 
    This is the main entry point of the application that creates an instance of the SerialMonitor class and runs the cmd loop.
    """
    logger = log_init()

    port_interface = port_manager.select_port(interactive=True, portname="serial monitor", logger=logger)
    format_input = input("format ('STR', 'HEX') ['STR'] >> ")
    format = format_input.strip() if format_input.strip() else 'STR'
    
    print_numbers_input = input("Print numeric data to CLI? (y/n) [n] >> ").strip().lower()
    print_numbers = True if print_numbers_input == 'y' else False

    if not port_interface:
        return
    
    target_serial_interface = serial_interface(port_interface, terminal=False, max_queue_size=10, format=format, logger=logger)
    SerialMonitor(target_serial_interface, plotting=(format == 'STR'), print_numbers=print_numbers).cmdloop()

if __name__ == "__main__":
    serial_monitor_cli()