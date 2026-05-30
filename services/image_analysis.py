import cv2
import numpy as np
def analyze_brightness(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)

    if brightness < 60:
        label = "Underexposed"
    elif brightness > 200:
        label = "Overexposed"
    elif brightness < 100:
        label = "Slightly Dark"
    elif brightness > 160:
        label = "Slightly Bright"
    else:
        label = "Balanced"

    return label, round(brightness, 2)


def analyze_blur(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_value = cv2.Laplacian(gray, cv2.CV_64F).var()

    if blur_value < 50:
        label = "Very Blurry"
    elif blur_value < 200:
        label = "Slightly Blurry"
    elif blur_value < 500:
        label = "Mostly Sharp"
    else:
        label = "Sharp"

    return label, round(blur_value, 2)

def analyze_image(image_path):
    lighting_label, brightness_value = analyze_brightness(image_path)
    focus_label, blur_value = analyze_blur(image_path)

    return {
        "lighting": lighting_label,
        "focus": focus_label,
        "brightness_value": brightness_value,
        "blur_value": blur_value
    }