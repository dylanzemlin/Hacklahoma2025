import csv
import copy
import itertools
import time
import tts
import cv2 as cv
import numpy as np
import mediapipe as mp
import socket
from model.keypoint_classifier.keypoint_classifier import KeyPointClassifier


# Constants for custom hand sign recognition
SIGN_CONFIRM_TEXT = "1"
SIGN_BACKSPACE_TEXT = "2"
SIGN_SPACE_TEXT = "3"
TIME_BETWEEN_SIGNS = 5
MSG_ID_CHARACTER = "0"
MSG_ID_NEWLINE = "1"
MSG_ID_BACKSPACE = "2"
MSG_ID_PREDICTION = "3"
MSG_ID_FINALIZE = "4"
MSG_ID_TIME_REMAINING = "5"
MSG_ID_START_UPDATE = "6"
MSG_ID_START_FAIL = "7"
MSG_ID_START_SUCCESS = "8"

# ASL Stuff
use_brect = True
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.5,
)
keypoint_classifier = KeyPointClassifier()

# Read the labels
with open("model/keypoint_classifier/keypoint_classifier_label.csv", encoding="utf-8-sig") as f:
    keypoint_classifier_labels = csv.reader(f)
    keypoint_classifier_labels = [row[0] for row in keypoint_classifier_labels]

# Other stuff
text = ""
is_recording = False
next_record_time = -1
next_prediction_send = -1
last_prediction = ""
first_detected_thumbs_up = -1
last_send_time_remaining = -1
send_buffer_peepo = -1

HOST_DISPLAY = "100.81.9.51"
PORT_DISPLAY = 8080

HOST_TTS = "127.0.0.1"
PORT_TTS = 5004

def send_character(character):
    if character == MSG_ID_CHARACTER or character == MSG_ID_NEWLINE or character == MSG_ID_BACKSPACE or character == MSG_ID_PREDICTION or character == MSG_ID_FINALIZE or character == MSG_ID_TIME_REMAINING:
        return
    
    print("Sending character: " + character)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST_DISPLAY, PORT_DISPLAY))
    combined_bytes = MSG_ID_CHARACTER.encode() + character.encode()
    sock.sendto(combined_bytes, (HOST_DISPLAY, PORT_DISPLAY))

def send_newline():
    print("Sending newline")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST_DISPLAY, PORT_DISPLAY))
    sock.sendto(MSG_ID_NEWLINE.encode(), (HOST_DISPLAY, PORT_DISPLAY))

def send_prediction(character):
    global last_prediction
    # if last_prediction == character:
    #     return

    if character == MSG_ID_CHARACTER or character == MSG_ID_NEWLINE or character == MSG_ID_BACKSPACE or character == MSG_ID_PREDICTION or character == MSG_ID_FINALIZE or character == MSG_ID_TIME_REMAINING:
        return
    
    print("Sending prediction: " + character)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST_DISPLAY, PORT_DISPLAY))
    combined_bytes = MSG_ID_PREDICTION.encode() + character.encode()
    print(combined_bytes)
    sock.sendto(combined_bytes, (HOST_DISPLAY, PORT_DISPLAY))
    last_prediction = character

def send_finalize():
    print("Sending finalize")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST_DISPLAY, PORT_DISPLAY))
    sock.sendto(MSG_ID_FINALIZE.encode(), (HOST_DISPLAY, PORT_DISPLAY))

def send_backspace():
    print("Sending backspace")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST_DISPLAY, PORT_DISPLAY))
    sock.sendto(MSG_ID_BACKSPACE.encode(), (HOST_DISPLAY, PORT_DISPLAY))

def send_tts(text):
    print("Sending TTS: " + text)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST_TTS, PORT_TTS))
    sock.sendto(text.encode(), (HOST_TTS, PORT_TTS))

