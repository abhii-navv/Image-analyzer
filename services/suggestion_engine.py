# Import required libraries
from google import genai                     # Google Gemini AI client
from google.genai import types              # For handling structured content (like images)
from dotenv import load_dotenv              # To load environment variables from .env file
import os                                   # For accessing environment variables
import base64                               # (Optional here, not used directly)
import re                                   # For parsing text using regex

# Load environment variables from .env file
load_dotenv()

# Initialize Gemini client using API key from environment
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# Function to dynamically build a prompt based on image analysis values
def build_prompt(lighting, focus, contrast, brightness_value, blur_value, contrast_value):

    conditions = []  # Store condition-based editing suggestions

    # Analyze brightness (exposure)
    if brightness_value < 80:
        conditions.append("Image is underexposed — increase Exposure and lift Shadows.")
    elif brightness_value > 180:
        conditions.append("Image is overexposed — reduce Exposure and pull down Highlights.")
    else:
        conditions.append("Exposure is balanced — make minor light adjustments only.")

    # Analyze sharpness (blur detection)
    if blur_value < 100:
        conditions.append("Image is blurry — apply strong Sharpening and reduce Noise.")
    elif blur_value < 300:
        conditions.append("Image is slightly soft — apply moderate Sharpening.")
    else:
        conditions.append("Image is sharp — minimal sharpening needed.")

    # Analyze contrast
    if contrast_value < 30:
        conditions.append("Contrast is very low — increase Contrast, Clarity, and Texture.")
    elif contrast_value < 60:
        conditions.append("Contrast is moderate — slight boost to Contrast and Clarity.")
    else:
        conditions.append("Contrast is good — avoid over-contrasting.")

    # Convert condition list into formatted bullet points
    condition_block = "\n".join(f"- {c}" for c in conditions)

    # Return the full structured prompt
    return f"""You are a professional wildlife photo editor.

Technical analysis of this image:
- Lighting: {lighting} (brightness: {brightness_value})
- Focus: {focus} (sharpness: {blur_value})
- Contrast: {contrast} (contrast: {contrast_value})

Editing priorities based on values:
{condition_block}

Give specific numeric editing settings for this exact photo.
Use + for positive, - for negative. No ranges — one exact number per setting.
Skip any setting that does not need adjustment.

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
Midtones Hue: [value]
Midtones Saturation: [value]
Highlights Hue: [value]
Highlights Saturation: [value]
Blending: [value]
Balance: [value]

EFFECTS:
Texture: [value]
Clarity: [value]
Dehaze: [value]
Vignette Amount: [value]
Vignette Feather: [value]
Grain Amount: [value]

DETAIL:
Sharpening Amount: [value]
Sharpening Radius: [value]
Sharpening Masking: [value]
Noise Reduction Luminance: [value]
Color Noise Reduction: [value]

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

TONAL CONTRAST:
High Tones: [value]
Mid Tones: [value]
Low Tones: [value]

VIGNETTE:
Outer Brightness: [value]
Inner Brightness: [value]

TIPS:
1. [tip about exposure and lighting for this specific photo]
2. [tip about focus and sharpness]
3. [tip about color and white balance]
4. [tip specific to the wildlife subject in this photo]
5. [tip about post processing order]
6. [tip about camera settings for next time]
7. [one advanced editing tip for this photo]
"""


# Function to send image + prompt to Gemini and get suggestions
def get_suggestions(lighting, focus, contrast, brightness_value, blur_value, contrast_value, image_path):

    # Read image file as bytes
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Detect file extension
    ext = image_path.rsplit(".", 1)[1].lower()

    # Assign MIME type based on extension
    mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/" + ext

    # Build prompt dynamically
    prompt = build_prompt(lighting, focus, contrast, brightness_value, blur_value, contrast_value)

    try:
        # Send request to Gemini model
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),  # Image input
                prompt  # Text prompt
            ]
        )

        # Parse and return structured response
        return parse_response(response.text)

    except Exception as e:
        error_msg = str(e).lower()

        # Handle different types of API errors
        if "api key expired" in error_msg or "api_key_invalid" in error_msg:
            raise GeminiError("Your Gemini API key has expired. Please renew it at aistudio.google.com/apikey")

        elif "quota" in error_msg or "rate" in error_msg or "resource_exhausted" in error_msg:
            raise GeminiError("Gemini rate limit reached. Please wait 1-2 minutes and try again.")

        elif "invalid_argument" in error_msg:
            raise GeminiError("Gemini rejected the request. The image may be corrupted or unsupported.")

        elif "unavailable" in error_msg or "deadline" in error_msg or "timeout" in error_msg:
            raise GeminiError("Gemini is temporarily unavailable. Please try again in a moment.")

        else:
            raise GeminiError(f"Gemini error: {str(e)}")


# Custom exception class for Gemini-related errors
class GeminiError(Exception):
    pass


# Function to parse Gemini's text response into structured data
def parse_response(text):
    lightroom = {}   # Store Lightroom settings
    snapseed = {}    # Store Snapseed settings
    tips = []        # Store tips list

    # Split response into lines
    lines = text.strip().split("\n")

    section = None       # Track current section
    subsection = None    # Track subsection

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Detect sections
        if line == "LIGHTROOM:":
            section = "lightroom"
            subsection = None

        elif line == "SNAPSEED:":
            section = "snapseed"
            subsection = None

        elif line == "TIPS:":
            section = "tips"
            subsection = None

        # Detect subsection (like LIGHT, COLOR, etc.)
        elif line.endswith(":") and section in ["lightroom", "snapseed"]:
            subsection = line[:-1]

        # Parse Lightroom values
        elif section == "lightroom" and ":" in line:
            key, val = line.split(":", 1)
            val = val.strip()

            # Ignore useless values
            if val and val not in ["0", "+0", "-0"] and val.lower() not in ["none", "n/a"]:
                full_key = f"{subsection} — {key.strip()}" if subsection else key.strip()
                lightroom[full_key] = val

        # Parse Snapseed values
        elif section == "snapseed" and ":" in line:
            key, val = line.split(":", 1)
            val = val.strip()

            if val and val not in ["0", "+0", "-0"] and val.lower() not in ["none", "n/a"]:
                full_key = f"{subsection} — {key.strip()}" if subsection else key.strip()
                snapseed[full_key] = val

        # Parse tips using regex
        elif section == "tips":
            match = re.match(r'^(\d+[\.\)]|\-|\•|\*)\s+(.+)', line)
            if match:
                tips.append(match.group(2).strip())

    # Return structured result
    return {
        "lightroom": lightroom,
        "snapseed": snapseed,
        "beginner_tips": tips
    }
