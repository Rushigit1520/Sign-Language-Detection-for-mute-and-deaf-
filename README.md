<div align="center">

# 🤟 Sign Language To Text & Speech Conversion

### Real-Time ASL Fingerspelling Recognition using CNN & MediaPipe

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.12+-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.7+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-00897B?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Author:** Rushikesh Farakate

---

*A real-time computer vision application that translates American Sign Language (ASL) hand gestures into text and speech using Convolutional Neural Networks, MediaPipe hand landmark detection, and heuristic post-processing — achieving up to **99% accuracy** under optimal conditions.*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Model Details](#-model-details)
- [Screenshots](#-screenshots)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

Over **70 million** deaf people worldwide rely on sign language for communication. This project bridges the communication gap by providing a real-time system that:

1. **Captures** hand gestures via webcam
2. **Detects** hand landmarks using MediaPipe
3. **Classifies** gestures into ASL letters using a trained CNN
4. **Refines** predictions with heuristic rules and temporal smoothing
5. **Builds** words and sentences with spell-check suggestions
6. **Speaks** the result aloud via text-to-speech

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎥 **Real-Time Detection** | Live webcam feed with instant hand tracking |
| 🧠 **CNN Classification** | 8-group CNN model with 97-99% accuracy |
| 🔬 **Heuristic Refinement** | Post-processing rules to disambiguate similar gestures |
| 📊 **Prediction Smoothing** | 5-frame temporal buffer to eliminate flickering |
| 📝 **Word Building** | Automatic character-to-word construction |
| 🔤 **Spell Suggestions** | PyEnchant-powered autocomplete (4 suggestions) |
| 🔊 **Text-to-Speech** | pyttsx3-powered voice output |
| ⌫ **Backspace Gesture** | Natural gesture to delete characters |
| 🌙 **Dark Theme UI** | Modern Catppuccin-inspired dark interface |

---

## 🏗 Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Webcam     │────▶│  MediaPipe   │────▶│  Skeleton    │
│   Input      │     │  Hand Track  │     │  Drawing     │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Speech     │◀────│  Sentence    │◀────│   CNN Model  │
│   Output     │     │  Builder     │     │  (8 Groups)  │
└──────────────┘     └──────┬───────┘     └──────┬───────┘
                            │                     │
                            ▼                     ▼
                     ┌──────────────┐     ┌──────────────┐
                     │  Spell Check │     │  Heuristic   │
                     │  Suggestions │     │  Classifier  │
                     └──────────────┘     └──────────────┘
```

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.8+ |
| Deep Learning | TensorFlow / Keras |
| Hand Detection | MediaPipe (via cvzone) |
| Computer Vision | OpenCV |
| GUI Framework | Tkinter |
| Spell Checker | PyEnchant |
| Text-to-Speech | pyttsx3 |
| Data Processing | NumPy |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** ([Download](https://python.org/downloads))
- **Webcam** (built-in or USB)
- **Windows 8+** (recommended)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/RushikeshF/Sign-Language-To-Text-and-Speech-Conversion.git
cd Sign-Language-To-Text-and-Speech-Conversion

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify environment
python setup.py

# 5. Run the application
python final_pred.py
```

### One-Click Launch (Windows)

Simply double-click **`run.bat`** — it handles venv creation, dependency installation, and app launch automatically.

---

## 📁 Project Structure

```
Sign-Language-To-Text-and-Speech-Conversion/
│
├── final_pred.py              # Main application (GUI + prediction)
├── heuristic_classifier.py    # Post-CNN heuristic rules
├── prediction_wo_gui.py       # CLI-only prediction (testing)
├── data_collection_binary.py  # Training data collection utility
├── data_collection_final.py   # Skeleton data collection utility
│
├── cnn8grps_rad1_model.h5     # Pre-trained CNN model (~13 MB)
├── white.jpg                  # Blank canvas template
│
├── requirements.txt           # Python dependencies
├── setup.py                   # Environment verification script
├── run.bat                    # Windows one-click launcher
├── .gitignore                 # Git exclusion rules
├── README.md                  # This file
│
└── AtoZ_3.1/                  # Training dataset (A-Z folders)
    ├── A/
    ├── B/
    └── ... Z/
```

---

## 🔬 How It Works

### 1. Hand Detection (MediaPipe)
The webcam feed is processed frame-by-frame. MediaPipe's hand tracking model identifies 21 landmark points on the detected hand, providing precise positional data regardless of background or lighting conditions.

### 2. Skeleton Rendering
Landmark points are extracted and drawn as a skeleton (green lines + red dots) on a plain white 400×400 canvas. This normalization eliminates background noise and lighting variation.

### 3. CNN Classification (8 Groups)
Instead of classifying all 26 letters directly, the CNN classifies gestures into **8 visually similar groups**:

| Group | Letters |
|-------|---------|
| 0 | A, E, M, N, S, T |
| 1 | B, D, F, I, U, V, K, R, W |
| 2 | C, O |
| 3 | G, H |
| 4 | L |
| 5 | P, Q, Z |
| 6 | X |
| 7 | Y, J |

### 4. Heuristic Refinement
Within each group, mathematical operations on landmark coordinates (distances, relative positions) disambiguate individual letters. This two-stage approach achieves **97% accuracy** generally and **99%** with clean backgrounds.

### 5. Temporal Smoothing
A 5-frame prediction buffer uses majority voting to prevent character flickering during real-time recognition.

### 6. Word Building & Suggestions
- **"next" gesture** → commits the current character
- **"backspace" gesture** → deletes the last character  
- **space gesture** → adds a space between words
- **PyEnchant** provides 4 spell-check suggestions in real-time

---

## 🧠 Model Details

| Property | Value |
|----------|-------|
| Architecture | Convolutional Neural Network |
| Input Shape | 400 × 400 × 3 (RGB) |
| Output Classes | 8 groups |
| Training Data | 180 skeleton images per letter |
| Accuracy | 97% (general) / 99% (clean background) |
| File Size | ~13 MB |
| Framework | Keras / TensorFlow |

---

## 🖼 Screenshots

### System Flowchart
![System Flowchart](https://user-images.githubusercontent.com/99630855/201490238-224f65aa-071f-473a-8c23-a9d60e0a47d8.png)

### MediaPipe Landmarks
![Landmarks](https://user-images.githubusercontent.com/99630855/201489741-3649959e-df4d-4c32-898a-8f994be92ca2.png)

### Use-Case Diagram
![Use-case](https://user-images.githubusercontent.com/99630855/201490218-85f4c194-0496-4dfb-b920-e486256bd6b7.png)

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Webcam not detected** | Check USB connection; try `cv2.VideoCapture(1)` in code |
| **Model file not found** | Ensure `cnn8grps_rad1_model.h5` is in the project root |
| **PyEnchant import error** | Install enchant C library: `pip install pyenchant` |
| **TensorFlow GPU issues** | Use CPU: `pip install tensorflow-cpu` |
| **Tkinter not found** | Reinstall Python with "tcl/tk" option checked |
| **Low accuracy** | Ensure good lighting; keep hand centered in frame |
| **App crashes on start** | Run `python setup.py` to diagnose missing components |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Made with ❤️ by Rushikesh Farakate**

*If this project helped you, consider giving it a ⭐!*

</div>
