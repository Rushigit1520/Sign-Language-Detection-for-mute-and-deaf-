import math
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
from keras.models import load_model
import traceback

model = load_model('/cnn8grps_rad1_model.h5')
# Author: Rushikesh Farakate
white = np.ones((400, 400), np.uint8) * 255
cv2.imwrite("white.jpg", white)

capture = cv2.VideoCapture(0)

hd = HandDetector(maxHands=1)
hd2 = HandDetector(maxHands=1)

offset = 29
step = 1
flag = False
suv = 0


def distance(x, y):
    return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))


def distance_3d(x, y):
    return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2) + ((x[2] - y[2]) ** 2))


bfh = 0
dicttt=dict()
count=0
kok=[]

while True:
    try:
        _, frame = capture.read()
        frame = cv2.flip(frame, 1)
        hands = hd.findHands(frame, draw=False, flipType=True)
        print(frame.shape)
        if hands:
            # #print(" --------- lmlist=",hands[1])
            hand = hands[0]
            x, y, w, h = hand['bbox']
            image = frame[y - offset:y + h + offset, x - offset:x + w + offset]
            white = cv2.imread("white.jpg")
            # img_final=img_final1=img_final2=0
            handz = hd2.findHands(image, draw=False, flipType=True)
            if handz:
                hand = handz[0]
                pts = hand['lmList']
                # x1,y1,w1,h1=hand['bbox']

                os = ((400 - w) // 2) - 15
                os1 = ((400 - h) // 2) - 15
                for t in range(0, 4, 1):
                    cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), (pts[t + 1][0] + os, pts[t + 1][1] + os1),
                             (0, 255, 0), 3)
                for t in range(5, 8, 1):
                    cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), (pts[t + 1][0] + os, pts[t + 1][1] + os1),
                             (0, 255, 0), 3)
                for t in range(9, 12, 1):
                    cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), (pts[t + 1][0] + os, pts[t + 1][1] + os1),
                             (0, 255, 0), 3)
                for t in range(13, 16, 1):
                    cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), (pts[t + 1][0] + os, pts[t + 1][1] + os1),
                             (0, 255, 0), 3)
                for t in range(17, 20, 1):
                    cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), (pts[t + 1][0] + os, pts[t + 1][1] + os1),
                             (0, 255, 0), 3)
                cv2.line(white, (pts[5][0] + os, pts[5][1] + os1), (pts[9][0] + os, pts[9][1] + os1), (0, 255, 0),
                         3)
                cv2.line(white, (pts[9][0] + os, pts[9][1] + os1), (pts[13][0] + os, pts[13][1] + os1), (0, 255, 0),
                         3)
                cv2.line(white, (pts[13][0] + os, pts[13][1] + os1), (pts[17][0] + os, pts[17][1] + os1),
                         (0, 255, 0), 3)
                cv2.line(white, (pts[0][0] + os, pts[0][1] + os1), (pts[5][0] + os, pts[5][1] + os1), (0, 255, 0),
                         3)
                cv2.line(white, (pts[0][0] + os, pts[0][1] + os1), (pts[17][0] + os, pts[17][1] + os1), (0, 255, 0),
                         3)

                for i in range(21):
                    cv2.circle(white, (pts[i][0] + os, pts[i][1] + os1), 2, (0, 0, 255), 1)

                cv2.imshow("2", white)
                # cv2.imshow("5", skeleton5)

                # #print(model.predict(img))
                white = white.reshape(1, 400, 400, 3)
                prob = np.array(model.predict(white)[0], dtype='float32')
                ch1 = np.argmax(prob, axis=0)
                prob[ch1] = 0
                ch2 = np.argmax(prob, axis=0)
                prob[ch2] = 0
                ch3 = np.argmax(prob, axis=0)
                prob[ch3] = 0


                from heuristic_classifier import HeuristicClassifier
                ch1 = HeuristicClassifier.apply_heuristics(ch1, ch2, pts)

                print("ch1=", ch1, " ch2=", ch2, " ch3=", ch3)
                kok.append(ch1)

                # # [0->aemnst][1->bfdiuvwkr][2->co][3->gh][4->l][5->pqz][6->x][7->yj]
                if ch1 != 1:
                    if (ch1,ch2) in dicttt:
                        dicttt[(ch1,ch2)] += 1
                    else:
                        dicttt[(ch1,ch2)] = 1

                frame = cv2.putText(frame, "Predicted " + str(ch1), (30, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    3, (0, 0, 255), 2, cv2.LINE_AA)

        cv2.imshow("frame", frame)
        interrupt = cv2.waitKey(1)
        if interrupt & 0xFF == 27:
            # esc key
            break


    except Exception:
        print("==", traceback.format_exc())



dicttt = {key: val for key, val in sorted(dicttt.items(), key = lambda ele: ele[1], reverse = True)}
print(dicttt)
print(set(kok))
capture.release()
cv2.destroyAllWindows()


