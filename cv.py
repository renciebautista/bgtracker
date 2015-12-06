#test.py
try:
    import tkinter as tk  # for python 3
except:
    import Tkinter as tk  # for python 2
    import tkMessageBox as messagebox

import pygubu
import numpy as np
import argparse
import datetime
import imutils
import time
import cv2
from PIL import ImageTk, Image




class MyApplication(pygubu.TkApplication):  
    global cap
    global firstFrame
    global text_status
    global var
    text_status = "Stopped"

    cap = cv2.VideoCapture(0)
    

    

    def _create_ui(self):
        #1: Create a builder
        self.builder = builder = pygubu.Builder()   

        #2: Load an ui file
        builder.add_from_file('gui.ui')

        #3: Create the widget using self.master as parent
        self.mainwindow = builder.get_object('mainwindow', self.master)
        self.lmain = builder.get_object('lmain', self.master)
        self.btnMonitor = builder.get_object('btnMonitor', self.master)
        # Connect method callbacks
        builder.connect_callbacks(self)

        # self.show_frame()

        self.motion_detect()

        

    # define the method callbacks
    def toggle_monitor(self):
        
        if self.btnMonitor['text'] == 'Stop Monitoring':
            self.btnMonitor.config(text='Start Monitoring')
        else:
            self.btnMonitor.config(text='Stop Monitoring')

    def on_button1_clicked(self):
        active_stat.set(False)
        # messagebox.showinfo('Message', 'You clicked Button 1')
        # Camera 0 is the integrated web cam on my netbook
        camera_port = 0
         
        #Number of frames to throw away while the camera adjusts to light levels
        ramp_frames = 30
         
        # Now we can initialize the camera capture object with the cv2.VideoCapture class.
        # All it needs is the index to a camera port.
        # camera = cv2.VideoCapture(camera_port)
         
        # Captures a single image from the camera and returns it in PIL format
        def get_image():
         # read is the easiest way to get a full image out of a VideoCapture object.
         retval, im = cap.read()
         return im
         
        # Ramp the camera - these frames will be discarded and are only used to allow v4l2
        # to adjust light levels, if necessary
        for i in xrange(ramp_frames):
         temp = get_image()
        # print("Taking image...")
        # Take the actual image we want to keep
        camera_capture = get_image()
        file = "image.jpg"
        # A nice feature of the imwrite method is that it will automatically choose the
        # correct format based on the file extension you provide. Convenient!
        cv2.imwrite(file, camera_capture)
         
        # You'll want to release the camera, otherwise you won't be able to create a new
        # capture object until your script exits
        # del(camera)
        # self.show_frame()
        
        messagebox.showinfo('Message', 'Template saved.')
        active_stat.set(True)
        time.sleep(0.25)
        self.motion_detect()


    def on_button2_clicked(self):
        # messagebox.showinfo('Message', 'You clicked Button 2')
        # self.lmain.configure(text="hello, world!")
        self.show_frame()


    def on_button3_clicked(self):
        messagebox.showinfo('Message', 'You clicked Button 2')
        # active_stat.set(True)
        # self.motion_detect()

    # def show_frame(self):
    #     cv2image = cv2.imread('image.jpg',1)
    #     img = Image.fromarray(cv2image)
    #     imgtk = ImageTk.PhotoImage(image=img)
    #     self.lmain.imgtk = imgtk
    #     self.lmain.configure(image=imgtk)


    def show_frame(self):
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)

        # cv2.imshow('image',img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        if active_stat.get():
            print 'active'
        else:
            self.lmain.after(1, self.show_frame)

    def motion_detect(self):

        img = cv2.imread('image.jpg',1)

        frame1 = imutils.resize(img, width=500)
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
        firstFrame = gray1

        # grab the current frame and initialize the occupied/unoccupied
        # text
        _, frame = cap.read()
        text = "Unoccupied"
        if self.btnMonitor['text'] == 'Stop Monitoring':
            text_status = "Started"
        else:
            text_status = "Stopped"

        # # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # # compute the absolute difference between the current frame and
        # # first frame
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # # dilate the thresholded image to fill in holes, then find contours
        # # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        # # (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 500:
                continue
     
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"

        # draw the text and timestamp on the frame
        cv2.putText(frame, "Monitoring Status: {}".format(text_status), (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "Tester Status: {}".format(text), (10, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        img = Image.fromarray(frame)

        # cv2.imshow('image',img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)

        # print("Taking image...")
        if active_stat.get():
            self.lmain.after(1, self.motion_detect)

if __name__ == '__main__':
    root = tk.Tk()
    active_stat = tk.BooleanVar(root)
    active_stat.set(True)
    app = MyApplication(root)
    app.run()
    
