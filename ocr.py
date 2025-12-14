import cv2
import easyocr
import re

class OCR_Object:

    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.blur_kernel = (3, 3)

    def __preprocess(self, img):
        # resize if too large
        height, width = img.shape[:2]
        max_dim = 1280
        
        if max(height, width) > max_dim:
            scale = max_dim / max(height, width)
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)


        # Convert to grayscale and enhance
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray, self.blur_kernel, 0)
        _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return gray

    def __process_ocr(self, img):
        return self.reader.readtext(img)

    def __postprocess(self, results):
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

        boxes.sort(key=lambda b: (round(b[0] / 25), b[1]))

        final_text = ''
        for _, __, text in boxes:
            final_text += text + ' '

        return final_text.strip()

    def process(self, img):
        preprocessed_img = self.__preprocess(img)
        ocr_results = self.__process_ocr(preprocessed_img)
        final_text = self.__postprocess(ocr_results)
        return final_text
    


if __name__ == "__main__":
    ocr = OCR_Object()
    img = cv2.imread("img/3.jpg")
    text = ocr.process(img)
    print("Extracted Text:", text)