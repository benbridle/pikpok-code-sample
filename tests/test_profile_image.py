import os
import sys

sys.path.append(os.getcwd())


from app.modules.profile_image import generate_profile_image, ProfileImage


def test_profile_image_conversions():
    # Test that the convertion methods on ProfileImage don't distort the image
    p1 = generate_profile_image()

    # Test bytes
    p2 = ProfileImage.from_bytes(bytes(p1))
    assert p1 == p2

    # Test base64
    p2 = ProfileImage.from_base64_string(p1.to_base64_string())
    assert p1 == p2

    # Test int
    p2 = ProfileImage.from_int(int(p1))
    assert p1 == p2
