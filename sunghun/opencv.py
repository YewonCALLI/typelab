import cv2
import numpy as np

def main():
    cam_index = 1  # 사용할 카메라 인덱스
    cap = cv2.VideoCapture(cam_index, cv2.CAP_ANY)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    save_triggered = False

    cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Preview", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # 더 부드럽게
        th = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            11,   # blockSize
            5     # C
        )

        # morphology 커널 강화
        kernel = np.ones((2, 2), np.uint8)
        th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        display = frame.copy()
        index = 0
        boxes = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            aspect = h / w if w != 0 else 0

            if area < 80 or w < 4 or h < 4:
                continue
            if aspect < 0.3 or aspect > 10:
                continue

            boxes.append((x, y, x + w, y + h))
            cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 1)
            cv2.putText(display, str(index), (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            index += 1

        if boxes:
            x1 = min(b[0] for b in boxes)
            y1 = min(b[1] for b in boxes)
            x2 = max(b[2] for b in boxes)
            y2 = max(b[3] for b in boxes)

            pad_x = int((x2 - x1) * 0.1)
            pad_y = int((y2 - y1) * 0.1)

            x1 -= pad_x
            y1 -= pad_y
            x2 += pad_x
            y2 += pad_y

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            w = x2 - x1
            h = y2 - y1
            target_ratio = 16 / 9

            if w / h > target_ratio:
                new_h = int(w / target_ratio)
                y1 = cy - new_h // 2
                y2 = cy + new_h // 2
            else:
                new_w = int(h * target_ratio)
                x1 = cx - new_w // 2
                x2 = cx + new_w // 2

            # 프레임 밖으로 나가지 않도록 보정
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(display.shape[1], x2)
            y2 = min(display.shape[0], y2)

            # 빨간 박스 표시
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # 저장 트리거되면 thinning용 이미지 저장
            if save_triggered:
                crop = gray[y1:y2, x1:x2]
                blurred_crop = cv2.GaussianBlur(crop, (5, 5), 0)
                th_crop = cv2.adaptiveThreshold(blurred_crop, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                cv2.THRESH_BINARY_INV, 15, 10)
                th_crop = cv2.morphologyEx(th_crop, cv2.MORPH_CLOSE, kernel)
                output = cv2.resize(th_crop, (512, 288))
                cv2.imwrite("thinning_input.png", output)
                print("✅ thinning_input.png 저장 완료")
                save_triggered = False

        cv2.imshow("Preview", display)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('s'):
            save_triggered = True
        elif key == 27:  # ESC
          break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
