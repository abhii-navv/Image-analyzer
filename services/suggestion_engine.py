import google.generativeai as genai
from dotenv import load_dotenv
import os
import base64
import re

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def get_suggestions(lighting, focus, brightness_value, blur_value, image_path):
    
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    ext = image_path.rsplit(".", 1)[1].lower()
    mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/" + ext

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
You are a world-class wildlife photography editor with 20 years of experience.

Analyze this wildlife photo carefully. Here is the technical data:
- Lighting: {lighting} (brightness value: {brightness_value})
- Focus: {focus} (blur value: {blur_value})

Give COMPLETE professional editing settings based on what you actually see in this photo.
Be very specific with values. Positive values with + sign, negative with - sign.
Only recommend settings that will actually improve THIS specific photo.

Use EXACTLY this format:

LIGHTROOM:
LIGHT:
Exposure: [value]
Contrast: [value]
Highlights: [value]
Shadows: [value]
Whites: [value]
Blacks: [value]

COLOR:
Temp: [value]
Tint: [value]
Vibrance: [value]
Saturation: [value]

COLOR MIX:
Red Hue: [value]
Red Saturation: [value]
Red Luminance: [value]
Orange Hue: [value]
Orange Saturation: [value]
Orange Luminance: [value]
Yellow Hue: [value]
Yellow Saturation: [value]
Yellow Luminance: [value]
Green Hue: [value]
Green Saturation: [value]
Green Luminance: [value]
Aqua Hue: [value]
Aqua Saturation: [value]
Aqua Luminance: [value]
Blue Hue: [value]
Blue Saturation: [value]
Blue Luminance: [value]
Purple Hue: [value]
Purple Saturation: [value]
Purple Luminance: [value]
Magenta Hue: [value]
Magenta Saturation: [value]
Magenta Luminance: [value]

COLOR GRADING:
Shadows Hue: [value]
Shadows Saturation: [value]
Shadows Luminance: [value]
Midtones Hue: [value]
Midtones Saturation: [value]
Midtones Luminance: [value]
Highlights Hue: [value]
Highlights Saturation: [value]
Highlights Luminance: [value]
Blending: [value]
Balance: [value]

EFFECTS:
Texture: [value]
Clarity: [value]
Dehaze: [value]
Vignette Amount: [value]
Vignette Midpoint: [value]
Vignette Roundness: [value]
Vignette Feather: [value]
Vignette Highlights: [value]
Grain Amount: [value]
Grain Size: [value]
Grain Roughness: [value]

DETAIL:
Sharpening Amount: [value]
Sharpening Radius: [value]
Sharpening Detail: [value]
Sharpening Masking: [value]
Noise Reduction Luminance: [value]
Noise Reduction Detail: [value]
Noise Reduction Contrast: [value]
Color Noise Reduction: [value]
Color Noise Detail: [value]
Color Noise Smoothness: [value]

SNAPSEED:
TUNE IMAGE:
Brightness: [value]
Contrast: [value]
Saturation: [value]
Ambiance: [value]
Highlights: [value]
Shadows: [value]
Warmth: [value]

DETAILS:
Structure: [value]
Sharpening: [value]

WHITE BALANCE:
Temperature: [value]
Tint: [value]

CURVES:
RGB Curve: [value]
Red: [value]
Green: [value]
Blue: [value]

TONAL CONTRAST:
High Tones: [value]
Mid Tones: [value]
Low Tones: [value]
Protect Highlights: [value]
Protect Shadows: [value]

HDR SCAPE:
Filter Strength: [value]
Brightness: [value]
Saturation: [value]
Smoothing: [value]

LENS BLUR:
Blur Strength: [value]
Transition: [value]
Vignette Strength: [value]

VIGNETTE:
Outer Brightness: [value]
Inner Brightness: [value]

GLAMOUR GLOW:
Glow: [value]
Saturation: [value]
Warmth: [value]

TIPS:
1. [detailed tip about lighting and exposure]
2. [detailed tip about focus and sharpness]
3. [detailed tip about colors and white balance]
4. [detailed tip about the specific wildlife subject in this photo]
5. [detailed tip about post processing order to follow]
6. [detailed tip about a specific tool to use for this photo]
7. [tip for camera settings next time shooting this type of wildlife]

Give real numeric values only. No ranges like 10-20, pick one exact number.
Only recommend tools relevant to THIS specific wildlife photo.
Be specific to what you actually see — animal, background, lighting conditions.
"""

    response = model.generate_content([
        {"mime_type": mime_type, "data": image_data},
        prompt
    ])

    return parse_response(response.text)


def parse_response(text):
    lightroom = {}
    snapseed = {}
    tips = []

    lines = text.strip().split("\n")
    section = None
    subsection = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line == "LIGHTROOM:":
            section = "lightroom"
            subsection = None
        elif line == "SNAPSEED:":
            section = "snapseed"
            subsection = None
        elif line == "TIPS:":
            section = "tips"
            subsection = None
        elif line.endswith(":") and section in ["lightroom", "snapseed"]:
            subsection = line[:-1]
        elif section == "lightroom" and ":" in line:
            key, val = line.split(":", 1)
            val = val.strip()
            if val and val != "0" and val != "+0" and val != "-0" and val.lower() != "none" and val.lower() != "n/a":
                full_key = f"{subsection} — {key.strip()}" if subsection else key.strip()
                lightroom[full_key] = val
        elif section == "snapseed" and ":" in line:
            key, val = line.split(":", 1)
            val = val.strip()
            if val and val != "0" and val != "+0" and val != "-0" and val.lower() != "none" and val.lower() != "n/a":
                full_key = f"{subsection} — {key.strip()}" if subsection else key.strip()
                snapseed[full_key] = val
        elif section == "tips":
            match = re.match(r'^(\d+[\.\)]|\-|\•|\*)\s+(.+)', line)
            if match:
                tips.append(match.group(2).strip())

    return {
        "lightroom": lightroom,
        "snapseed": snapseed,
        "beginner_tips": tips
    }