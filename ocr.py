import cv2
import easyocr
import re
import os

reader = easyocr.Reader(['en'], gpu=False)

def process_ocr(img):
    # preprocess
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # easy ocr for text detection and recognition
    results = reader.readtext(gray)

    # order fixing and filtering
    boxes = []
    for box, text, conf in results:
        if conf < 0.4:
            continue
        text = re.sub(r'[^A-Za-z0-9 !]', '', text).strip()
        if not text:
            continue
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        boxes.append((sum(ys)/4, sum(xs)/4, text))

    # sort top-to-bottom, left-to-right
    boxes.sort(key=lambda b: (round(b[0] / 25), b[1]))

    final_text = ''
    for _, __, text in boxes:
        final_text += text + ' '

    return final_text.strip()
