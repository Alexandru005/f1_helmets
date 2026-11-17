# F1 Helmets
 
A real-time AR filter for your webcam. Show a hand gesture and a Formula 1 driver's helmet appears on your head, tracked live with face, hand and pose detection.
 
Built with Python, OpenCV and MediaPipe Holistic.
 
## How it works
 
1. The webcam frame is mirrored and passed to MediaPipe Holistic, which detects face, hands and body pose.
2. The state of each finger (raised or folded) is computed from the hand landmarks and matched against a gesture.
3. The helmet of the selected driver is resized to your face width and blended over your head with its alpha channel (transparent PNG).
4. The driver's name is drawn on the frame.
## Gestures
 
Hands are mirrored, so use the hand named below as you see it on screen.
 
| Gesture | Result |
| --- | --- |
| Right hand, four fingers up (thumb folded) | Max Verstappen |
| Right hand, thumb only | Charles Leclerc |
| Right hand, thumb and pinky out ("call me") | Kimi Antonelli |
| Both fists, arms crossed in an X | Lewis Hamilton |
| Left hand, open palm | Remove the helmet |
 
If no helmet is selected, the screen shows "Choose a pilot".
 
## Requirements
 
- Python 3.12
- A webcam
- `mediapipe==0.10.14` and `numpy<2` (newer MediaPipe versions removed the `mp.solutions` API used here)
## Installation
 
```powershell
git clone https://github.com/Alexandru005/f1_helmets.git
cd f1_helmets
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
 
On Linux or macOS, activate the environment with `source venv/bin/activate`.
 
## Usage
 
Run from the project folder, so the helmet images are found:
 
```powershell
python main_app.py
```
 
Press `q` or close the window to quit.
 
## Project structure
 
```
f1_helmets/
├── main_app.py          # webcam loop and window
├── img_prelucration.py  # GestureDetector: gestures, face tracking, helmet overlay
├── assets/
│   └── helmets/         # transparent PNG helmets (one per driver)
└── requirements.txt
```
 
## Customizing
 
- **Add a driver:** put a transparent PNG in `assets/helmets/`, register it in the `helmets` dictionary in `img_prelucration.py`, add a gesture in `process_frame`, and a text color in `COLORS` in `main_app.py`.
- **Helmet size and position:** adjust `helmet_w = face_width * 2.7` and `pos_y` in `process_frame`.
## Notes
 
This is a student project and is not affiliated with Formula 1, its teams or its drivers. Helmet images belong to their respective owners.
 