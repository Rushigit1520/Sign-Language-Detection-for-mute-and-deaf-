"""
Setup & Verification Script for Sign Language To Text Conversion
Run this before first use to validate the environment.

Usage:
    python setup.py
"""
import sys
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REQUIRED_FILES = [
    "cnn8grps_rad1_model.h5",
    "white.jpg",
    "final_pred.py",
    "heuristic_classifier.py",
]

REQUIRED_PACKAGES = [
    "cv2",
    "numpy",
    "keras",
    "tensorflow",
    "cvzone",
    "mediapipe",
    "pyttsx3",
    "enchant",
    "PIL",
]


def check_python_version():
    v = sys.version_info
    print(f"  Python version: {v.major}.{v.minor}.{v.micro}")
    if v.major < 3 or (v.major == 3 and v.minor < 8):
        print("  [FAIL] Python 3.8+ is required.")
        return False
    print("  [OK]")
    return True


def check_files():
    ok = True
    for f in REQUIRED_FILES:
        path = os.path.join(BASE_DIR, f)
        if os.path.isfile(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"  {f}: [OK] ({size_mb:.1f} MB)")
        else:
            print(f"  {f}: [MISSING]")
            ok = False
    return ok


def check_packages():
    ok = True
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
            print(f"  {pkg}: [OK]")
        except ImportError:
            print(f"  {pkg}: [MISSING]")
            ok = False
    return ok


def check_webcam():
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("  Webcam: [OK]")
            cap.release()
            return True
        else:
            print("  Webcam: [NOT DETECTED]")
            return False
    except Exception as e:
        print(f"  Webcam: [ERROR] {e}")
        return False


def main():
    print("=" * 55)
    print(" Sign Language To Text - Environment Check")
    print("=" * 55)
    results = {}

    print("\n1. Python Version:")
    results["python"] = check_python_version()

    print("\n2. Required Files:")
    results["files"] = check_files()

    print("\n3. Required Packages:")
    results["packages"] = check_packages()

    print("\n4. Webcam Access:")
    results["webcam"] = check_webcam()

    print("\n" + "=" * 55)
    all_ok = all(results.values())
    if all_ok:
        print(" ALL CHECKS PASSED - Ready to run!")
        print(" Launch with: python final_pred.py")
    else:
        print(" SOME CHECKS FAILED:")
        for k, v in results.items():
            if not v:
                print(f"   - {k}")
        if not results.get("packages"):
            print("\n Fix packages: pip install -r requirements.txt")
    print("=" * 55)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
