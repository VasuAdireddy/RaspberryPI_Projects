import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import RPi.GPIO as r

r.setmode(r.BCM)
r.setwarnings(False)
r.setup(18, r.OUT)
r.setup(23, r.OUT)
r.setup(24, r.OUT)
r.setup(25, r.OUT)

# Initialize PiCamera and set resolution
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# Allow the camera to warm up
time.sleep(0.1)

# Load Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Define the known width of the face (in meters) and the focal length of the camera (in pixels)
KNOWN_WIDTH = 0.15 # meters
FOCAL_LENGTH = 600 # pixels

# Divide the camera's field of view into four quadrants
width, height = camera.resolution
quadrant_width = int(width / 2)
quadrant_height = int(height / 2)

no_of_rows = 2
no_of_columns = 2

floor_map = [[0 for _ in range(no_of_columns)] for _ in range(no_of_rows)]
print(floor_map[0],"\n",floor_map[1], sep="")

def on_off_appliances():
    if floor_map[1][0] == 1:
        r.output(18, r.HIGH)
    else:
         r.output(18, r.LOW)

    if floor_map[0][0] == 1:
        r.output(23, r.HIGH)
    else:
         r.output(23, r.LOW)

    if floor_map[1][1] == 1:
        r.output(24, r.HIGH)
    else:
         r.output(24, r.LOW)

    if floor_map[0][1] == 1:
        r.output(25, r.HIGH)
    else:
         r.output(25, r.LOW)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # Convert the raw frame to a NumPy array
    image = frame.array

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Add a vertical line to separate left and right side of the frame
    cv2.line(image, (quadrant_width, 0), (quadrant_width, height), (0, 255, 0), 1)

    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray,
                                          scaleFactor=1.1,
                                          minNeighbors=5,
                                          minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)

    # Determine which quadrant the detected face is in and turn on the corresponding LED

    '''
        |----------------------|----------------------|
        |                      |                      |
        |  floor_map[0][0]     |    floor_map[0][1]   |
        |                      |                      |
        |----------------------|----------------------|
        |                      |                      |
        |  floor_map[1][0]     |    floor_map[1][1]   |
        |                      |                      |
        |----------------------|----------------------|
    '''
    floor_map[0][0] = floor_map[0][1] = floor_map[1][0] = floor_map[1][1] = 0

    for (x, y, w, h) in faces:
        # Calculate the distance of the detected face from the camera
        face_width = w
        distance = (KNOWN_WIDTH * FOCAL_LENGTH) / face_width
        print("Distance: {:.2f} meters".format(distance))

        # Calculate the center point of the detected face
        face_center = x + (w / 2)

        # Determine which side of the field of view the face is on
        if face_center < quadrant_width:
            if distance < 0.5:
                floor_map[1][0] = 1
            elif distance > 0.5:
                 floor_map[0][0] = 1
        elif face_center > quadrant_width:

            if distance < 0.5:
                 floor_map[1][1] = 1
            elif distance > 0.5:
                 floor_map[0][1] = 1


        on_off_appliances()
        
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)

    # Display the resulting image
    cv2.imshow('Face Detection', image)

    if len(faces) == 0:
        r.output(18, r.LOW)
        r.output(23, r.LOW)
        r.output(24, r.LOW)
        r.output(25, r.LOW)

    # Clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # Wait for a key press to exit

    close = cv2.waitKey(1)
    if close == 113: break

# Clean up
cv2.destroyAllWindows()