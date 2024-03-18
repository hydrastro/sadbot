import easyocr
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from sadbot.commands import googletrans

# map user shortcut to the actual language model name
L_MAP = {
    'ch': 'ch_sim'
}

def get_text(lang: str, photo: bytes) -> str:
    if lang in L_MAP:
        lang = L_MAP[lang]
    if not lang:
        lang = "en" # default

    reader = easyocr.Reader([lang], gpu=False)
    result = reader.readtext(photo)

    res = "OCR:\n"
    for data in result:
        res += data[1] + '\n'
    
    return res


def get_text_and_translate(lang: str, photo: bytes, translator: googletrans.Translator, dest: str, src: str) -> str:
    if lang in L_MAP:
        lang = L_MAP[lang]
    if not lang:
        lang = "en" # default

    reader = easyocr.Reader([lang], gpu=False)
    result = reader.readtext(photo)

    image = Image.open(BytesIO(photo))
    surface = ImageDraw.Draw(image)

    for data in result:
        coords = data[0]
        text = data[1]
        res = ""
        try:
            res = translator.translate(text, dest=dest, src=src).text
        except ValueError as error:
            res = str(error)
        
        font = ImageFont.truetype("./sadbot/assets/fonts/arialbd.ttf", 32)
        surface.text((coords[0][0], coords[0][1]), res, font=font, fill="black", stroke_width=4, stroke_fill="#ffffff")
    
    out = BytesIO()
    image.save(out, format="JPEG")
    return out.getvalue()

