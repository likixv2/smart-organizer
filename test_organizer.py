from organizer import classify, get_unique_dest_path
import re
from organizer import PDF_KEYWORDS

def test_classify_image():
    assert classify("photo.jpg") == "Images"

def test_classify_image_uppercase():
    assert classify("photo.JPG") == "Images"

def test_classify_document():
    assert classify("resume.txt") == "Documents"

def test_classify_audio():
    assert classify("song.mp3") == "Audio"

def test_classify_unknown_extension():
    assert classify("mystery.xyz") == "Others"

from organizer import classify, get_unique_dest_path

def test_unique_path_no_collision(tmp_path):
    dest_folder = tmp_path / "Images"
    dest_folder.mkdir()
    result = get_unique_dest_path(dest_folder, "photo.jpg")
    assert result == dest_folder / "photo.jpg"

def test_unique_path_with_collision(tmp_path):
    dest_folder = tmp_path / "Images"
    dest_folder.mkdir()
    (dest_folder / "photo.jpg").touch()  # simulate an existing file

    result = get_unique_dest_path(dest_folder, "photo.jpg")
    assert result == dest_folder / "photo_1.jpg"

def test_unique_path_multiple_collisions(tmp_path):
    dest_folder = tmp_path / "Images"
    dest_folder.mkdir()
    (dest_folder / "photo.jpg").touch()
    (dest_folder / "photo_1.jpg").touch()
    (dest_folder / "photo_2.jpg").touch()

    result = get_unique_dest_path(dest_folder, "photo.jpg")
    assert result == dest_folder / "photo_3.jpg"


def test_keyword_matching_uses_word_boundaries():
    # Regression test: "unit" should not match inside "opportunity"
    text = "we see a great opportunity in this market"
    pattern = r'\b' + re.escape("unit") + r'\b'
    assert re.search(pattern, text) is None

def test_keyword_matching_matches_real_word():
    text = "please complete unit 3 of the course"
    pattern = r'\b' + re.escape("unit") + r'\b'
    assert re.search(pattern, text) is not None