import cv2
import mediapipe as mp
import math
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pandas as pd
from datetime import datetime

# Initialize MediaPipe models
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose

# Function to calculate angle in 3D
def calculate_angle_3d(pointA, pointB, pointC):
    """
    Calculates the angle at point B formed by lines BA and BC in 3D space.
    Returns the angle in degrees.
    """
    # Vectors BA and BC
    BA = [pointA[i] - pointB[i] for i in range(3)]
    BC = [pointC[i] - pointB[i] for i in range(3)]

    # Dot product and magnitudes
    dot_product = sum(BA[i] * BC[i] for i in range(3))
    magnitude_BA = math.sqrt(sum(BA[i] ** 2 for i in range(3)))
    magnitude_BC = math.sqrt(sum(BC[i] ** 2 for i in range(3)))

    # Avoid division by zero and invalid values
    if magnitude_BA == 0 or magnitude_BC == 0:
        return 0.0

    # Ensure the value is within the valid range for acos
    cos_angle = dot_product / (magnitude_BA * magnitude_BC)
    cos_angle = min(1.0, max(-1.0, cos_angle))  # Clamp value between -1 and 1

    # Calculate the angle in radians
    angle_rad = math.acos(cos_angle)
    # Convert to degrees
    angle_deg = math.degrees(angle_rad)

    # Determine direction (optional)
    cross_product = [
        BA[1]*BC[2] - BA[2]*BC[1],
        BA[2]*BC[0] - BA[0]*BC[2],
        BA[0]*BC[1] - BA[1]*BC[0]
    ]
    direction = 1 if cross_product[2] >= 0 else -1

    return angle_deg * direction

# Initialize global variables
recording = False
stop_event = threading.Event()
angle_window = None
video_window = None
angle_data = []

# Declare GUI variables
flexion_extension_angle_label = None
lateral_flexion_angle_label = None
rotation_angle_label = None
cva_angle_label = None
protraction_retraction_value_label = None
flex_ext_label = None
lat_flex_label = None
rotation_label = None
pro_ret_label = None
posture_label = None
video_label = None

