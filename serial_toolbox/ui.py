import threading
import time
import queue
import cmd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import yaml
from pydantic import ValidationError  # Ensure this is imported
from .interface_core import serial_interface
from .connect import port_manager
from .log_init import log_init
from .models import Config  # Import the pydantic model

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

class SerialMonitor(cmd.Cmd):
    """
    A command-line serial monitor equipped with plotting functionality.
    
    Attributes
    ----------
    interface : serial_interface
        The serial interface for communication.
    plotting : bool
        Flag to enable or disable plotting.
    print_numbers : bool
        Flag to control numeric data printing.
    data_lock : threading.Lock
        Lock to manage access to shared data.
    traces : list
        List of data traces for plotting.
    plot_queue : queue.Queue
        Queue for handling plot data.
    print_queue : queue.Queue
        Queue for handling print data.
    window_size : int
        Size of the data window for the plot.
    session : PromptSession
        Interactive session for the command prompt.
    animation : FuncAnimation, optional
        Animation instance for the plot.

    Methods
    -------
    on_close_plot(event)
        Handle the plot window being closed.
    rxd_update()
        Continuously update received data.
    is_comma_separated_numbers(data_str)
        Check if the given string is a comma-separated string of numbers.
    update_traces(values)
        Update the traces with new values.
    update_plot(frame)
        Update the plot with the received data.
    print_rxd()
        Print the received data without interrupting the CLI.
    do_send(arg)
        Send a command via the serial interface.
    do_exit(arg)
        Exit the serial monitor.
    cmdloop(intro=None)
        A replacement for the standard cmdloop with additional processing.
    preloop()
        Hook method executed once when the cmdloop method is called.
    postloop()
        Hook method executed once when the cmdloop method is about to return.
    """

    doc_header = 'Commands (type help <command> for details):'

    intro = 'Type help or ? to list commands.\n'
    prompt = '(sertools) '

    def __init__(self, interface, config: Config):
        """
        Initialize the SerialMonitor with the given interface and configuration.

        Parameters
        ----------
        interface : serial_interface
            The serial interface for communication.
        config : Config
            Configuration for the serial monitor.
        """
        super().__init__()
        self.running = True  # Initialize running before starting threads
        self.interface = interface
        self.plotting = config.plotting
        self.print_numbers = config.print_numbers  # Flag to control numeric data printing
        self.data_lock = threading.Lock()

        # Initialize plotting parameters
        self.traces = []
        self.plot_queue = queue.Queue()
        self.print_queue = queue.Queue()
        self.window_size = config.window_size

        # Initialize prompt_toolkit session
        self.session = PromptSession()

        # Plot initialization must be done in the main thread
        self.animation = None
        if self.plotting:
            self.figure, self.ax = plt.subplots()
            self.animation = FuncAnimation(self.figure, self.update_plot, interval=100, cache_frame_data=False)
            self.figure.canvas.mpl_connect('close_event', self.on_close_plot)

        # Start the RXD update thread
        self.update_thread = threading.Thread(target=self.rxd_update)
        self.update_thread.daemon = True
        self.update_thread.start()

        # Start the print update thread
        self.print_thread = threading.Thread(target=self.print_rxd)
        self.print_thread.daemon = True
        self.print_thread.start()

    def on_close_plot(self, event):
        """
        Handle the plot window being closed.

        Parameters
        ----------
        event : matplotlib.backend_bases.CloseEvent
            The close event for the plot window.
        """
        self.running = False
        if self.animation and self.animation.event_source:
            self.animation.event_source.stop()  # Stop the animation timer

    def rxd_update(self):
        """
        Continuously update received data.
        """
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
            time.sleep(0.01)

    def is_comma_separated_numbers(self, data_str):
        """
        Check if the given string is a comma-separated string of numbers.

        Parameters
        ----------
        data_str : str
            The string to check.

        Returns
        -------
        bool
            True if the string is a comma-separated string of numbers, False otherwise.
        """
        try:
            [float(x) for x in data_str.split(',')]
            return True
        except ValueError:
            return False

    def update_traces(self, values):
        """
        Update the traces with new values.

        Parameters
        ----------
        values : list of float
            The new values to add to the traces.
        """
        while len(self.traces) < len(values):
            self.traces.append([])
        
        for i, value in enumerate(values):
            self.traces[i].append(value)
        
        for trace in self.traces:
            if len(trace) > self.window_size:
                trace.pop(0)

    def update_plot(self, frame):
        """
        Update the plot with the received data.

        Parameters
        ----------
        frame : int
            The current frame number.
        """
        with self.data_lock:
            self.ax.clear()
            for trace in self.traces:
                self.ax.plot(trace)
            self.ax.relim()
            self.ax.autoscale_view()
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

    def print_rxd(self):
        """
        Print the received data without interrupting the CLI.
        """
        while self.running:
            try:
                message = self.print_queue.get_nowait()
                with patch_stdout():
                    print(message)
            except queue.Empty:
                pass
            time.sleep(0.1)

    def do_send(self, arg):
        """
        Send a command via the serial interface.

        Parameters
        ----------
        arg : str
            The command to send.

        Examples
        --------
        send TEST_COMMAND

        send 54657374 (for HEX)
        """
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

    def help_send(self):
        """
        Print detailed help for the send command.
        """
        print("\n".join([
            "send <command>",
            "Send a command via the serial interface.",
            "",
            "Examples:",
            "  send TEST_COMMAND",
            "  send 54657374 (for HEX)"
        ]))

    def do_exit(self, arg):
        """
        Exit the serial monitor.

        Parameters
        ----------
        arg : str
            Unused parameter.

        Examples
        --------
        exit
            Exit the serial monitor.
        """
        print('Exiting Serial Monitor.')
        self.running = False
        if self.animation and self.animation.event_source:
            self.animation.event_source.stop()  # Stop the animation timer
        return True

    def help_exit(self):
        """
        Print detailed help for the exit command.
        """
        print("Exit the serial monitor.")

    def cmdloop(self, intro=None):
        """
        A replacement for the standard cmdloop with additional processing.

        Parameters
        ----------
        intro : str, optional
            An introductory message to display at the start of the cmdloop.
        """
        self.preloop()  # Hook after initialization before looping
        if intro is not None:
            self.intro = intro
        if self.intro:
            self.stdout.write(str(self.intro) + "\n")

        while self.running:
            try:
                with patch_stdout():
                    line = self.session.prompt(self.prompt)
                if line.strip():
                    self.onecmd(line)
            except (KeyboardInterrupt, EOFError):
                print('Exiting Serial Monitor.')
                self.running = False
                if self.animation and self.animation.event_source:
                    self.animation.event_source.stop()  # Stop the animation timer
                break

        self.postloop()  # Hook before exiting
    
    def preloop(self):
        """
        Hook method executed once when the cmdloop method is called.
        """
        pass

    def postloop(self):
        """
        Hook method executed once when the cmdloop method is about to return.
        """
        self.running = False

