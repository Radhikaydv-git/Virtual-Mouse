import cv2
import mediapipe as mp
import pyautogui

# Initialize the camera, MediaPipe Hands, and PyAutoGUI screen size
cap = cv2.VideoCapture(0)
hand_detector = mp.solutions.hands.Hands(max_num_hands=1)
drawing_utils = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()
index_x, index_y = 0, 0
smoothening = 7  # To make the mouse movement smoother
prev_x, prev_y = 0, 0

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks

    if hands:
        for hand in hands:
            drawing_utils.draw_landmarks(frame, hand)
            landmarks = hand.landmark
            index_finger_tip = landmarks[8]  # Index finger tip
            thumb_tip = landmarks[4]         # Thumb tip
            middle_finger_tip = landmarks[12] # Middle finger tip

            # Convert coordinates
            x_index = int(index_finger_tip.x * frame_width)
            y_index = int(index_finger_tip.y * frame_height)
            index_x = screen_width / frame_width * x_index
            index_y = screen_height / frame_height * y_index

            x_thumb = int(thumb_tip.x * frame_width)
            y_thumb = int(thumb_tip.y * frame_height)
            thumb_x = screen_width / frame_width * x_thumb
            thumb_y = screen_height / frame_height * y_thumb

            # Smoothing the mouse movement
            curr_x = prev_x + (index_x - prev_x) / smoothening
            curr_y = prev_y + (index_y - prev_y) / smoothening

            # Move the mouse
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            # Draw circles on the thumb and index finger tips
            cv2.circle(img=frame, center=(x_index, y_index), radius=10, color=(0, 255, 255), thickness=-1)
            cv2.circle(img=frame, center=(x_thumb, y_thumb), radius=10, color=(0, 0, 255), thickness=-1)

            # Check if thumb and index finger are close for clicking
            if abs(index_y - thumb_y) < 20:
                pyautogui.click()
                pyautogui.sleep(1)
            # Check if thumb and middle finger are close for right-clicking
            elif abs(landmarks[12].y - thumb_y) < 20:
                pyautogui.click(button='right')
                pyautogui.sleep(1)

            # Scrolling functionality: Check if middle finger is up for scrolling
            if middle_finger_tip.y < landmarks[9].y:
                pyautogui.scroll(20)  # Scroll up
            elif middle_finger_tip.y > landmarks[9].y:
                pyautogui.scroll(-20)  # Scroll down

    # Show the video frame
    cv2.imshow('Virtual Mouse', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on pressing 'q'
        break

cap.release()
cv2.destroyAllWindows()
