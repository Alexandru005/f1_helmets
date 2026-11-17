import cv2
import mediapipe as mp

class GestureDetector:
    def __init__(self):
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # Memoria aplicației: reține ce cască e activă
        self.active_pilot = None

        # Încărcăm imaginile (IMREAD_UNCHANGED menține transparența)
        self.helmets = {
            "Max Verstappen": cv2.imread("assets/verstappen.png", cv2.IMREAD_UNCHANGED),
            "Charles Leclerc": cv2.imread("assets/leclerc.png", cv2.IMREAD_UNCHANGED),
            "Kimi Antonelli": cv2.imread("assets/antonelli.png", cv2.IMREAD_UNCHANGED),
            "Lewis Hamilton": cv2.imread("assets/hamilton.png", cv2.IMREAD_UNCHANGED)
        }

    def _get_fingers_state(self, hand_landmarks, is_right_hand=True):
        fingers = []
        lm = hand_landmarks.landmark

        if is_right_hand:
            fingers.append(0 if lm[4].x > lm[3].x else 1)
        else:
            fingers.append(0 if lm[4].x < lm[3].x else 1)

        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]

        for tip, pip in zip(tip_ids, pip_ids):
            if lm[tip].y < lm[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    # Funcția matematică care lipește casca transparentă peste imaginea video
    def _overlay_transparent(self, background, overlay, x, y):
        bg_h, bg_w, _ = background.shape
        h, w, c = overlay.shape # 'c' ne spune câte canale are imaginea (3 = RGB, 4 = RGBA)

        if x >= bg_w or y >= bg_h or x + w <= 0 or y + h <= 0:
            return background

        x_min, x_max = max(x, 0), min(x + w, bg_w)
        y_min, y_max = max(y, 0), min(y + h, bg_h)
        
        overlay_x_min, overlay_x_max = x_min - x, x_min - x + (x_max - x_min)
        overlay_y_min, overlay_y_max = y_min - y, y_min - y + (y_max - y_min)

        overlay_crop = overlay[overlay_y_min:overlay_y_max, overlay_x_min:overlay_x_max]
        
        # VERIFICARE DE SIGURANȚĂ: Aplicăm transparența DOAR dacă fișierul chiar are 4 canale
        if c == 4:
            alpha = overlay_crop[:, :, 3] / 255.0
            alpha_inv = 1.0 - alpha

            for color in range(3):
                background[y_min:y_max, x_min:x_max, color] = (
                    alpha * overlay_crop[:, :, color] +
                    alpha_inv * background[y_min:y_max, x_min:x_max, color]
                )
        else:
            background[y_min:y_max, x_min:x_max] = overlay_crop[:, :, :3]

        return background

    def process_frame(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.holistic.process(img_rgb)

        # 1. GESTUL DE RESET (Mâna ta STÂNGĂ fizică = MediaPipe right_hand)
        if results.right_hand_landmarks:
            fingers = self._get_fingers_state(results.right_hand_landmarks, is_right_hand=True)
            if fingers == [1, 1, 1, 1, 1]: # Reset helmet
                self.active_pilot = None 
            if fingers == [0, 0, 1, 0, 0]: # Degetul mijlociu
                self.active_pilot = "Bye!" 

        # 2. GESTURILE PILOȚILOR (Mâna ta DREAPTĂ fizică = MediaPipe left_hand)
        if results.left_hand_landmarks:
            fingers = self._get_fingers_state(results.left_hand_landmarks, is_right_hand=False)
            
            if fingers == [0, 1, 1, 1, 1]:
                self.active_pilot = "Max Verstappen"
            elif fingers == [1, 0, 0, 0, 0]:
                self.active_pilot = "Charles Leclerc"
            elif fingers == [1, 0, 0, 0, 1]:
                self.active_pilot = "Kimi Antonelli"

        # 3. VERIFICĂM GESTUL COMBINAT (Ambele mâini pentru Hamilton)
        if results.left_hand_landmarks and results.right_hand_landmarks:
            fingers_right = self._get_fingers_state(results.left_hand_landmarks, is_right_hand=False)
            fingers_left = self._get_fingers_state(results.right_hand_landmarks, is_right_hand=True)

            if fingers_right == [0, 0, 0, 0, 0] and fingers_left == [0, 0, 0, 0, 0]:
                if results.pose_landmarks:
                    wrist_15_x = results.pose_landmarks.landmark[15].x
                    wrist_16_x = results.pose_landmarks.landmark[16].x
                    
                    if wrist_16_x > wrist_15_x:
                        self.active_pilot = "Lewis Hamilton"

       # 4. APLICĂM FILTRUL AR
        if results.face_landmarks and self.active_pilot and self.active_pilot in self.helmets:
            helmet_img = self.helmets[self.active_pilot]
            
            if helmet_img is not None:
                h_img, w_img, _ = img.shape
                
                # Extragem coordonatele feței
                x_left = int(results.face_landmarks.landmark[234].x * w_img)
                x_right = int(results.face_landmarks.landmark[454].x * w_img)
                y_top = int(results.face_landmarks.landmark[10].y * h_img)
                
                # 1. MĂRIM LĂȚIMEA CĂȘTII 
                face_width = max(x_right - x_left, 10) 
                helmet_w = int(face_width * 2.7) 
                
                orig_h, orig_w, _ = helmet_img.shape
                aspect_ratio = orig_h / orig_w
                helmet_h = int(helmet_w * aspect_ratio)
                
                # Redimensionăm imaginea
                helmet_resized = cv2.resize(helmet_img, (helmet_w, helmet_h))
                
                # 2. AJUSTĂM POZIȚIA 
                pos_x = x_left - int((helmet_w - face_width) / 2)
                pos_y = y_top - int(helmet_h * 0.35) 
                
                # Lipim imaginea
                img = self._overlay_transparent(img, helmet_resized, pos_x, pos_y)

        # Returnăm imaginea modificată și statusul pentru a fi afișat ca text
        status_text = self.active_pilot if self.active_pilot else "Choose a pilot"
        return img, status_text