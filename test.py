import cv2
import matplotlib.pyplot as plt
import numpy as np
from bot_inputs.bot_logic import enhance_image

def detect_fish(ss, template):
    checkFloater = cv2.imread(ss)
    template = cv2.imread(template)

    enhanced_image = enhance_image(checkFloater)
    enhanced_template = enhance_image(template)

    # Parameters for multi-scale template matching
    scales = np.linspace(0.8, 1.5, 7)  # Adjust the range and number of scales as needed
    best_match = None
    best_val = -np.inf

    for scale in scales:
        resized_template = cv2.resize(enhanced_template, (0, 0), fx=scale, fy=scale)
        result = cv2.matchTemplate(enhanced_image, resized_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > best_val:
            best_val = max_val
            best_match = (max_loc, resized_template.shape[:2])

    if best_val > 0.7:
        print(f"Best match value: {best_val}")
        top_left, (h, w) = best_match
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(checkFloater, top_left, bottom_right, (0, 255, 0), 2)

        # Use matplotlib to display the image
        plt.imshow(cv2.cvtColor(checkFloater, cv2.COLOR_BGR2RGB))
        plt.title("Detected Floater")
        plt.show()

        return True

    return False


# Example usage
if __name__ == "__main__":
    # Load image
    image_path = "images/test4.png"
    template_path = "images/detected.png"

    # Detect fish
    detected = detect_fish(image_path, template_path)
    if detected:
        print("Fish detected!")
    else:
        print("No fish detected.")
