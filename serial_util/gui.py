import streamlit as st
import serial
import time
import threading
from queue import Queue

# initialize serial port
ser = serial.Serial('COM3', 9600)    # replace 'COM3' with your port name and 9600 with your baud rate
q = Queue()    # thread safe queue to hold the data

# define a function to continuously read from the serial port
def serial_thread(q):
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()    # read a '\n' terminated line
            data = int(line)    # convert the line to int, you should modify this line according to your data format
            q.put(data)    # put the data in queue

# start the serial thread
threading.Thread(target=serial_thread, args=(q,), daemon=True).start()

# define a function to draw the line chart
def line_chart():
    chart = st.line_chart()    # create an empty line chart
    data = []    # initialize an empty list to hold the data
    while True:
        if not q.empty():
            data.append(q.get())    # append the data from queue to the list
            chart.add_rows([data])    # update the line chart
        time.sleep(0.01)    # pause for a short period to reduce CPU usage

# start the Streamlit app
if __name__ == "__main__":
    line_chart()
