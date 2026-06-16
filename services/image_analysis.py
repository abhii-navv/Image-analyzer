# Import Gemini AI SDK (new version)
import google.generativeai as genai

# Load environment variables from .env file
from dotenv import load_dotenv

# OS module to access environment variables
import os

# Used to convert image into base64 format (required for API)
import base64

# Regex module for parsing structured text
import re


# Load variables from .env file into environment
load_dotenv()

# Get Gemini API key from environment
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini client with API key
genai.configure(api_key=api_key)


# Main function to get editing suggestions from Gemini
def get_suggestions(lighting, focus, contrast, brightness_value, blur_value, contrast_value, image_path):

    # Open image file in binary mode
    with open(image_path, "rb") as f:
        # Convert image to base64 string (required for Gemini input)
        image_data = base64.b64encode(f.read()).decode("utf-8")

    # Extract file extension (jpg, png, etc.)
    ext = image_path.rsplit(".", 1)[1].lower()

    # Determine correct MIME type for image
    mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/" + ext

    # Initialize Gemini model (fast + powerful version)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Build prompt dynamically using f-string
    prompt = f"""
You are a world-class wildlife photography editor with 20 years of experience.

Analyze this wildlife photo carefully. Here is the technical data:
- Lighting: {lighting} (brightness value: {brightness_value})
- Focus: {focus} (blur value: {blur_value})
- Contrast: {contrast} (contrast value: {contrast_value})

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

    # Send request to Gemini with image + prompt
    response = model.generate_content([
        {"mime_type": mime_type, "data": image_data},  # Image input
        prompt  # Text prompt
    ])

    # Parse response text into structured output
    return parse_response(response.text)


# Function to convert raw Gemini text into structured dictionaries
def parse_response(text):

    lightroom = {}   # Dictionary to store Lightroom settings
    snapseed = {}    # Dictionary to store Snapseed settings
    tips = []        # List to store tips

    # Split response into lines
    lines = text.strip().split("\n")

    section = None       # Track current section (LIGHTROOM / SNAPSEED / TIPS)
    subsection = None    # Track subsection (LIGHT, COLOR, etc.)

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Identify main sections
        if line == "LIGHTROOM:":
            section = "lightroom"
            subsection = None

        elif line == "SNAPSEED:":
            section = "snapseed"
            subsection = None

        elif line == "TIPS:":
            section = "tips"
            subsection = None

        # Identify subsections like LIGHT:, COLOR:, etc.
        elif line.endswith(":") and section in ["lightroom", "snapseed"]:
            subsection = line[:-1]

        # Parse Lightroom values
        elif section == "lightroom" and ":" in line:
            key, val = line.split(":", 1)
            val = val.strip()

            # Filter out useless values
            if val and val != "0" and val != "+0" and val != "-0" and val.lower() != "none" and val.lower() != "n/a":
                full_key = f"{subsection} — {key.strip()}" if subsection else key.strip()
                lightroom[full_key] = val

        # Parse Snapseed values
        elif section == "snapseed" and ":" in line:
            key, val = line.split(":", 1)
            val = val.strip()

            if val and val != "0" and val != "+0" and val != "-0" and val.lower() != "none" and val.lower() != "n/a":
                full_key = f"{subsection} — {key.strip()}" if subsection else key.strip()
                snapseed[full_key] = val

        # Extract numbered tips using regex
        elif section == "tips":
            match = re.match(r'^(\d+[\.\)]|\-|\•|\*)\s+(.+)', line)
            if match:
                tips.append(match.group(2).strip())

    # Return structured output
    return {
        "lightroom": lightroom,
        "snapseed": snapseed,
        "beginner_tips": tips
    }