def serial_monitor(config_file):
    """
    Start and run the CLI application with configuration from a YAML file.

    Parameters
    ----------
    config_file : str
        Path to the configuration file.
    """
    # Load the configuration
    with open(config_file, 'r') as file:
        try:
            config_data = yaml.safe_load(file)
            config = Config(**config_data)
        except ValidationError as e:
            print(f"Configuration error: {e}")
            return

    logger = log_init()

    port_interface = port_manager.select_port(
        interactive=False,
        baudrate=config.baudrate,
        timeout=config.timeout,
        portname="sertools",
        logger=logger)

    if not port_interface:
        return

    target_serial_interface = serial_interface(
        port_interface,
        terminal=False,
        max_queue_size=10,
        format=config.format,
        logger=logger
    )
    serial_monitor_instance = SerialMonitor(target_serial_interface, config)
    
    # Start the command loop in its own thread
    cmd_thread = threading.Thread(target=serial_monitor_instance.cmdloop)
    cmd_thread.start()
    
    # Start the main loop to keep plot active
    while serial_monitor_instance.running:
        if serial_monitor_instance.plotting:
            try:
                plt.pause(0.1)
            except Exception as e:
                print(f"Plotting error: {e}")
        time.sleep(0.1)

    # Ensure the command loop thread exits cleanly
    cmd_thread.join()