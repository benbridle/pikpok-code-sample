import base64
from PIL import Image

image_length = 16
palette_size = 16

class ProfileImage:
    """A square pixel-art image for use as a profile picture. Each pixel is
    represented by an int, which references a colour on a palett."""
    def __init__(self):
        self.width = image_length
        self.height = image_length
        self.palette_size = palette_size
        self.image = []
        for _ in range(self.height):
            self.image.append([0] * self.width)


    @classmethod
    def from_base64_string(cls, base64_string):
        image_bytes = base64.b64decode(base64_string.encode('utf-8'))
        return cls.from_bytes(image_bytes)

    def to_base64_string(self):
        return base64.b64encode(bytes(self)).decode("utf-8")


    @classmethod
    def from_bytes(cls, image_bytes):
        flat_image = []
        for i in image_bytes:
            flat_image.append(i >> 4)  # First nybble
            flat_image.append(i & 2**4-1)  # Last nybble
        image = cls()
        image.image = [flat_image[x : x + 16] for x in range(0, 256, 16)]
        return image

    def __bytes__(self):
        flat_image = sum(self.image, [])  # flatten the image into a 1-dimensional list
        image_bytearray = bytearray()
        for i in range(0, len(flat_image), 2):
            image_bytearray.append((flat_image[i] << 4) + flat_image[i+1])
        return bytes(image_bytearray)


    @classmethod
    def from_int(cls, image_int):
        return cls.from_bytes(image_int.to_bytes(128, byteorder="big"))

    def __int__(self):
        return int.from_bytes(bytes(self), byteorder="big")


    def fill(self, colour):
        """Fill the image with colour."""
        for y in range(self.height):
            for x in range(self.width):
                self.image[y][x] = colour

    def pretty_print(self):
        """Print image as text."""
        for row in self.image:
            print(" ".join([str(x).rjust(2) for x in row]))
        print()

    def set_pixel(self, x, y, colour):
        """Set the colour of a pixel."""
        self.assert_colour_is_valid(colour)
        self.image[y][x] = colour

    def assert_colour_is_valid(self, colour):
        """Ensure the colour falls within the range of the palette."""
        if not 0 <= colour < 16:
            raise ValueError(f"Colour must be between 0 and 15 (inclusive).")