def send_time_remaining(time_remaining):
    global last_send_time_remaining

    if last_send_time_remaining > time.time():
        return
    
    last_send_time_remaining = time.time() + 0.5
    print("Sending time remaining: " + str(time_remaining))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST_DISPLAY, PORT_DISPLAY))
    rounded_time_remaining = round(time_remaining)
    combined_bytes = MSG_ID_TIME_REMAINING.encode() + str(rounded_time_remaining).encode()
    sock.sendto(combined_bytes, (HOST_DISPLAY, PORT_DISPLAY))

def send_start_begin():
    global send_buffer_peepo

    if send_buffer_peepo > time.time():
        return
    
    send_buffer_peepo = time.time() + 0.5
    print("Sending start begin")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST_DISPLAY, PORT_DISPLAY))
    time_thumbs_remaining = 5 - (time.time() - first_detected_thumbs_up)
    combined_bytes = MSG_ID_START_UPDATE.encode() + str(round(time_thumbs_remaining)).encode()
    sock.sendto(combined_bytes, (HOST_DISPLAY, PORT_DISPLAY))

def send_start_fail():
    print("Sending start fail")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST_DISPLAY, PORT_DISPLAY))
    sock.sendto(MSG_ID_START_FAIL.encode(), (HOST_DISPLAY, PORT_DISPLAY))

def send_start_success():
    print("Sending start success")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST_DISPLAY, PORT_DISPLAY))
    sock.sendto(MSG_ID_START_SUCCESS.encode(), (HOST_DISPLAY, PORT_DISPLAY))

def start():
    global is_recording
    is_recording = True

def on_image_received(image):
    global text, next_record_time, last_prediction, next_prediction_send, first_detected_thumbs_up, is_recording

    # Mirror the iamge
    image = cv.flip(image, 1)

    # Perform a deep copy for debug purposes
    debug_image = copy.deepcopy(image)

    # Convert the image to RGB
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

    # Process the image and get the results from the hands model
    results = hands.process(image)

    # Check if we have any hands
    if results.multi_handedness is not None:

        # Loop through the results and process each hand
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):

            # Bounding box calculation
            brect = calc_bounding_rect(debug_image, hand_landmarks)

            # Landmark calculation
            landmark_list = calc_landmark_list(debug_image, hand_landmarks)

            # Conversion to relative coordinates / normalized coordinates
            pre_processed_landmark_list = pre_process_landmark(landmark_list)

            # Hand sign classification
            hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
        
            if is_recording and next_record_time < time.time():
                if next_record_time == -1:
                    next_record_time = time.time() + TIME_BETWEEN_SIGNS
                else:
                    next_record_time = time.time() + TIME_BETWEEN_SIGNS

                    if keypoint_classifier_labels[hand_sign_id] == SIGN_CONFIRM_TEXT:
                        # We are confirming the text
                        # tts.speak(text)
                        send_tts(text)
                        text = ""
                        is_recording = False
                        first_detected_thumbs_up = -1
                        send_finalize()
                    elif keypoint_classifier_labels[hand_sign_id] == SIGN_BACKSPACE_TEXT:
                        # We are deleting a character
                        text = text[:-1]
                        send_backspace()
                    elif keypoint_classifier_labels[hand_sign_id] == SIGN_SPACE_TEXT:
                        # We are adding a space
                        text += " "
                        send_newline()
                    else:
                        # We are just adding a character
                        text += keypoint_classifier_labels[hand_sign_id]
                        send_character(keypoint_classifier_labels[hand_sign_id])
            elif is_recording and next_record_time > time.time() and next_prediction_send < time.time():
                send_prediction(keypoint_classifier_labels[hand_sign_id])
                next_prediction_send = time.time() + 0.2
            elif is_recording and next_record_time > time.time():
                send_time_remaining(int(next_record_time - time.time()))
            elif not is_recording and keypoint_classifier_labels[hand_sign_id] == SIGN_CONFIRM_TEXT:
                # If we have seen the thumbs up for 5 seconds, we start recording
                if first_detected_thumbs_up == -1:
                    first_detected_thumbs_up = time.time()
                    print("Thumbs up detected")
                elif time.time() - first_detected_thumbs_up > 5:
                    send_start_success()
                    start()
                    first_detected_thumbs_up = -1
                else:
                    print(f"Waiting for 5 seconds: {time.time() - first_detected_thumbs_up}")
                    send_start_begin()
            elif first_detected_thumbs_up != -1:
                first_detected_thumbs_up = -1
                send_start_fail()

            # Drawing part
            debug_image = draw_bounding_rect(use_brect, debug_image, brect)
            debug_image = draw_landmarks(debug_image, landmark_list)
            debug_image = draw_info_text(
                debug_image,
                brect,
                handedness,
                keypoint_classifier_labels[hand_sign_id],
            )
    else:
        next_record_time = -1

    # Display the debug image
    draw_debug(debug_image)

