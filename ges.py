import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

fingerTips = [4, 8, 12, 16, 20]

gesture_map = {
    "01000": "1",
    "01100": "2",
    "01110": "3",
    "01111": "4",
    "11111": "5",
    "11000": "+",
    "11100": "-",
    "00110": "*",
    "00011": "/",
    "00001": "=",
    "00000": "C"
}

expression = ""
cooldown = 0
last_gesture = ""
frame_count = 0

def fingersUp(hand):
    lmList = hand.landmark
    fingerState = ""

    if lmList[fingerTips[0]].x < lmList[fingerTips[0] - 1].x:
        fingerState += "1"
    else:
        fingerState += "0"

    for id in range(1, 5):
        if lmList[fingerTips[id]].y < lmList[fingerTips[id] - 2].y:
            fingerState += "1"
        else:
            fingerState += "0"

    return fingerState

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            finger_state = fingersUp(handLms)
            gesture = gesture_map.get(finger_state, "")

            if gesture and gesture != last_gesture:
                frame_count = 1
                last_gesture = gesture
            elif gesture == last_gesture:
                frame_count += 1
                if frame_count == 15:
                    if gesture == "=":
                        try:
                            result = str(eval(expression))
                            expression = result
                        except:
                            expression = "Error"
                    elif gesture == "C":
                        expression = ""
                    else:
                        expression += gesture
            else:
                last_gesture = ""
                frame_count = 0

    cv2.putText(img, "Expr: " + expression, (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    cv2.imshow("Hand Calculator", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
