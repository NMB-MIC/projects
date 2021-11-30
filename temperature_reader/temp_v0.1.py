#temp
import cv2
import numpy as np
import pandas as pd
from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import time
import threading
from evdev import InputDevice, categorize, ecodes
import evdev
import psycopg2
import paho.mqtt.client as paho

broker="localhost"
port=1883

#global viriable
temp = '.'
rfid = ''
msg = 'init'
c = 0
name = ''
status = ''

def selectEmpno(rfidcode):
    empno = rfidcode
    global name
    try:
        connection = psycopg2.connect(user="pi",
                                  password="123456",
                                  host="localhost",
                                  port="5432",
                                  database="temp")
        cursor = connection.cursor()
        postgreSQL_select_Query = "SELECT empno FROM public.authen where rfid ='"+rfidcode+"' limit 1;"

        cursor.execute(postgreSQL_select_Query)
        #print("Selecting rows from authors table using cursor.fetchall")
        authors_records = cursor.fetchall()
        #print(len(authors_records))
        #print("Print each row and it's columns values")
        if len(authors_records) != 0:
            empno = str(authors_records[0])[2:7]
            

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            #print("PostgreSQL connection is closed")
            name = empno
        return empno

def insertData(empno,temp,status):
    try:
        connection = psycopg2.connect(user="pi",
                                  password="123456",
                                  host="localhost",
                                  port="5432",
                                  database="temp")
        cursor = connection.cursor()
        postgreSQL_select_Query = "INSERT INTO public.temps(empno, temp,status) VALUES ( '"+empno+"', '"+temp+"','"+status+"');"

        cursor.execute(postgreSQL_select_Query)
        connection.commit()
        #authors_records = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print("Error while insert data from PostgreSQL", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            #print("PostgreSQL connection is closed")

def rfidRead():
  client1= paho.Client("control1")                                         
  client1.connect(broker,port)
  RFID_LOOKUP = {
	2: '1',
	3: '2',
	4: '3',
	5: '4',
	6: '5',
	7: '6',
	8: '7',
	9: '8',
	10: '9',
        11: '0',
        28:'enter'
  }

  #find device
  #devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
  #for device in devices:
      #print(device.path, device.name, device.phys)
  code = ''
  dev = InputDevice('/dev/input/event0')
  for event in dev.read_loop():
      if event.type == ecodes.EV_KEY:
          raw = str(categorize(event))
          splits = raw.split(', ')
          if str(splits[2]) == 'down':
              x = splits[1].split(' ')[0]
              num = RFID_LOOKUP[int(x)]
              code = code+num      
              if num == 'enter':  
                  code = code[:-5]
                  if len(code) != 10:
                      code = 'card reader error'
                      print(code)
                  else:
                      global rfid
                      rfid = code                           
                      ret= client1.publish("Rfid/CardNo",rfid)  
                      print(code)
                  code = ''


def visualize(frame):
    global temp , msg ,name
    height, width, channels = frame.shape

    #monitor area
    upper_left_monit = (width // 2 -120 , height // 2 -70)
    bottom_right_monit = (width // 2 +120 , height // 2 +70)
    cv2.rectangle(frame, upper_left_monit, bottom_right_monit, (255, 0, 0), thickness=2)
    cv2.putText(frame, 'temp here!!', upper_left_monit, cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 0, 0))

    #temp number area
    upper_left = (width // 2 -200 , height // 2 -150)
    bottom_right = (width // 2 +200 , height // 2 +150)
    cv2.rectangle(frame, upper_left, bottom_right, (255, 0, 0), thickness=1)

    #show temp
    text = 'Your temp is '+temp
    cv2.putText(frame, text, (10, 40),cv2.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0), 4)
    if temp != '.':
        if float(temp) > 37.5:
            cv2.putText(frame, 'ABNORMAL', (500, 40),cv2.FONT_HERSHEY_SIMPLEX,1, (0, 0, 255), 4)
        else:
            cv2.putText(frame, 'NORMAL', (500, 40),cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 0),4 )
   
    #show msg
    color = (0,0,255) #ng
    msgs = name+' is recorded'
    if msg == msgs:
        color = (0,255,0) #ok

    cv2.putText(frame, msg, (10, 80),cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 3)

    #imgshow
    cv2.namedWindow('Body Temperature checking',flags=cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Body Temperature checking',1280,800)
    cv2.imshow('Body Temperature checking', frame)


#fixed roi
def roi(frame):
    height, width, channels = frame.shape
    y =  height // 2 -150
    x = width // 2 -200
    h = 300
    w = 400
    frame = frame[y:y+h, x:x+w]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray

def nothing(x):
    pass

#canny detect edged
def canny(gray):
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)

    #cv2.namedWindow('image')
    #cv2.createTrackbar('th1','image',0,300,nothing)
    #cv2.createTrackbar('th2','image',0,300,nothing)
    #while(1):
        #Th1 = cv2.getTrackbarPos('th1','image')
        #Th2 = cv2.getTrackbarPos('th2','image')
        #edged = cv2.Canny(blurred, Th1, Th2, 255)
        #cv2.imshow('image',edged)
        #k = cv2.waitKey(1) & 0xFF
        #if k == 27:
            #break
    edged = cv2.Canny(blurred,125 , 0, 255)
    return edged

#find contours display
def warped(edged,gray):
    #find contours display
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    displayCnt = None
    # loop over the contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # the thermostat display
        if len(approx) == 4:
            displayCnt = approx
            break
    #warped
    if displayCnt is not None:
        warped = four_point_transform(gray, displayCnt.reshape(4, 2))
        h,w = warped.shape
        #print(warped.shape)
        if 300  > h > 100 and 400 >w > 100:
            #print(warped.shape)
            return warped

#threh digit display
def threh(warped):
        thresh = cv2.threshold(warped, 50, 255,
        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 9)) 
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel) 
        ksize = (7,7) 
        kernels = np.ones(ksize, np.uint8)
        thresh = cv2.dilate(thresh, kernels, iterations=1) #การพองตัว
        thresh = thresh[50:-40,50:-40]
        return thresh