def draw_debug(image):
    cv.rectangle(image, (0, 0), (300, 50), (0, 0, 0), -1)
    cv.putText(image, text, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv.LINE_AA)

    # Draw the time until next sign on the top right
    if is_recording:
        cv.putText(
            image,
            str(int(next_record_time - time.time())),
            (image.shape[1] - 50, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
            cv.LINE_AA,
        )

    cv.imshow("Hand Gesture Recognition", image)

def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)

    return [x, y, x + w, y + h]

def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point

def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list

def draw_landmarks(image, landmark_point):
    if len(landmark_point) > 0:
        # Thumb
        cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]), (0, 0, 0), 6)
        cv.line(
            image,
            tuple(landmark_point[2]),
            tuple(landmark_point[3]),
            (255, 255, 255),
            2,
        )
        cv.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]), (0, 0, 0), 6)
        cv.line(
            image,
            tuple(landmark_point[3]),
            tuple(landmark_point[4]),
            (255, 255, 255),
            2,
        )

        # Index finger
        cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]), (0, 0, 0), 6)
        cv.line(
            image,
            tuple(landmark_point[5]),
            tuple(landmark_point[6]),
            (255, 255, 255),
            2,
        )
        cv.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]), (0, 0, 0), 6)
        cv.line(
            image,
            tuple(landmark_point[6]),
            tuple(landmark_point[7]),
            (255, 255, 255),
            2,
        )
        cv.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]), (0, 0, 0), 6)
        cv.line(
            image,
            tuple(landmark_point[7]),
            tuple(landmark_point[8]),
            (255, 255, 255),
            2,
        )

        # Middle finger
        cv.line(
            image, tuple(landmark_point[9]), tuple(landmark_point[10]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[9]),
            tuple(landmark_point[10]),
            (255, 255, 255),
            2,
        )
        cv.line(
            image, tuple(landmark_point[10]), tuple(landmark_point[11]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[10]),
            tuple(landmark_point[11]),
            (255, 255, 255),
            2,
        )
        cv.line(
            image, tuple(landmark_point[11]), tuple(landmark_point[12]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[11]),
            tuple(landmark_point[12]),
            (255, 255, 255),
            2,
        )

        # Ring finger
        cv.line(
            image, tuple(landmark_point[13]), tuple(landmark_point[14]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[13]),
            tuple(landmark_point[14]),
            (255, 255, 255),
            2,
        )
        cv.line(
            image, tuple(landmark_point[14]), tuple(landmark_point[15]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[14]),
            tuple(landmark_point[15]),
            (255, 255, 255),
            2,
        )
        cv.line(
            image, tuple(landmark_point[15]), tuple(landmark_point[16]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[15]),
            tuple(landmark_point[16]),
            (255, 255, 255),
            2,
        )

        # Little finger
        cv.line(
            image, tuple(landmark_point[17]), tuple(landmark_point[18]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[17]),
            tuple(landmark_point[18]),
            (255, 255, 255),
            2,
        )
        cv.line(
            image, tuple(landmark_point[18]), tuple(landmark_point[19]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[18]),
            tuple(landmark_point[19]),
            (255, 255, 255),
            2,
        )
        cv.line(
            image, tuple(landmark_point[19]), tuple(landmark_point[20]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[19]),
            tuple(landmark_point[20]),
            (255, 255, 255),
            2,
        )

        # Palm
        cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]), (0, 0, 0), 6)
        cv.line(
            image,
            tuple(landmark_point[0]),
            tuple(landmark_point[1]),
            (255, 255, 255),
            2,
        )
        cv.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]), (0, 0, 0), 6)
        cv.line(
            image,
            tuple(landmark_point[1]),
            tuple(landmark_point[2]),
            (255, 255, 255),
            2,
        )
        cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]), (0, 0, 0), 6)
        cv.line(
            image,
            tuple(landmark_point[2]),
            tuple(landmark_point[5]),
            (255, 255, 255),
            2,
        )
        cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]), (0, 0, 0), 6)
        cv.line(
            image,
            tuple(landmark_point[5]),
            tuple(landmark_point[9]),
            (255, 255, 255),
            2,
        )
        cv.line(
            image, tuple(landmark_point[9]), tuple(landmark_point[13]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[9]),
            tuple(landmark_point[13]),
            (255, 255, 255),
            2,
        )
        cv.line(
            image, tuple(landmark_point[13]), tuple(landmark_point[17]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[13]),
            tuple(landmark_point[17]),
            (255, 255, 255),
            2,
        )
        cv.line(
            image, tuple(landmark_point[17]), tuple(landmark_point[0]), (0, 0, 0), 6
        )
        cv.line(
            image,
            tuple(landmark_point[17]),
            tuple(landmark_point[0]),
            (255, 255, 255),
            2,
        )

    # Key Points
    for index, landmark in enumerate(landmark_point):
        if index == 0:  # 手首1
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 1:  # 手首2
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 2:  # 親指：付け根
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 3:  # 親指：第1関節
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 4:  # 親指：指先
            cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
        if index == 5:  # 人差指：付け根
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 6:  # 人差指：第2関節
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 7:  # 人差指：第1関節
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 8:  # 人差指：指先
            cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
        if index == 9:  # 中指：付け根
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 10:  # 中指：第2関節
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 11:  # 中指：第1関節
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 12:  # 中指：指先
            cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
        if index == 13:  # 薬指：付け根
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 14:  # 薬指：第2関節
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 15:  # 薬指：第1関節
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 16:  # 薬指：指先
            cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
        if index == 17:  # 小指：付け根
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 18:  # 小指：第2関節
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 19:  # 小指：第1関節
            cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 20:  # 小指：指先
            cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255), -1)
            cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)

    return image

