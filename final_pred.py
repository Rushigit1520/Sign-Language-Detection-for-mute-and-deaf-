# Author: Rushikesh Farakate
# Sign Language To Text and Speech Conversion - Main Application

import numpy as np
import math
import cv2
import os, sys, traceback, logging
from collections import Counter
from string import ascii_uppercase

import pyttsx3
from keras.models import load_model  # type: ignore
from cvzone.HandTrackingModule import HandDetector
import enchant
import tkinter as tk
from PIL import Image, ImageTk

# Import heuristic classifier ONCE at top level (not inside loop)
from heuristic_classifier import HeuristicClassifier

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "cnn8grps_rad1_model.h5")
WHITE_IMG_PATH = os.path.join(BASE_DIR, "white.jpg")
CANVAS_SIZE = 400
CROP_OFFSET = 29
PRED_BUFFER = 5
LOOP_DELAY = 1

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("SignLangApp")

hd = HandDetector(maxHands=1)
hd2 = HandDetector(maxHands=1)
spell_dict = enchant.Dict("en-US")


def draw_skeleton(pts, bw, bh):
    white = cv2.imread(WHITE_IMG_PATH)
    if white is None:
        white = np.ones((CANVAS_SIZE, CANVAS_SIZE, 3), np.uint8) * 255
    ox = ((CANVAS_SIZE - bw) // 2) - 15
    oy = ((CANVAS_SIZE - bh) // 2) - 15
    for s, e in [(0,4),(5,8),(9,12),(13,16),(17,20)]:
        for t in range(s, e):
            cv2.line(white, (pts[t][0]+ox, pts[t][1]+oy), (pts[t+1][0]+ox, pts[t+1][1]+oy), (0,255,0), 3)
    for a, b in [(5,9),(9,13),(13,17),(0,5),(0,17)]:
        cv2.line(white, (pts[a][0]+ox, pts[a][1]+oy), (pts[b][0]+ox, pts[b][1]+oy), (0,255,0), 3)
    for i in range(21):
        cv2.circle(white, (pts[i][0]+ox, pts[i][1]+oy), 2, (0,0,255), 1)
    return white


class Application:
    def __init__(self):
        self.vs = cv2.VideoCapture(0)
        if not self.vs.isOpened():
            log.error("Cannot open webcam"); sys.exit(1)
        if not os.path.isfile(MODEL_PATH):
            log.error("Model not found: %s", MODEL_PATH); sys.exit(1)
        self.model = load_model(MODEL_PATH)
        log.info("Model loaded from %s", MODEL_PATH)

        self.speak_engine = pyttsx3.init()
        self.speak_engine.setProperty("rate", 100)
        voices = self.speak_engine.getProperty("voices")
        if voices:
            self.speak_engine.setProperty("voice", voices[0].id)

        self.ct = {"blank": 0}
        for ch in ascii_uppercase:
            self.ct[ch] = 0
        self.prediction_buffer = []
        self.blank_flag = 0
        self.space_flag = False
        self.next_flag = True
        self.prev_char = ""
        self.count = -1
        self.ten_prev_char = [" "] * 10
        self.ccc = 0
        self.current_image = None
        self.current_symbol = "-"
        self.photo = "Empty"
        self.pts = None
        self.str = " "
        self.word = " "
        self.word1 = self.word2 = self.word3 = self.word4 = " "

        self._build_gui()
        self.video_loop()

    def _build_gui(self):
        self.root = tk.Tk()
        self.root.title("Sign Language To Text Conversion")
        self.root.protocol("WM_DELETE_WINDOW", self.destructor)
        self.root.geometry("1400x750")
        self.root.configure(bg="#1E1E2E")
        self.root.resizable(False, False)

        self.panel = tk.Label(self.root, bg="#1E1E2E")
        self.panel.place(x=50, y=60, width=480, height=640)
        self.panel2 = tk.Label(self.root, bg="#1E1E2E")
        self.panel2.place(x=800, y=115, width=400, height=400)

        self.T = tk.Label(self.root, bg="#1E1E2E", fg="#89B4FA")
        self.T.place(x=350, y=5)
        self.T.config(text="Sign Language To Text Conversion", font=("Courier", 30, "bold"))

        self.panel3 = tk.Label(self.root, bg="#1E1E2E", fg="#A6E3A1")
        self.panel3.place(x=820, y=585)
        self.T1 = tk.Label(self.root, bg="#1E1E2E", fg="#F38BA8")
        self.T1.place(x=580, y=580)
        self.T1.config(text="Character :", font=("Courier", 30, "bold"))

        self.panel5 = tk.Label(self.root, bg="#1E1E2E", fg="#A6E3A1")
        self.panel5.place(x=820, y=632)
        self.T3 = tk.Label(self.root, bg="#1E1E2E", fg="#F38BA8")
        self.T3.place(x=580, y=632)
        self.T3.config(text="Sentence :", font=("Courier", 30, "bold"))

        self.T4 = tk.Label(self.root, bg="#1E1E2E", fg="#F9E2AF")
        self.T4.place(x=580, y=700)
        self.T4.config(text="Suggestions :", font=("Courier", 26, "bold"))

        bs = {"font": ("Courier", 18), "bg": "#313244", "fg": "#CDD6F4",
              "activebackground": "#45475A", "activeforeground": "#FFFFFF",
              "relief": "flat", "padx": 10, "pady": 5}
        self.b1 = tk.Button(self.root, **bs); self.b1.place(x=840, y=690)
        self.b2 = tk.Button(self.root, **bs); self.b2.place(x=960, y=690)
        self.b3 = tk.Button(self.root, **bs); self.b3.place(x=1080, y=690)
        self.b4 = tk.Button(self.root, **bs); self.b4.place(x=1200, y=690)
        self.speak_btn = tk.Button(self.root, **bs, text="Speak", command=self.speak_fun)
        self.speak_btn.place(x=1250, y=580)
        self.clear_btn = tk.Button(self.root, **bs, text="Clear", command=self.clear_fun)
        self.clear_btn.place(x=1250, y=630)

    def video_loop(self):
        try:
            ok, frame = self.vs.read()
            if not ok or frame is None:
                self.root.after(LOOP_DELAY, self.video_loop); return

            cv2image = cv2.flip(frame, 1)
            cv2image_copy = np.array(cv2image)
            hands = hd.findHands(cv2image, draw=False, flipType=True)

            cv2image_rgb = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB)
            self.current_image = Image.fromarray(cv2image_rgb)
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)

            if hands and hands[0]:
                hand_data = hands[0]
                hand_map = hand_data[0] if isinstance(hand_data, list) else hand_data
                x, y, w, h = hand_map["bbox"]
                y1, y2 = max(y-CROP_OFFSET, 0), min(y+h+CROP_OFFSET, cv2image_copy.shape[0])
                x1, x2 = max(x-CROP_OFFSET, 0), min(x+w+CROP_OFFSET, cv2image_copy.shape[1])
                image = cv2image_copy[y1:y2, x1:x2]

                if image is not None and image.size > 0:
                    handz = hd2.findHands(image, draw=False, flipType=True)
                    self.ccc += 1
                    if handz and handz[0]:
                        hi = handz[0]
                        hm = hi[0] if isinstance(hi, list) else hi
                        self.pts = hm["lmList"]
                        res = draw_skeleton(self.pts, w, h)
                        self.predict(res)

                        self.current_image2 = Image.fromarray(res)
                        imgtk2 = ImageTk.PhotoImage(image=self.current_image2)
                        self.panel2.imgtk = imgtk2
                        self.panel2.config(image=imgtk2)
                        self.panel3.config(text=self.current_symbol, font=("Courier", 30))
                        self.b1.config(text=self.word1, font=("Courier",20), wraplength=825, command=self.action1)
                        self.b2.config(text=self.word2, font=("Courier",20), wraplength=825, command=self.action2)
                        self.b3.config(text=self.word3, font=("Courier",20), wraplength=825, command=self.action3)
                        self.b4.config(text=self.word4, font=("Courier",20), wraplength=825, command=self.action4)

            self.panel5.config(text=self.str, font=("Courier", 30), wraplength=1025)
        except Exception:
            log.error("video_loop error:\n%s", traceback.format_exc())
        finally:
            self.root.after(LOOP_DELAY, self.video_loop)

    def _apply_suggestion(self, word):
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        self.str = self.str[:idx_word] + word.upper()

    def action1(self): self._apply_suggestion(self.word1)
    def action2(self): self._apply_suggestion(self.word2)
    def action3(self): self._apply_suggestion(self.word3)
    def action4(self): self._apply_suggestion(self.word4)

    def speak_fun(self):
        text = self.str.strip()
        if text:
            self.speak_engine.say(text)
            self.speak_engine.runAndWait()

    def clear_fun(self):
        self.str = " "
        self.word1 = self.word2 = self.word3 = self.word4 = " "

    def predict(self, test_image):
        white = test_image.reshape(1, CANVAS_SIZE, CANVAS_SIZE, 3)
        prob = np.array(self.model.predict(white, verbose=0)[0], dtype="float32")
        ch1 = np.argmax(prob, axis=0); prob[ch1] = 0
        ch2 = np.argmax(prob, axis=0); prob[ch2] = 0

        ch1 = HeuristicClassifier.apply_heuristics(ch1, ch2, self.pts)

        if str(ch1).strip() and str(ch1) not in ("next", "Backspace"):
            self.prediction_buffer.append(ch1)
            if len(self.prediction_buffer) > PRED_BUFFER:
                self.prediction_buffer.pop(0)
            if self.prediction_buffer:
                ch1 = Counter(self.prediction_buffer).most_common(1)[0][0]

        if ch1 == "next" and self.prev_char != "next":
            prev2 = self.ten_prev_char[(self.count - 2) % 10]
            if prev2 != "next":
                if prev2 == "Backspace":
                    self.str = self.str[:-1]
                else:
                    self.str += prev2
            else:
                prev0 = self.ten_prev_char[self.count % 10]
                if prev0 != "Backspace":
                    self.str += prev0

        if ch1 == "  " and self.prev_char != "  ":
            self.str += "  "

        self.prev_char = ch1
        self.current_symbol = ch1
        self.count += 1
        self.ten_prev_char[self.count % 10] = ch1

        if self.str.strip():
            st = self.str.rfind(" ")
            word = self.str[st + 1:]
            self.word = word
            if word.strip():
                spell_dict.check(word)
                sugg = spell_dict.suggest(word)
                self.word1 = sugg[0] if len(sugg) >= 1 else " "
                self.word2 = sugg[1] if len(sugg) >= 2 else " "
                self.word3 = sugg[2] if len(sugg) >= 3 else " "
                self.word4 = sugg[3] if len(sugg) >= 4 else " "
            else:
                self.word1 = self.word2 = self.word3 = self.word4 = " "

    def destructor(self):
        log.info("Shutting down...")
        self.root.destroy()
        if self.vs.isOpened():
            self.vs.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    log.info("Starting Sign Language To Text Conversion...")
    app = Application()
    app.root.mainloop()
