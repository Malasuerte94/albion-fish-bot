import cv2

import matplotlib.pyplot as plt


def detect_fish(image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = [cnt for cnt in contours if 1 <= cv2.boundingRect(cnt)[2] <= 15 and 1 <= cv2.boundingRect(cnt)[3] <= 15]
        
        detected = False
        for contour in filtered_contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(gray_image, (x, y), (x + w, y + h), (0, 255, 0), 1)
            detected = True
            
        if len(contours) > 0:
            plt.imshow(cv2.cvtColor(gray_image, cv2.COLOR_BGR2RGB))
            plt.title("Detected Fish")
            plt.show()

        return detected
    
    
# Example usage
if __name__ == "__main__":
    # Load image
    image = cv2.imread("images/test.png")
    # Create FishDetector object
    detector = detect_fish(image)
    if detector:
        print("Fish detected!")
    else:
        print("No fish detected.")