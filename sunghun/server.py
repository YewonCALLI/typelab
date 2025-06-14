import cv2
import numpy as np
import base64
from websocket import create_connection

# WebSocket 서버 주소
RAILWAY_WS_URL = "ws://your-railway-endpoint"

# 카메라 초기화
cap = cv2.VideoCapture(3)  

def send_image(img):
    _, buf = cv2.imencode('.png', img)
    b64 = base64.b64encode(buf).decode('utf-8')
    try:
        ws = create_connection(RAILWAY_WS_URL)
        ws.send(b64)
        ws.close()
        print("전송 완료")
    except Exception as e:
        print(f"전송 실패: {e}")

while True:
    ret, frame = cap.read()
    if not ret:
        print("카메라 실패")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                               cv2.THRESH_BINARY_INV, 15, 10)

    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    display = frame.copy()
    index = 0

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h < 500:  # 너무 작은 건 제외
            continue

        roi = th[y:y+h, x:x+w]
        roi_resized = cv2.resize(roi, (64, 64))

        # 사각형 표시 + 번호
        cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 1)
        cv2.putText(display, str(index), (x, y-5), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 1)

        # 전송
        send_image(roi_resized)
        index += 1

    cv2.imshow("Preview", display)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('s'):
        print("수동 캡처 실행")  # 이미 실시간 처리 중이므로 의미 없음, 원하면 여기서 처리 트리거 가능

cap.release()
cv2.destroyAllWindows()
