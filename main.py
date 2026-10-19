import cv2
import mediapipe as mp

from hand_tracking import INDEX_TIP, THUMB_TIP
from geometry import render_portal, portal_width, ClosingGestureDetector
from filters import FILTROS


def main():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError(
            "No se pudo abrir la camara. Revisa el indice de camara o los permisos."
        )

    filtro_index = 0
    closing_detector = ClosingGestureDetector()
    encerrar = False

    def ao_clicar(event, x, y, flags, param):
        nonlocal encerrar
        if event == cv2.EVENT_LBUTTONUP and 8 <= x <= 128 and 8 <= y <= 48:
            encerrar = True

    cv2.namedWindow("Filters", cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback("Filters", ao_clicar)

    while not encerrar:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        left_hand = None
        right_hand = None

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks, results.multi_handedness
            ):
                raw_label = handedness.classification[0].label
                label = "Right" if raw_label == "Left" else "Left"

                if label == "Left":
                    left_hand = hand_landmarks
                else:
                    right_hand = hand_landmarks

        if left_hand is not None and right_hand is not None:
            lm_left = left_hand.landmark
            lm_right = right_hand.landmark

            p1 = (lm_left[INDEX_TIP].x * w, lm_left[INDEX_TIP].y * h)
            p2 = (lm_left[THUMB_TIP].x * w, lm_left[THUMB_TIP].y * h)
            p3 = (lm_right[INDEX_TIP].x * w, lm_right[INDEX_TIP].y * h)
            p4 = (lm_right[THUMB_TIP].x * w, lm_right[THUMB_TIP].y * h)

            width = portal_width(p1, p2, p3, p4)

            if closing_detector.update(width, w):
                filtro_index = (filtro_index + 1) % len(FILTROS)

            frame = render_portal(frame, p1, p2, p3, p4, FILTROS[filtro_index])

        cv2.rectangle(frame, (8, 8), (128, 48), (45, 45, 180), -1)
        cv2.putText(frame, "Encerrar", (22, 35), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("Filters", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty("Filters", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    hands.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
