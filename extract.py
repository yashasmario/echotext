lines = [l.strip() for l in raw_text.split("\n") if len(l.strip()) > 2]
product_guess = lines[0]
print("Product:", product_guess)
