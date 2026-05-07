# Author: Rushikesh Farakate
# Importing Libraries
import numpy as np
import math
import cv2
import os, sys
import traceback
import pyttsx3
from keras.models import load_model # type: ignore

from cvzone.HandTrackingModule import HandDetector
from string import ascii_uppercase
import enchant
ddd=enchant.Dict("en-US")
hd = HandDetector(maxHands=1)
hd2 = HandDetector(maxHands=1)
import tkinter as tk
from PIL import Image, ImageTk

offset=29


os.environ["THEANO_FLAGS"] = "device=cuda, assert_no_cpu_op=True"


# Application :

class Application:

    def __init__(self):
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.model = load_model('cnn8grps_rad1_model.h5')
        self.speak_engine=pyttsx3.init()
        self.speak_engine.setProperty("rate",100)
        voices=self.speak_engine.getProperty("voices")
        self.speak_engine.setProperty("voice",voices[0].id)

        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0
        self.space_flag=False
        self.next_flag=True
        self.prev_char=""
        self.count=-1
        self.ten_prev_char=[]
        for i in range(10):
            self.ten_prev_char.append(" ")


        for i in ascii_uppercase:
            self.ct[i] = 0
        print("Loaded model from disk")


        self.root = tk.Tk()
        self.root.title("Sign Language To Text Conversion")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.geometry("1400x750")
        self.root.configure(bg="#1E1E2E")  # Dark mode background

        self.panel = tk.Label(self.root, bg="#1E1E2E")
        self.panel.place(x=50, y=60, width=480, height=640)

        self.panel2 = tk.Label(self.root, bg="#1E1E2E")  # initialize image panel
        self.panel2.place(x=800, y=115, width=400, height=400)

        self.T = tk.Label(self.root, bg="#1E1E2E", fg="#89B4FA")
        self.T.place(x=350, y=5)
        self.T.config(text="Sign Language To Text Conversion", font=("Courier", 30, "bold"))

        self.panel3 = tk.Label(self.root, bg="#1E1E2E", fg="#A6E3A1")  # Current Symbol
        self.panel3.place(x=820, y=585)

        self.T1 = tk.Label(self.root, bg="#1E1E2E", fg="#F38BA8")
        self.T1.place(x=580, y=580)
        self.T1.config(text="Character :", font=("Courier", 30, "bold"))

        self.panel5 = tk.Label(self.root, bg="#1E1E2E", fg="#A6E3A1")  # Sentence
        self.panel5.place(x=820, y=632)

        self.T3 = tk.Label(self.root, bg="#1E1E2E", fg="#F38BA8")
        self.T3.place(x=580, y=632)
        self.T3.config(text="Sentence :", font=("Courier", 30, "bold"))

        self.T4 = tk.Label(self.root, bg="#1E1E2E", fg="#F9E2AF")
        self.T4.place(x=580, y=700)
        self.T4.config(text="Suggestions :", font=("Courier", 26, "bold"))

        btn_style = {"font": ("Courier", 18), "bg": "#313244", "fg": "#CDD6F4", "activebackground": "#45475A", "activeforeground": "#FFFFFF", "relief": "flat", "padx": 10, "pady": 5}

        self.b1=tk.Button(self.root, **btn_style)
        self.b1.place(x=840,y=690)

        self.b2 = tk.Button(self.root, **btn_style)
        self.b2.place(x=960, y=690)

        self.b3 = tk.Button(self.root, **btn_style)
        self.b3.place(x=1080, y=690)

        self.b4 = tk.Button(self.root, **btn_style)
        self.b4.place(x=1200, y=690)

        self.speak = tk.Button(self.root, **btn_style, text="Speak", command=self.speak_fun)
        self.speak.place(x=1250, y=580)

        self.clear = tk.Button(self.root, **btn_style, text="Clear", command=self.clear_fun)
        self.clear.place(x=1250, y=630)

        # Buffer for prediction smoothing (data stability)
        self.prediction_buffer = []





        self.str = " "
        self.ccc=0
        self.word = " "
        self.current_symbol = "C"
        self.photo = "Empty"


        self.word1=" "
        self.word2 = " "
        self.word3 = " "
        self.word4 = " "

        self.video_loop()

    def video_loop(self):
        try:
            ok, frame = self.vs.read()
            cv2image = cv2.flip(frame, 1)
            if cv2image is not None:
                hands = hd.findHands(cv2image, draw=False, flipType=True)
                cv2image_copy=np.array(cv2image)
                cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB)
                self.current_image = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=self.current_image)
                self.panel.imgtk = imgtk
                self.panel.config(image=imgtk)

                if hands[0]:
                    hand = hands[0]
                    map = hand[0]
                    x, y, w, h=map['bbox']
                    image = cv2image_copy[y - offset:y + h + offset, x - offset:x + w + offset]

                    white = cv2.imread("white.jpg")
                    # img_final=img_final1=img_final2=0
                    if image is not None and image.size > 0:
                        handz = hd2.findHands(image, draw=False, flipType=True)
                        self.ccc += 1
                        if handz[0]:
                            hand = handz[0]
                            handmap=hand[0]
                            self.pts = handmap['lmList']
                            # x1,y1,w1,h1=hand['bbox']

                            os = ((400 - w) // 2) - 15
                            os1 = ((400 - h) // 2) - 15
                            for t in range(0, 4, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                         (0, 255, 0), 3)
                            for t in range(5, 8, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                         (0, 255, 0), 3)
                            for t in range(9, 12, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                         (0, 255, 0), 3)
                            for t in range(13, 16, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                         (0, 255, 0), 3)
                            for t in range(17, 20, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                         (0, 255, 0), 3)
                            cv2.line(white, (self.pts[5][0] + os, self.pts[5][1] + os1), (self.pts[9][0] + os, self.pts[9][1] + os1), (0, 255, 0),
                                     3)
                            cv2.line(white, (self.pts[9][0] + os, self.pts[9][1] + os1), (self.pts[13][0] + os, self.pts[13][1] + os1), (0, 255, 0),
                                     3)
                            cv2.line(white, (self.pts[13][0] + os, self.pts[13][1] + os1), (self.pts[17][0] + os, self.pts[17][1] + os1),
                                     (0, 255, 0), 3)
                            cv2.line(white, (self.pts[0][0] + os, self.pts[0][1] + os1), (self.pts[5][0] + os, self.pts[5][1] + os1), (0, 255, 0),
                                     3)
                            cv2.line(white, (self.pts[0][0] + os, self.pts[0][1] + os1), (self.pts[17][0] + os, self.pts[17][1] + os1), (0, 255, 0),
                                     3)

                            for i in range(21):
                                cv2.circle(white, (self.pts[i][0] + os, self.pts[i][1] + os1), 2, (0, 0, 255), 1)

                            res=white
                            self.predict(res)

                            self.current_image2 = Image.fromarray(res)

                            imgtk = ImageTk.PhotoImage(image=self.current_image2)

                            self.panel2.imgtk = imgtk
                            self.panel2.config(image=imgtk)

                            self.panel3.config(text=self.current_symbol, font=("Courier", 30))

                            #self.panel4.config(text=self.word, font=("Courier", 30))



                            self.b1.config(text=self.word1, font=("Courier", 20), wraplength=825, command=self.action1)
                            self.b2.config(text=self.word2, font=("Courier", 20), wraplength=825,  command=self.action2)
                            self.b3.config(text=self.word3, font=("Courier", 20), wraplength=825,  command=self.action3)
                            self.b4.config(text=self.word4, font=("Courier", 20), wraplength=825,  command=self.action4)

                self.panel5.config(text=self.str, font=("Courier", 30), wraplength=1025)
        except Exception:
            print(Exception.__traceback__)
            hands = hd.findHands(cv2image, draw=False, flipType=True)
            cv2image_copy=np.array(cv2image)
            cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB)
            self.current_image = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)

            if hands and hands[0]:
                hand = hands[0]
                map = hand[0]
                x, y, w, h = map['bbox']
                image = cv2image_copy[y - offset:y + h + offset, x - offset:x + w + offset]

                white = cv2.imread("white.jpg")
                # img_final=img_final1=img_final2=0

                handz = None
                if image is not None and image.size > 0:
                    handz = hd2.findHands(image, draw=False, flipType=True)
                    print(" ", self.ccc)
                    self.ccc += 1
                if handz:
                    hand = handz[0]
                    self.pts = hand['lmList']
                    # x1,y1,w1,h1=hand['bbox']

                    os = ((400 - w) // 2) - 15
                    os1 = ((400 - h) // 2) - 15
                    for t in range(0, 4, 1):
                        cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                 (0, 255, 0), 3)
                    for t in range(5, 8, 1):
                        cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                 (0, 255, 0), 3)
                    for t in range(9, 12, 1):
                        cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                 (0, 255, 0), 3)
                    for t in range(13, 16, 1):
                        cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                 (0, 255, 0), 3)
                    for t in range(17, 20, 1):
                        cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1), (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                 (0, 255, 0), 3)
                    cv2.line(white, (self.pts[5][0] + os, self.pts[5][1] + os1), (self.pts[9][0] + os, self.pts[9][1] + os1), (0, 255, 0),
                             3)
                    cv2.line(white, (self.pts[9][0] + os, self.pts[9][1] + os1), (self.pts[13][0] + os, self.pts[13][1] + os1), (0, 255, 0),
                             3)
                    cv2.line(white, (self.pts[13][0] + os, self.pts[13][1] + os1), (self.pts[17][0] + os, self.pts[17][1] + os1),
                             (0, 255, 0), 3)
                    cv2.line(white, (self.pts[0][0] + os, self.pts[0][1] + os1), (self.pts[5][0] + os, self.pts[5][1] + os1), (0, 255, 0),
                             3)
                    cv2.line(white, (self.pts[0][0] + os, self.pts[0][1] + os1), (self.pts[17][0] + os, self.pts[17][1] + os1), (0, 255, 0),
                             3)

                    for i in range(21):
                        cv2.circle(white, (self.pts[i][0] + os, self.pts[i][1] + os1), 2, (0, 0, 255), 1)

                    res=white
                    self.predict(res)

                    self.current_image2 = Image.fromarray(res)

                    imgtk = ImageTk.PhotoImage(image=self.current_image2)

                    self.panel2.imgtk = imgtk
                    self.panel2.config(image=imgtk)

                    self.panel3.config(text=self.current_symbol, font=("Courier", 30))

                    #self.panel4.config(text=self.word, font=("Courier", 30))



                    self.b1.config(text=self.word1, font=("Courier", 20), wraplength=825, command=self.action1)
                    self.b2.config(text=self.word2, font=("Courier", 20), wraplength=825,  command=self.action2)
                    self.b3.config(text=self.word3, font=("Courier", 20), wraplength=825,  command=self.action3)
                    self.b4.config(text=self.word4, font=("Courier", 20), wraplength=825,  command=self.action4)

            self.panel5.config(text=self.str, font=("Courier", 30), wraplength=1025)
        except Exception:
            print("==", traceback.format_exc())
        finally:
            self.root.after(1, self.video_loop)

    def distance(self,x,y):
        return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))

    def action1(self):
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word1.upper()


    def action2(self):
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str=self.str[:idx_word]
        self.str=self.str+self.word2.upper()
        #self.str[idx_word:last_idx] = self.word2


    def action3(self):
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word3.upper()



    def action4(self):
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word4.upper()


    def speak_fun(self):
        self.speak_engine.say(self.str)
        self.speak_engine.runAndWait()


    def clear_fun(self):
        self.str=" "
        self.word1 = " "
        self.word2 = " "
        self.word3 = " "
        self.word4 = " "

    def predict(self, test_image):
        white=test_image
        white = white.reshape(1, 400, 400, 3)
        prob = np.array(self.model.predict(white)[0], dtype='float32')
        ch1 = np.argmax(prob, axis=0)
        prob[ch1] = 0
        ch2 = np.argmax(prob, axis=0)
        prob[ch2] = 0
        ch3 = np.argmax(prob, axis=0)
        prob[ch3] = 0

        pl = [ch1, ch2]

        from heuristic_classifier import HeuristicClassifier
        ch1 = HeuristicClassifier.apply_heuristics(ch1, ch2, self.pts)



        # Stabilize prediction using mode over last 5 frames
        from collections import Counter
        if str(ch1).strip() != "" and str(ch1) != "next" and str(ch1) != "Backspace":
            self.prediction_buffer.append(ch1)
            if len(self.prediction_buffer) > 5:
                self.prediction_buffer.pop(0)
            
            # Use most common prediction
            if len(self.prediction_buffer) > 0:
                ch1 = Counter(self.prediction_buffer).most_common(1)[0][0]
        
        if ch1=="next" and self.prev_char!="next":
            if self.ten_prev_char[(self.count-2)%10]!="next":
                if self.ten_prev_char[(self.count-2)%10]=="Backspace":
                    self.str=self.str[0:-1]
                else:
                    if self.ten_prev_char[(self.count - 2) % 10] != "Backspace":
                        self.str = self.str + self.ten_prev_char[(self.count-2)%10]
            else:
                if self.ten_prev_char[(self.count - 0) % 10] != "Backspace":
                    self.str = self.str + self.ten_prev_char[(self.count - 0) % 10]


        if ch1=="  " and self.prev_char!="  ":
            self.str = self.str + "  "

        self.prev_char=ch1
        self.current_symbol=ch1
        self.count += 1
        self.ten_prev_char[self.count%10]=ch1


        if len(self.str.strip())!=0:
            st=self.str.rfind(" ")
            ed=len(self.str)
            word=self.str[st+1:ed]
            self.word=word
            if len(word.strip())!=0:
                ddd.check(word)
                lenn = len(ddd.suggest(word))
                if lenn >= 4:
                    self.word4 = ddd.suggest(word)[3]

                if lenn >= 3:
                    self.word3 = ddd.suggest(word)[2]

                if lenn >= 2:
                    self.word2 = ddd.suggest(word)[1]

                if lenn >= 1:
                    self.word1 = ddd.suggest(word)[0]
            else:
                self.word1 = " "
                self.word2 = " "
                self.word3 = " "
                self.word4 = " "


    def destructor(self):
        print(self.ten_prev_char)
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()


print("Starting Application...")

(Application()).root.mainloop()
