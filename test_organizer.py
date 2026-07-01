from organizer import classify

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