def video_loop():
    global flexion_extension_angle_label, lateral_flexion_angle_label, rotation_angle_label, cva_angle_label
    global protraction_retraction_value_label
    global flex_ext_label, lat_flex_label, rotation_label, pro_ret_label, posture_label
    global video_label
    global angle_data, angle_window, video_window

    cap = cv2.VideoCapture(0)

    # Use both Face Mesh and Pose models
    with mp_face_mesh.FaceMesh(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh, mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                break

            # Flip the frame horizontally for a mirror view
            frame = cv2.flip(frame, 1)
            frame_height, frame_width = frame.shape[:2]

            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame
            face_results = face_mesh.process(rgb_frame)
            pose_results = pose.process(rgb_frame)

            # Initialize default values
            flexion_extension = "N/A"
            lateral_flexion = "N/A"
            rotation = "N/A"
            protraction_retraction = "N/A"
            posture_status = "N/A"
            flexion_extension_angle = None
            lateral_flexion_angle = None
            rotation_angle = None
            cva_angle = None
            protraction_retraction_value = None

            if recording and face_results.multi_face_landmarks and pose_results.pose_landmarks:
                # Extract pose landmarks
                pose_landmarks = pose_results.pose_landmarks.landmark

                # Get shoulder coordinates with z-values
                left_shoulder = pose_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                right_shoulder = pose_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

                left_shoulder_coords = (
                    left_shoulder.x * frame_width,
                    left_shoulder.y * frame_height,
                    left_shoulder.z * frame_width
                )
                right_shoulder_coords = (
                    right_shoulder.x * frame_width,
                    right_shoulder.y * frame_height,
                    right_shoulder.z * frame_width
                )

                # Calculate T1 position (midpoint between shoulders) in 3D
                t1_coords = (
                    (left_shoulder_coords[0] + right_shoulder_coords[0]) / 2,
                    (left_shoulder_coords[1] + right_shoulder_coords[1]) / 2,
                    (left_shoulder_coords[2] + right_shoulder_coords[2]) / 2
                )

                # Calculate shoulder width
                shoulder_width = abs(right_shoulder_coords[0] - left_shoulder_coords[0])

                # Get face landmarks
                face_landmarks = face_results.multi_face_landmarks[0].landmark

                # Facial keypoints indices
                chin_idx = 152
                nose_tip_idx = 1
                left_eye_idx = 33
                right_eye_idx = 263
                left_ear_idx = 234  # Left ear approximated as tragus
                right_ear_idx = 454  # Right ear approximated as tragus

                # Get 3D coordinates
                chin = face_landmarks[chin_idx]
                nose_tip = face_landmarks[nose_tip_idx]
                left_eye = face_landmarks[left_eye_idx]
                right_eye = face_landmarks[right_eye_idx]
                left_ear = face_landmarks[left_ear_idx]
                right_ear = face_landmarks[right_ear_idx]

                chin_coords = (chin.x * frame_width, chin.y * frame_height, chin.z * frame_width)
                nose_tip_coords = (nose_tip.x * frame_width, nose_tip.y * frame_height, nose_tip.z * frame_width)
                left_eye_coords = (left_eye.x * frame_width, left_eye.y * frame_height, left_eye.z * frame_width)
                right_eye_coords = (right_eye.x * frame_width, right_eye.y * frame_height, right_eye.z * frame_width)
                left_ear_coords = (left_ear.x * frame_width, left_ear.y * frame_height, left_ear.z * frame_width)
                right_ear_coords = (right_ear.x * frame_width, right_ear.y * frame_height, right_ear.z * frame_width)

                # Midpoint between ears (approximate head center)
                head_center = (
                    (left_ear_coords[0] + right_ear_coords[0]) / 2,
                    (left_ear_coords[1] + right_ear_coords[1]) / 2,
                    (left_ear_coords[2] + right_ear_coords[2]) / 2
                )

                # Reference horizontal point for T1
                horizontal_ref_point = (t1_coords[0] + 100, t1_coords[1], t1_coords[2])

                # Calculate CVA Angle between T1, left ear (tragus), and horizontal reference point
                cva_angle = calculate_angle_3d(horizontal_ref_point, t1_coords, left_ear_coords)

                # Determine Posture Status based on CVA Angle
                if cva_angle < 50:
                    posture_status = "Forward Head Posture"
                else:
                    posture_status = "Good Posture"

                # Body axis vector (from hips to T1)
                left_hip = pose_landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                right_hip = pose_landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

                hips_mid = [
                    (left_hip.x + right_hip.x) / 2 * frame_width,
                    (left_hip.y + right_hip.y) / 2 * frame_height,
                    (left_hip.z + right_hip.z) / 2 * frame_width
                ]

                body_axis = [t1_coords[i] - hips_mid[i] for i in range(3)]

                # Head orientation vectors
                # From nose to chin (front-back tilt)
                head_vector_FB = [chin_coords[i] - nose_tip_coords[i] for i in range(3)]
                # From left ear to right ear (side tilt)
                head_vector_LR = [right_ear_coords[i] - left_ear_coords[i] for i in range(3)]

                # Calculate Flexion/Extension Angle
                flexion_extension_angle = calculate_angle_3d(body_axis, t1_coords, head_center)

                # Determine Flexion/Extension Status
                if flexion_extension_angle > 5:
                    flexion_extension = "Flexion"
                elif flexion_extension_angle < -5:
                    flexion_extension = "Extension"
                else:
                    flexion_extension = "Neutral"

                # Calculate Lateral Flexion Angle
                lateral_flexion_angle = calculate_angle_3d(body_axis, t1_coords, nose_tip_coords)

                # Determine Lateral Flexion Status
                if lateral_flexion_angle > 5:
                    lateral_flexion = "Left Tilt"
                elif lateral_flexion_angle < -5:
                    lateral_flexion = "Right Tilt"
                else:
                    lateral_flexion = "Neutral"

                # Calculate Head Rotation Angle
                rotation_angle = calculate_angle_3d([1, 0, 0], nose_tip_coords, chin_coords)

                # Determine Rotation Status
                if rotation_angle > 5:
                    rotation = "Left Rotation"
                elif rotation_angle < -5:
                    rotation = "Right Rotation"
                else:
                    rotation = "Neutral"

                # Calculate Protraction/Retraction Linear Measurement
                horizontal_displacement = left_ear_coords[0] - t1_coords[0]

                if shoulder_width > 0:
                    protraction_retraction_value = horizontal_displacement / shoulder_width
                else:
                    protraction_retraction_value = 0

                # Define thresholds for interpretation
                threshold = 0.05  # Adjust as needed

                # Determine Protraction/Retraction Status
                if protraction_retraction_value > threshold:
                    protraction_retraction = "Protraction"
                elif protraction_retraction_value < -threshold:
                    protraction_retraction = "Retraction"
                else:
                    protraction_retraction = "Neutral"

                # Draw reference lines and points
                # Horizontal line from T1
                cv2.line(
                    frame,
                    (int(t1_coords[0]), int(t1_coords[1])),
                    (int(horizontal_ref_point[0]), int(horizontal_ref_point[1])),
                    (255, 0, 0), 2
                )

                # Line from T1 to left ear (tragus)
                cv2.line(
                    frame,
                    (int(t1_coords[0]), int(t1_coords[1])),
                    (int(left_ear_coords[0]), int(left_ear_coords[1])),
                    (0, 255, 0), 2
                )

                # Line representing body axis
                cv2.line(
                    frame,
                    (int(hips_mid[0]), int(hips_mid[1])),
                    (int(t1_coords[0]), int(t1_coords[1])),
                    (0, 255, 255), 2
                )

                # Draw keypoints
                keypoints = [chin_coords, nose_tip_coords, left_eye_coords, right_eye_coords,
                             left_ear_coords, right_ear_coords, t1_coords, hips_mid]
                for point in keypoints:
                    cv2.circle(frame, (int(point[0]), int(point[1])), 5, (255, 255, 255), -1)

                # Collect angle data
                angle_record = {
                    'Flexion/Extension Angle': flexion_extension_angle,
                    'Lateral Flexion Angle': lateral_flexion_angle,
                    'Rotation Angle': rotation_angle,
                    'CVA Angle': cva_angle,
                    'Protraction/Retraction Value': protraction_retraction_value,
                    'Posture Status': posture_status
                }
                angle_data.append(angle_record)

                # Update GUI labels
                if angle_window:
                    def update_labels():
                        if flexion_extension_angle is not None:
                            flexion_extension_angle_label.config(
                                text=f'Flex/Ext Angle: {flexion_extension_angle:.2f}°'
                            )
                        else:
                            flexion_extension_angle_label.config(text='Flex/Ext Angle: N/A')

                        if lateral_flexion_angle is not None:
                            lateral_flexion_angle_label.config(
                                text=f'Lateral Flexion Angle: {lateral_flexion_angle:.2f}°'
                            )
                        else:
                            lateral_flexion_angle_label.config(text='Lateral Flexion Angle: N/A')

                        if rotation_angle is not None:
                            rotation_angle_label.config(
                                text=f'Rotation Angle: {rotation_angle:.2f}°'
                            )
                        else:
                            rotation_angle_label.config(text='Rotation Angle: N/A')

                        if cva_angle is not None:
                            cva_angle_label.config(
                                text=f'CVA Angle: {cva_angle:.2f}°'
                            )
                        else:
                            cva_angle_label.config(text='CVA Angle: N/A')

                        if protraction_retraction_value is not None:
                            protraction_retraction_value_label.config(
                                text=f'Pro/Ret Value: {protraction_retraction_value:.3f}'
                            )
                        else:
                            protraction_retraction_value_label.config(text='Pro/Ret Value: N/A')

                        flex_ext_label.config(text=f'Flexion/Extension: {flexion_extension}')
                        lat_flex_label.config(text=f'Lateral Flexion: {lateral_flexion}')
                        rotation_label.config(text=f'Rotation: {rotation}')
                        pro_ret_label.config(text=f'Protraction/Retraction: {protraction_retraction}')
                        posture_label.config(text=f'Posture Status: {posture_status}')

                    angle_window.after(0, update_labels)

            # Update the video frame
            if recording and video_window and video_label:
                frame_resized = cv2.resize(frame, (640, 480))
                rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)

                def update_frame():
                    video_label.imgtk = imgtk
                    video_label.configure(image=imgtk)

                video_window.after(0, update_frame)

            # Small delay to prevent high CPU usage
            cv2.waitKey(1)

    cap.release()

    # Exit when stopped
    if cap.isOpened():
        cap.release()