def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        # Outer rectangle
        cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]), (0, 0, 0), 1)

    return image

def draw_info_text(image, brect, handedness, hand_sign_text):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22), (0, 0, 0), -1)

    info_text = handedness.classification[0].label[0:]
    if hand_sign_text != "":
        info_text = info_text + ":" + hand_sign_text
    cv.putText(
        image,
        info_text,
        (brect[0] + 5, brect[1] - 4),
        cv.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1,
        cv.LINE_AA,
    )

    return image

def draw_info(image, fps, mode, number):
    cv.putText(
        image,
        "FPS:" + str(fps),
        (10, 30),
        cv.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 0, 0),
        4,
        cv.LINE_AA,
    )
    cv.putText(
        image,
        "FPS:" + str(fps),
        (10, 30),
        cv.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 255, 255),
        2,
        cv.LINE_AA,
    )

    mode_string = [
        "Logging Key Point",
        "Capturing Landmarks From Provided Dataset Mode",
    ]
    if 1 <= mode <= 2:
        cv.putText(
            image,
            "MODE:" + mode_string[mode - 1],
            (10, 90),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv.LINE_AA,
        )
        if 0 <= number <= 9:
            cv.putText(
                image,
                "NUM:" + str(number),
                (10, 110),
                cv.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
                cv.LINE_AA,
            )
    return image
