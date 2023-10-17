"""OCR stuff stolen from Yōkai (we miss you)"""
import ctypes
from os.path import isfile

import cv2
from scipy.ndimage import interpolation
import numpy


class TesseractError(Exception):
    """Tesseract Error class"""


class Tesseract:
    """Tesseract class"""

    _lib = None
    _api = None

    # pylint: disable=too-few-public-methods
    class TessBaseAPI(ctypes._Pointer):  # pylint: disable=protected-access
        """Tesseract Base API class"""

        _type_ = type("_TessBaseAPI", (ctypes.Structure,), {})

    @classmethod
    def setup_lib(cls, lib_path=None):
        """Create ctypes wrapper for Tesseract instead of using Python wrapper."""
        if cls._lib is not None:
            return
        if lib_path is None:
            if isfile("/usr/lib/libtesseract.so.4"):
                lib_path = "/usr/lib/libtesseract.so.4"
            else:
                lib_path = "/usr/lib/x86_64-linux-gnu/libtesseract.so.4"
        cls._lib = lib = ctypes.CDLL(lib_path)

        # source:
        # https://github.com/tesseract-ocr/tesseract/blob/95ea778745edd1cdf6ee22f9fe653b9e061d5708/src/api/capi.h

        lib.TessBaseAPICreate.restype = cls.TessBaseAPI

        lib.TessBaseAPIDelete.restype = None  # void
        lib.TessBaseAPIDelete.argtypes = (cls.TessBaseAPI,)  # handle

        lib.TessBaseAPIInit3.argtypes = (
            cls.TessBaseAPI,
            ctypes.c_char_p,
            ctypes.c_char_p,
        )

        lib.TessBaseAPISetImage.restype = None
        lib.TessBaseAPISetImage.argtypes = (
            cls.TessBaseAPI,
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        )

        lib.TessBaseAPISetVariable.argtypes = (
            cls.TessBaseAPI,
            ctypes.c_char_p,
            ctypes.c_char_p,
        )

        lib.TessBaseAPIGetUTF8Text.restype = ctypes.c_char_p
        lib.TessBaseAPIGetUTF8Text.argtypes = (cls.TessBaseAPI,)

    def __init__(self, language="eng", datapath=None, lib_path=None):
        if self._lib is None:
            self.setup_lib(lib_path)
        self._api = self._lib.TessBaseAPICreate()
        self._lib.TessBaseAPIInit3(self._api, datapath, language.encode())
        self.closed = False

    def __del__(self):
        if not self._lib or not self._api:
            return
        if not getattr(self, "closed", False):
            self._lib.TessBaseAPIDelete(self._api)
            self.closed = True

    def _check_setup(self):
        if not self._lib:
            raise TesseractError("lib not configured")
        if not self._api:
            raise TesseractError("api not created")

    def set_image(
        self, imagedata, width, height, bytes_per_pixel, bytes_per_line=None
    ):  # pylint: disable=too-many-arguments
        """Set image function"""
        self._check_setup()
        if bytes_per_line is None:
            bytes_per_line = width * bytes_per_pixel
        self._lib.TessBaseAPISetImage(
            self._api, imagedata, width, height, bytes_per_pixel, bytes_per_line
        )

    def set_variable(self, key, val):
        """Set variable function"""
        self._check_setup()
        self._lib.TessBaseAPISetVariable(self._api, key, val)

    def get_utf8_text(self):
        """Get UTF-8 text function"""
        self._check_setup()
        return self._lib.TessBaseAPIGetUTF8Text(self._api)

    def get_text(self):
        """Get text function"""
        self._check_setup()
        result = self._lib.TessBaseAPIGetUTF8Text(self._api)
        if result:
            return result.decode("utf-8")
        return None


def convert_to_grayscale(image_data):
    """Convert to grayscale function"""
    return cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)


def correct_skew(image, delta=1, limit=5):
    """Correct skew function"""

    # pylint: disable=too-many-locals
    def determine_score(arr, angle):
        """Determine score function"""
        data = interpolation.rotate(arr, angle, reshape=False, order=0)
        histogram = numpy.sum(data, axis=1)
        score = numpy.sum((histogram[1:] - histogram[:-1]) ** 2)
        return histogram, score

    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    scores = []
    angles = numpy.arange(-limit, limit + delta, delta)
    for angle in angles:
        _histogram, score = determine_score(thresh, angle)
        scores.append(score)

    best_angle = angles[scores.index(max(scores))]

    (height, width) = image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    rotated = cv2.warpAffine(
        image,
        matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )

    return best_angle, rotated


def tesseract_process_image2(tess, frame_piece):
    """Process image function"""
    height, width = frame_piece.frame.shape
    tess.set_image(frame_piece.frame.ctypes, width, height, 1)
    text = tess.get_utf8_text()
    return text.strip()


class FramePiece:  # pylint: disable=too-few-public-methods
    """FramePiece class"""

    def __init__(self, img, whitelist):
        self.frame = img
        self.whitelist = (
            whitelist
            if whitelist
            else ("ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz1234567890")
        )
        self.psm = 4


def get_text(lang: str, photo: bytes) -> str:
    """Retrieves text from an image"""
    nparr = numpy.fromstring(photo, numpy.uint8)
    image = cv2.imdecode(
        nparr, cv2.IMREAD_COLOR
    )  # CV_LOAD_IMAGE_COLOR) # cv2.IMREAD_COLOR in OpenCV 3.1
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if image.shape[0] < 1000:
        image = cv2.resize(image, None, fx=2.0, fy=2.0)

    _angle, image = correct_skew(image)

    tess = Tesseract(language=lang)

    frame_piece = FramePiece(image, None)
    decoded_text = tesseract_process_image2(tess, frame_piece)
    decoded_text = decoded_text.decode()
    return decoded_text