def start_recording():
    global recording, angle_window, video_window
    global flexion_extension_angle_label, lateral_flexion_angle_label, rotation_angle_label, cva_angle_label
    global protraction_retraction_value_label
    global flex_ext_label, lat_flex_label, rotation_label, pro_ret_label, posture_label
    global video_label, angle_data

    if not recording:
        recording = True
        angle_data = []

        # Create the angle window
        angle_window = tk.Toplevel(window)
        angle_window.title("Angle Measurements")

        # Create labels
        flexion_extension_angle_label = tk.Label(
            angle_window, text="Flex/Ext Angle: N/A", font=("Helvetica", 12)
        )
        flexion_extension_angle_label.pack(pady=5)

        lateral_flexion_angle_label = tk.Label(
            angle_window, text="Lateral Flexion Angle: N/A", font=("Helvetica", 12)
        )
        lateral_flexion_angle_label.pack(pady=5)

        rotation_angle_label = tk.Label(
            angle_window, text="Rotation Angle: N/A", font=("Helvetica", 12)
        )
        rotation_angle_label.pack(pady=5)

        cva_angle_label = tk.Label(
            angle_window, text="CVA Angle: N/A", font=("Helvetica", 12)
        )
        cva_angle_label.pack(pady=5)

        protraction_retraction_value_label = tk.Label(
            angle_window, text="Pro/Ret Value: N/A", font=("Helvetica", 12)
        )
        protraction_retraction_value_label.pack(pady=5)

        flex_ext_label = tk.Label(
            angle_window, text="Flexion/Extension: N/A", font=("Helvetica", 12)
        )
        flex_ext_label.pack(pady=5)

        lat_flex_label = tk.Label(
            angle_window, text="Lateral Flexion: N/A", font=("Helvetica", 12)
        )
        lat_flex_label.pack(pady=5)

        rotation_label = tk.Label(
            angle_window, text="Rotation: N/A", font=("Helvetica", 12)
        )
        rotation_label.pack(pady=5)

        pro_ret_label = tk.Label(
            angle_window, text="Protraction/Retraction: N/A", font=("Helvetica", 12)
        )
        pro_ret_label.pack(pady=5)

        posture_label = tk.Label(
            angle_window, text="Posture Status: N/A", font=("Helvetica", 12)
        )
        posture_label.pack(pady=5)

        # Window closing events
        def on_angle_window_close():
            stop_recording()

        angle_window.protocol("WM_DELETE_WINDOW", on_angle_window_close)

        # Create the video window
        video_window = tk.Toplevel(window)
        video_window.title("Video Feed")

        video_label = tk.Label(video_window)
        video_label.pack()

        def on_video_window_close():
            stop_recording()

        video_window.protocol("WM_DELETE_WINDOW", on_video_window_close)

