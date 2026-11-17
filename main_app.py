import cv2

from img_prelucration import GestureDetector

WINDOW = "F1-Helmets"

# Culorile textului în format BGR (ordinea OpenCV)
COLORS = {
    "Max Verstappen": (255, 0, 0),
    "Kimi Antonelli": (190, 210, 0),
    "Charles Leclerc": (0, 0, 255),
    "Lewis Hamilton": (240, 32, 160),
    "Choose a pilot": (255, 210, 20),
}


def main():
    # Inițializăm detectorul de gesturi (AI-ul)
    detector = GestureDetector()

    # Pornim camera web (0 = prima cameră)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Nu pot deschide camera")

    # Fereastră redimensionabilă: imaginea se întinde pe toată fereastra
    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW, 1000, 700)

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # 1. Oglindim imaginea (crucial pentru logica de stânga/dreapta din GestureDetector)
        frame = cv2.flip(frame, 1)

        # 2. Procesăm cadrul pentru a lipi filtrul AR și a obține textul
        frame, command_text = detector.process_frame(frame)

        # 3. Scriem textul direct pe imagine
        color = COLORS.get(command_text)
        if color:
            cv2.putText(frame, command_text, (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # 4. Afișăm cadrul
        cv2.imshow(WINDOW, frame)

        # q pentru ieșire sau închiderea ferestrei cu butonul X
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
            break

    # Eliberăm camera și închidem ferestrele
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()