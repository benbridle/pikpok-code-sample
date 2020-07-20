import base64
from PIL import Image

image_length = 16
palette_size = 16
default_palette = {
    0: (232, 0, 0),  # red
    1: (231, 151, 0),  # orange
    2: (230, 219, 0),  # yellow
    3: (146, 226, 51),  # lightgreen
    4: (0, 192, 0),  # green
    5: (1, 229, 242),  # cyan
    6: (0, 130, 202),  # midblue
    7: (6, 0, 238),  # blue
    8: (255, 166, 209),  # lightpink
    9: (226, 62, 255),  # pink
    10: (130, 2, 129),  # purple
    11: (255, 255, 255),  # white
    12: (228, 228, 228),  # lightgrey
    13: (136, 135, 137),  # grey
    14: (34, 34, 34),  # darkgrey
    15: (161, 106, 63),  # brown
}


class ProfileImage:
    """A square pixel-art image for use as a profile picture. Each pixel is
    represented by an int, which references a colour on a palette."""

    def __init__(self):
        self.width = image_length
        self.height = image_length
        self.palette_size = palette_size
        self.image = []
        for _ in range(self.height):
            self.image.append([0] * self.width)

    @classmethod
    def from_base64_string(cls, base64_string):
        image_bytes = base64.b64decode(base64_string.encode("utf-8"))
        return cls.from_bytes(image_bytes)

    def to_base64_string(self):
        return base64.b64encode(bytes(self)).decode("utf-8")

    @classmethod
    def from_bytes(cls, image_bytes):
        flat_image = []
        for i in image_bytes:
            flat_image.append(i >> 4)  # First nybble
            flat_image.append(i & 2 ** 4 - 1)  # Last nybble
        image = cls()
        image.image = [flat_image[i : i + 16] for i in range(0, 256, 16)]
        return image

    def __bytes__(self):
        flat_image = sum(self.image, [])  # flatten the image into a 1-dimensional list
        image_bytearray = bytearray()
        for i in range(0, len(flat_image), 2):
            image_bytearray.append((flat_image[i] << 4) + flat_image[i + 1])
        return bytes(image_bytearray)

    @classmethod
    def from_int(cls, image_int):
        return cls.from_bytes(image_int.to_bytes(128, byteorder="big"))

    def __int__(self):
        return int.from_bytes(bytes(self), byteorder="big")


    def to_PIL_image(self, palette=default_palette):
        """
        Converts to a PIL Image, so that the image can be saved in a standard image format.
        :palette: takes a dictionary that maps the numbers 0..15 to an (r,g,b) tuple
        """
        flat_image = sum(self.image, [])  # flattens list
        colour_data = [palette[colour_index] for colour_index in flat_image]
        pil_image = Image.new("RGB", (self.width, self.height))
        pil_image.putdata(colour_data)
        return pil_image

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

    def __str__(self):
        image_str = ""
        for row in self.image:
            image_str += " ".join([str(x).rjust(2) for x in row]) + "\n"
        return image_str

    def set_pixel(self, x, y, colour):
        """Set the colour of a pixel."""
        self.assert_colour_is_valid(colour)
        self.image[y][x] = colour

    def assert_colour_is_valid(self, colour):
        """Ensure the colour falls within the range of the palette."""
        if not 0 <= colour < 16:
            raise ValueError(f"Colour must be between 0 and 15 (inclusive).")

    def apply_image_as_mask(self, mask_image_file_path, colour_index):
        """Takes a .png file, converts it to black and white, scales it to the
        size of the PixelImage, and imposes itself onto the PixelImage as the
        chosen colour."""
        mask_image = Image.open(mask_image_file_path).convert("RGBA")

        # Change high alpha pixels to black, in case the mask is via the alpha channel
        # If the alpha value of a pixel renders it to be more than half transparent,
        # make that pixel black. This ensures that an image using an alpha mask can
        # now be used as a value mask (monochrome).
        black = (0, 0, 0, 255)
        alpha_channel = 3
        mask_data = mask_image.getdata()
        mask_data = [black if pixel[alpha_channel] < 128 else pixel for pixel in mask_data]
        mask_image.putdata(mask_data)

        # Convert mask to greyscale
        mask_image = mask_image.convert("L")
        # Scale mask to size of ProfileImage
        mask_image = mask_image.resize((self.width, self.height), Image.NEAREST)
        # Convert PIL Image to a 2-dimensional list
        mask = list(mask_image.getdata())
        mask_2d = [mask[i : i + self.width] for i in range(0, 256, self.width)]

        # Apply mask to ProfileImage
        for y, row in enumerate(mask_2d):
            for x, value in enumerate(row):
                if value > 128:  # if brighter than mid-grey
                    self.set_pixel(x, y, colour_index)
