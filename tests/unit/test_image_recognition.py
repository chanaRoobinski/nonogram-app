import pytest

from nonogram.image_recognition.interface import ImageToPatternConverter


def test_convert_is_not_implemented():
    converter = ImageToPatternConverter()
    with pytest.raises(NotImplementedError):
        converter.convert("some/image/path.png")
