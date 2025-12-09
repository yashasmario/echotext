import pytesseract

raw_text = pytesseract.image_to_string("processed.jpg")
print(raw_text)
