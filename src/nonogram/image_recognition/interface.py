from nonogram.core.grid import Grid


class ImageToPatternConverter:
    """Placeholder for a future phase: converting an uploaded image into a
    nonogram pattern (Grid) via image recognition.

    Not implemented in this MVP. Python's image-processing ecosystem (OpenCV,
    PIL/Pillow) is the intended toolset for a future concrete implementation —
    this is the reason the whole backend is written in Python rather than
    splitting solver logic and image logic across two stacks (see
    NONOGRAM_APP_SKILL.md, Section 0). Future subclasses should override
    convert() with a real implementation.
    """

    def convert(self, image_path: str) -> Grid:
        raise NotImplementedError(
            "Image-to-nonogram conversion is planned for a future phase and "
            "is not implemented yet."
        )
