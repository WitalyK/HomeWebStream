from pyimagesearch.motion_detection.singlemotiondetector import SingleMotionDetector
from imutils.video import VideoStream
from imutils import resize
from imutils import encodings
from flask import Response, Flask, render_template
from ui_mainform import Ui_Dialog
from PyQt5 import QtWidgets, QtGui
from threading import Lock, Thread
from datetime import datetime
from time import sleep
import cv2

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = Lock()
# initialize a flask object
app = Flask(__name__)
# initialize the video stream and allow the camera sensor to
# warmup
# vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
sleep(2.0)


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


def detect_motion(frameCount):
    # grab global references to the video stream, output frame, and
    # lock variables
    global vs, outputFrame, lock
    # initialize the motion detector and the total number of frames
    # read thus far
    md = SingleMotionDetector(accumWeight=0.1)
    total = 0
    # loop over frames from the video stream
    while True:
        # read the next frame from the video stream, resize it,
        # convert the frame to grayscale, and blur it
        frame = vs.read()
        frame = resize(frame, width=1200)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        # grab the current timestamp and draw it on the frame
        timestamp = datetime.now()
        cv2.putText(frame, timestamp.strftime(
            "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        # if the total number of frames has reached a sufficient
        # number to construct a reasonable background model, then
        # continue to process the frame
        if total > frameCount:
            # detect motion in the image
            motion = md.detect(gray)
            # check to see if motion was found in the frame
            if motion is not None:
                # unpack the tuple and draw the box surrounding the
                # "motion area" on the output frame
                (thresh, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                              (0, 0, 255), 2)

        # update the background model and increment the total number
        # of frames read thus far
        md.update(gray)
        total += 1
        # acquire the lock, set the output frame, and release the
        # lock
        with lock:
            outputFrame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


class MyWindow(QtWidgets.QWidget, Ui_Dialog):  # Ui_WebStream

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.startwebserverbutton.clicked.connect(lambda: self.on_start())
        self.stopwebserverbutton.setDisabled(True)
        self.stopwebserverbutton.clicked.connect(lambda: self.on_stop())
        self.enablebuttoncolor = '''background-color: rgb(255, 130, 5);\n
                                                border-radius: 10px;\n
                                                color: rgb(87, 0, 0);'''
        self.disablebuttoncolor = '''background-color: rgb(255, 74, 38);\n
                                                border-radius: 10px;\n
                                                color: rgb(87, 0, 0);'''

    def on_start(self):
        self.startwebserverbutton.setDisabled(True)
        self.startwebserverbutton.setStyleSheet(self.disablebuttoncolor)
        self.stopwebserverbutton.setDisabled(False)
        self.stopwebserverbutton.setStyleSheet(self.enablebuttoncolor)
        if self.lineEdit.text():
            try:
                port = int(self.lineEdit.text())
                kwargs['port'] = port
            except:
                pass
        if not t1.is_alive(): t1.start()
        # app.run(host="0.0.0.0", port=port, debug=True, threaded=True, use_reloader=False)

    def on_stop(self):
        self.startwebserverbutton.setDisabled(False)
        self.startwebserverbutton.setStyleSheet(self.enablebuttoncolor)
        self.stopwebserverbutton.setDisabled(True)
        self.stopwebserverbutton.setStyleSheet(self.disablebuttoncolor)
        app_qt.quit()


if __name__ == "__main__":
    import sys

    # start a thread that will perform motion detection
    t = Thread(target=detect_motion, args=(32,))
    t.daemon = True
    t.start()
    kwargs = {'host': "0.0.0.0", 'port': 8765, 'debug': False,
              'threaded': True, 'use_reloader': False}
    t1 = Thread(target=app.run, kwargs=kwargs)
    t1.daemon = True

    app_qt = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.setWindowOpacity(0.8)
    window.setWindowIcon(QtGui.QIcon('belka.png'))
    window.show()
    sys.exit(app_qt.exec_())

# release the video stream pointer
vs.stop()
