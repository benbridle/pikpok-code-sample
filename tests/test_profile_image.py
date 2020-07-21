import os
import sys

sys.path.append(os.getcwd())


from app.modules.profile_image import generate_profile_image, ProfileImage


def test_profile_image_serialisation():
    """Test that the serialisation methods on ProfileImage don't change the image."""
    p1 = generate_profile_image()

    # Test bytes serialisation
    p2 = ProfileImage.from_bytes(bytes(p1))
    assert p1 == p2

    # Test base64 serialisation
    p2 = ProfileImage.from_base64_string(p1.to_base64_string())
    assert p1 == p2

    # Test int serialisation
    p2 = ProfileImage.from_int(int(p1))
    assert p1 == p2
