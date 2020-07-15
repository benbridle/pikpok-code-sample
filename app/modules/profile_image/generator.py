from .profile_image import ProfileImage
import glob
import random
import os

module_path = os.path.dirname(os.path.realpath(__file__))
icon_paths = glob.glob(module_path + "/image_components/icons/*.png")
border_paths = glob.glob(module_path + "/image_components/borders/*.png")

background_colours = [10, 14, 7]
midground_colours = [9, 15, 13, 4, 6, 0]
foreground_colours = [1, 2, 3, 5, 8, 11, 12]

def generate_profile_image():
    """Generate a random profile image."""
    profile_image = ProfileImage()
    profile_image.fill(random.choice(background_colours))
    border_path = random.choice(border_paths)
    icon_path = random.choice(icon_paths)
    profile_image.apply_image_as_mask(border_path, random.choice(midground_colours))
    profile_image.apply_image_as_mask(icon_path, random.choice(foreground_colours))
    return profile_image
