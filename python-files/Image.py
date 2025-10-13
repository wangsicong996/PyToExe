import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import time
import tkinter as tk
from PIL import Image, ImageTk
import os

# --- Initialize Tkinter window ---
root = tk.Tk()
root.title("Sign Sight")

# Set custom icon (full path to Desktop)
icon_path = r"C:\Users\Baldev\Desktop\SignSight\signsight logo.png"
root.iconphoto(False, tk.PhotoImage(file=icon_path))

# Create frames for webcam and word display
video_label = tk.Label(root)
video_label.pack(padx=10, pady=10)

word_label = tk.Label(root, text="", font=("Helvetica", 20), bg="#1e1e1e", fg="#00ff00", width=40, height=3)
word_label.pack(padx=10, pady=10)

# --- Initialize OpenCV hand detection ---
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)
classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")

offset = 20
imgSize = 300
labels = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
    "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
    "U", "V", "W", "X", "Y", "Z", "Delete", "Nothing", "Space"
]

# Word tracking
current_letter = ""
typed_word = ""
last_time = time.time()

# --- Function to update frames ---
def update_frame():
    global last_time, typed_word, current_letter
    success, img = cap.read()
    if not success:
        root.after(10, update_frame)
        return

    imgOutput = img.copy()
    hands, _ = detector.findHands(img)

    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']

        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
        imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
        aspectRatio = h / w

        try:
            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize

            prediction, index = classifier.getPrediction(imgWhite, draw=False)

            # Add letter every 1 second
            if time.time() - last_time >= 1:
                current_letter = labels[index]

                if current_letter == "Space":
                    typed_word += " "
                elif current_letter == "Delete":
                    typed_word = typed_word[:-1]
                elif current_letter not in ["Nothing", "Delete"]:
                    typed_word += current_letter

                last_time = time.time()

            # Draw prediction on webcam feed
            cv2.rectangle(imgOutput, (x - offset, y - offset - 50),
                          (x - offset + 90, y - offset - 50 + 50),
                          (255, 0, 255), cv2.FILLED)
            cv2.putText(imgOutput, labels[index], (x, y - 26),
                        cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 2)
            cv2.rectangle(imgOutput, (x - offset, y - offset),
                          (x + w + offset, y + h + offset), (255, 0, 255), 4)

        except Exception as e:
            pass  # ignore small crop errors

    # Convert OpenCV image to Tkinter image
    img_rgb = cv2.cvtColor(imgOutput, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    imgtk = ImageTk.PhotoImage(image=img_pil)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    # Update word display (show last 25 chars)
    word_label.config(text=typed_word[-25:])

    root.after(10, update_frame)

# --- Start webcam update loop ---
update_frame()
root.mainloop()

# --- Release resources on close ---
cap.release()

