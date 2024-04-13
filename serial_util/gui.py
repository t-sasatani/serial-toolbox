import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .interface_core import SerialReader
from .connect import PortManager

class Application(tk.Tk):
    """
    GUI Application for showing the serial port data in a plot in real time.

    Methods
    -------
    update_plot()
        Updates the plot every 0.1 seconds with the data_list from SerialReader instance.

    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the tkinter window and start the plot update.
        """
        tk.Tk.__init__(self, *args, **kwargs)

        # Assuming your SerialReader is working and continuously appending
        # read values to a list called "data_list"
        self.reader = SerialReader(PortManager.select_port(), terminal=False)
        
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.plot = self.figure.add_subplot(1, 1, 1)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.update_plot()

    def update_plot(self):
        """
        Updates the matplotlib plot with new data from data_list in SerialReader instance.
        This function is called every 0.1 seconds.

        """
        if len(self.reader.data_list) > 0:
            self.plot.clear()
            self.plot.plot(self.reader.data_list)
            self.canvas.draw()
            
        self.after(100, self.update_plot)  # Repeats every 0.1 seconds

def serial_monitor_gui():
    """
    Start the tkinter GUI application and the main event loop.
    """
    app = Application()
    app.mainloop()