def findDigit(thresh):
        global temp,status
        temp = '.'

        #split contours
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	    cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        #print(len(cnts))
        digitCnts = []
        # loop over the digit area candidates
        for c in cnts:
            # compute the bounding box of the contour
            (x, y, w, h) = cv2.boundingRect(c)
            # if the contour is sufficiently large, it must be a digit
            #print('w',w)
            #print('h',h)
            if w >=  15 and (h >= 30 and h <= 130):
                digitCnts.append(c)
        #print('find digit :',len(digitCnts))
        
        if len(digitCnts) != 3:
            return
        digitCnts = contours.sort_contours(digitCnts,
	method="left-to-right")[0]
        digits = []

        DIGITS_LOOKUP = {
	(1, 1, 1, 0, 1, 1, 1): 0,
	(0, 0, 1, 0, 0, 1, 0): 1,
	(1, 0, 1, 1, 1, 0, 1): 2,
	(1, 0, 1, 1, 0, 1, 1): 3,
	(0, 1, 1, 1, 0, 1, 0): 4,
	(1, 1, 0, 1, 0, 1, 1): 5,
	(1, 1, 0, 1, 1, 1, 1): 6,
	(1, 0, 1, 0, 0, 1, 0): 7,
	(1, 1, 1, 1, 1, 1, 1): 8,
	(1, 1, 1, 1, 0, 1, 1): 9
        }

        #imgs = []
        for c in digitCnts:
            # extract the digit ROI
            (x, y, w, h) = cv2.boundingRect(c)
            roi = thresh[y:y + h, x:x + w]

            #imgs.append(roi)

            # compute the width and height of each of the 7 segments
            (roiH, roiW) = roi.shape
            (dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
            dHC = int(roiH * 0.05)
            # define the set of 7 segments
            segments = [
                ((0, 0), (w, dH)),	# top
                ((0, 0), (dW, h // 2)),	# top-left
                ((w - dW, 0), (w, h // 2)),	# top-right
                ((0, (h // 2) - dHC) , (w, (h // 2) + dHC)), # center
                ((0, h // 2), (dW, h)),	# bottom-left
                ((w - dW, h // 2), (w, h)),	# bottom-right
                ((0, h - dH), (w, h))	# bottom
            ]
            on = [0] * len(segments)

                # loop over the segments
            for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
                # extract the segment ROI, count the total number of
                # thresholded pixels in the segment, and then compute
                # the area of the segment

                segROI = roi[yA:yB, xA:xB]
                total = cv2.countNonZero(segROI)
                area = (xB - xA) * (yB - yA)

                # if the total number of non-zero pixels is greater than
                # 50% of the area, mark the segment as "on"

                if total / float(area) > 0.5:
                    on[i]= 1
            # lookup the digit and draw it on the image
            digit = DIGITS_LOOKUP[tuple(on)]
            if digit is not None:
                # calculate digit 1
                if str(digit) == '8':
                    roi_h , roi_w = roi.shape
                    if roi_w < 25:
                        digit = 1
                digits.append(digit)

        if len(digits) == 3:
            temp = "{}{}.{}".format(*digits)
            if float(temp) > 37.5:
              status = 'NG'
            else:
              status = 'OK'
            #cv2.imshow('img1',imgs[0])
            #cv2.imshow('img2',imgs[1])
            #cv2.imshow('img3',imgs[2])


def rfidTricker(frame):
    global c ,msg ,rfid,temp,name,status

    if len(rfid) == 10:
        if temp != '.':
            try:
                insertData(selectEmpno(rfid),temp,status)
                msg = name+' is recorded'
            except:
                msg = 'cannot connect db'
            rfid = ''
            c = 0
        else:
            c = c+1
            if c >5:
                msg = 'cannot detect temp'
                rfid = ''
                c = 0


def readTemp(frame):
    gray = roi(frame)
    canny_ = canny(gray)

    #cv2.imshow('roi', gray)
    #cv2.imshow('canny', canny_)

    warped_ = warped(canny_,gray)
    if warped_ is not None:
        #cv2.imshow('warped', warped_)
       
        threh_= threh(warped_)
        #cv2.imshow('threh', threh_)
 
        findDigit(threh_)

def cam():
    global temp
    global msg

    cap = cv2.VideoCapture(0)
    while(cap.isOpened()):
      ret, frame = cap.read()
      if ret == True:
          try:
            
            readTemp(frame)
            rfidTricker(frame)
            visualize(frame) 

          except Exception as e:
            print(e)
          if cv2.waitKey(1) & 0xFF == ord(' '):
            break
      else:
        break
    cap.release()
    cv2.destroyAllWindows()

def thread_cam():
  return cam()

def thread_rfid():
  return rfidRead()


if __name__ == '__main__':
  thrcam = threading.Thread(target=thread_cam)
  thrrfid = threading.Thread(target=thread_rfid)
  thrcam.start()
  thrrfid.start()