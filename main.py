def main():
    capture image
    preprocess
    text = OCR
    product_name = extract_name(text)
    product_info = fetch_from_db(product_name)
    speak(product_info)

if __name__ == "__main__":
    main()
