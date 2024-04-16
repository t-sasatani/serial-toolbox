import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .interface_core import serial_interface
from .connect import PortManager

class Application(ctk.CTk):
    """
    A Example tkinter application for serial communication.

    Attributes
    ----------
    interface : serial_interface
        The interface to interact with the serial port.
    left_frame : CTkFrame
        The Left Frame of the application.
    right_frame : CTkFrame
        The Right Frame of the application.
    entry_text : CTkStringVar
        The String variable linked to the data entry.
    data_entry : CTkEntry
        The entry field for the command.
    send_button : CTkButton
        The button to send the command.
    data_text : CTkText
        The textbox to display sent and received messages. Incoming data from the serial interface and the sent commands will be displayed in this field.
    figure : Figure
        The Figure object for the plot in the right frame. This object is what actually contains the graphical representation of the data.
    plot : AxesSubplot
        The subplot in the figure. This is where the data from the serial interface gets plotted.
    canvas : FigureCanvasTkAgg
        The canvas on which the figure is drawn. This is a tkinter-compatible canvas that the Figure object draws onto.
    """

    def __init__(self, interface):
        """Initialize the Application."""
        super().__init__()
        self.interface = interface

        ctk.set_appearance_mode("Dark")

        self.left_frame = ctk.CTkFrame(self)
        self.right_frame = ctk.CTkFrame(self)

        self.left_frame.grid(row=0, column=0, sticky='ns')
        self.right_frame.grid(row=0, column=1, sticky='nsew')

        self.entry_text = ctk.StringVar()
        self.data_entry = ctk.CTkEntry(self.left_frame, textvariable=self.entry_text)
        self.data_entry.pack(side=ctk.TOP, fill=ctk.X)
        self.data_entry.bind('<Return>', lambda event: self.send_command())

        self.send_button = ctk.CTkButton(self.left_frame, text="Send", command=self.send_command)
        self.send_button.pack(side=ctk.TOP, fill=ctk.X)

        self.data_text = ctk.CTkTextbox(self.left_frame, height=10, width=50)
        self.data_text.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(1, 1, 1)

        self.canvas = FigureCanvasTkAgg(self.figure, self.right_frame)
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.right_frame.rowconfigure(0, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        self.data_list = []

        self.update_plot()

    def send_command(self):
        """
        Fetch the command, send it via the serial interface and update the textbox.
        Clear the command entry field after sending the command.
        This function is connected to the 'Send' button and the 'Return' key while typing into the data_entry field.
        """
        command = self.entry_text.get()
        self.data_text.insert("end", "Sent: " + command + "\n")
        self.interface.write_to_port(command)
        self.entry_text.set("")

    def update_plot(self):
        """
        Update the plot with the data from the interface. 
        This function re-plots the data from the serial interface, then schedules itself to be called again after 100 ms.
        This function is automatically triggered in the initialization of the Application class, implementing a regular update of the plot.
        """
        queue_size = self.interface.data_queue.qsize()
        if queue_size > 0:
            self.plot.clear()
            self.data_list = []  # Clear data_list in every iteration of update_plot

            for _ in range(queue_size):
                data_dict = self.interface.data_queue.get()
                self.data_list.append(data_dict['data'])  # Store individual data-points
                
                # Once data is processed, requeue it for maintainance
                self.interface.data_queue.put(data_dict)
            
            # Outside of the loop, plot the entire data_list
            self.plot.plot(self.data_list)
            self.canvas.draw()

        self.after(100, self.update_plot)
        

def serial_monitor_gui():
    """
    Start and run the customtkinter application. 
    This is the main entry point of the application that creates an instance of the Application class and executes the main loop.
    """

    target_serial_interface = serial_interface(PortManager.select_port(), terminal=False, max_queue_size=200)
    app = Application(target_serial_interface)
    app.mainloop()
