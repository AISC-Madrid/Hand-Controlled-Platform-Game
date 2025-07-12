import cv2
import mediapipe as mp

class HandController:
    def __init__(self, cam_index=0):
        self.cap = cv2.VideoCapture(cam_index)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.results = None
        self.move_left = False
        self.move_right = False
        self.jump = False
        self.mp_draw = mp.solutions.drawing_utils

    def update(self, screen_width=800):
        success, frame = self.cap.read()
        if not success:
            return

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)

        # Reset controls
        self.move_left = False
        self.move_right = False
        self.jump = False

        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[0]
            if len(self.results.multi_hand_landmarks) > 1:
                hand_landmarks = self.results.multi_hand_landmarks[1]
            index_tip = hand_landmarks.landmark[8]
            thumb_tip = hand_landmarks.landmark[4]

            # Movement logic
            if index_tip.x < 0.4:
                self.move_left = True
            elif index_tip.x > 0.6:
                self.move_right = True

            dx = index_tip.x - thumb_tip.x
            dy = index_tip.y - thumb_tip.y
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < 0.05:
                self.jump = True

            # Draw landmarks
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        # Show the camera window (real-time)
        cv2.imshow("Hand Control", frame)
        cv2.waitKey(1)

    def get_controls(self):
        return self.move_left, self.move_right, self.jump

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