def stop_recording():
    global recording, angle_window, video_window
    global flexion_extension_angle_label, lateral_flexion_angle_label, rotation_angle_label, cva_angle_label
    global protraction_retraction_value_label
    global flex_ext_label, lat_flex_label, rotation_label, pro_ret_label, posture_label
    global video_label
    global angle_data

    if recording:
        recording = False
        if angle_window:
            angle_window.destroy()
            angle_window = None

        if video_window:
            video_window.destroy()
            video_window = None

        # Save data to Excel
        if angle_data:
            try:
                df = pd.DataFrame(angle_data)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'Neck_Angle_Data_{timestamp}.xlsx'
                df.index += 1  # Start frame count from 1
                df.index.name = 'Frame'
                df.to_excel(filename)
                messagebox.showinfo(
                    "Info", f"Recording Stopped\nData saved to {filename}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {e}")
        else:
            messagebox.showinfo("Info", "Recording Stopped\nNo data to save.")

        # Reset GUI variables
        flexion_extension_angle_label = None
        lateral_flexion_angle_label = None
        rotation_angle_label = None
        cva_angle_label = None
        protraction_retraction_value_label = None
        flex_ext_label = None
        lat_flex_label = None
        rotation_label = None
        pro_ret_label = None
        posture_label = None
        video_label = None
        angle_data = []

def on_closing():
    stop_event.set()
    window.destroy()

# Create the main window
window = tk.Tk()
window.title("Neck Movement Tracker - Control Panel")

# Create buttons
button_frame = tk.Frame(window)
button_frame.pack(pady=20)

start_button = tk.Button(
    button_frame, text="Start Recording", command=start_recording, width=15
)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(
    button_frame, text="Stop Recording", command=stop_recording, width=15
)
stop_button.pack(side=tk.LEFT, padx=10)

# Start the video processing thread
video_thread = threading.Thread(target=video_loop)
video_thread.daemon = True
video_thread.start()

# Handle window closing
window.protocol("WM_DELETE_WINDOW", on_closing)

# Start the Tkinter event loop
window.mainloop()
