import cv2
import pytesseract
import pyttsx3
import requests
import re
from datetime import datetime
import os

# Fix for Mac - help pyzbar find zbar library
if os.uname().sysname == 'Darwin':  # macOS
    os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib:/usr/local/lib'

from pyzbar import pyzbar

class EchoText:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.scanned_barcodes = set()  # Track already scanned barcodes
        
    def speak(self, text):
        """Convert text to speech"""
        print(f"🔊 {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def live_barcode_scan(self):
        """Continuously scan for barcodes until one is found and processed"""
        print("\n📷 Starting live barcode scanner...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return None
        
        self.speak("Show me the barcode. Scanning live.")
        
        found_barcode = None
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            display_frame = frame.copy()
            frame_count += 1
            
            # Scan for barcodes every frame
            barcodes = pyzbar.decode(frame)
            
            if barcodes:
                for barcode in barcodes:
                    # Draw rectangle around barcode
                    points = barcode.polygon
                    if len(points) == 4:
                        pts = [(point.x, point.y) for point in points]
                        for i in range(4):
                            pt1 = pts[i]
                            pt2 = pts[(i+1) % 4]
                            cv2.line(display_frame, pt1, pt2, (0, 255, 0), 3)
                    
                    # Get barcode data
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    
                    # Display on screen
                    x, y, w, h = barcode.rect
                    cv2.putText(display_frame, f"DETECTED: {barcode_data}", 
                              (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(display_frame, f"Type: {barcode_type}", 
                              (x, y+h+25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # If this is a new barcode we haven't scanned yet
                    if barcode_data not in self.scanned_barcodes:
                        print(f"📊 NEW Barcode detected: {barcode_data} (Type: {barcode_type})")
                        self.scanned_barcodes.add(barcode_data)
                        found_barcode = {
                            'data': barcode_data,
                            'type': barcode_type
                        }
                        # Wait a moment to show the detection, then process
                        cv2.imshow('EchoText - Live Scanner', display_frame)
                        cv2.waitKey(1000)  # Show detection for 1 second
                        break
            
            # Show instructions
            instructions = "Hold barcode steady | ESC: Exit | C: Capture front label"
            cv2.putText(display_frame, instructions, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show scanning indicator
            if frame_count % 20 < 10:
                cv2.circle(display_frame, (30, 60), 10, (0, 255, 0), -1)
                cv2.putText(display_frame, "SCANNING...", (50, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imshow('EchoText - Live Scanner', display_frame)
            
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                cap.release()
                cv2.destroyAllWindows()
                return None
            elif key == ord('c') or key == ord('C'):
                # Capture front label for OCR
                cv2.imwrite("front_label.jpg", frame)
                print("✅ Front label captured for OCR")
                self.speak("Front label captured")
                # Continue scanning for barcode
            
            # If we found a barcode, break the loop
            if found_barcode:
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        return found_barcode
    
    def capture_front_label(self):
        """Capture front label separately for product name/brand"""
        print("\n📷 Capture front label for product name...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return None
        
        self.speak("Show me the front label with product name. Press space to capture")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            display_frame = frame.copy()
            
            # Show instructions
            cv2.putText(display_frame, "SPACE: Capture front label | ESC: Skip", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('EchoText - Capture Front Label', display_frame)
            
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                cap.release()
                cv2.destroyAllWindows()
                return None
            elif key == 32:  # SPACE
                cv2.imwrite("front_label.jpg", frame)
                print("✅ Front label captured!")
                cap.release()
                cv2.destroyAllWindows()
                return frame
        
        cap.release()
        cv2.destroyAllWindows()
        return None
    
    def lookup_product_by_barcode(self, barcode_data):
        """Fetch product info from OpenFoodFacts database"""
        try:
            url = f"https://world.openfoodfacts.org/api/v2/product/{barcode_data}"
            print(f"🔍 Searching database for barcode: {barcode_data}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 1:
                    product = data.get('product', {})
                    
                    # Extract key information
                    info = {
                        'source': 'OpenFoodFacts',
                        'found': True,
                        'product_name': product.get('product_name', 'Unknown'),
                        'brands': product.get('brands', 'Unknown'),
                        'categories': product.get('categories', ''),
                        'ingredients_text': product.get('ingredients_text', ''),
                        'allergens': product.get('allergens', ''),
                        'nutrition_grade': product.get('nutrition_grades', 'Not available'),
                        'nutriments': product.get('nutriments', {}),
                        'serving_size': product.get('serving_size', ''),
                        'image_url': product.get('image_url', '')
                    }
                    
                    print(f"✅ Product found: {info['product_name']} - {info['brands']}")
                    return info
                else:
                    print("ℹ️  Product not found in database")
                    return {'source': 'OpenFoodFacts', 'found': False}
            else:
                print(f"❌ API request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Database lookup error: {e}")
            return None
    
    def ocr_front_label(self, image_path="front_label.jpg"):
        """Use OCR on front label to get product name/brand"""
        try:
            if not os.path.exists(image_path):
                print("ℹ️  No front label image found")
                return None
            
            print("📄 Reading front label with OCR...")
            
            # Preprocess image
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Try multiple preprocessing methods
            thresh1 = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh2 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Try OCR on different versions
            text1 = pytesseract.image_to_string(thresh1)
            text2 = pytesseract.image_to_string(thresh2)
            text3 = pytesseract.image_to_string(gray)
            
            # Use longest result
            raw_text = max([text1, text2, text3], key=len)
            
            print(f"\n📄 OCR Text from Front Label:\n{raw_text}\n")
            
            # Parse product name and brand
            lines = [l.strip() for l in raw_text.split("\n") if len(l.strip()) > 2]
            product_name = lines[0] if lines else "Unknown Product"
            brand = lines[1] if len(lines) > 1 else ""
            
            return {
                'product_name': product_name,
                'brand': brand,
                'raw_text': raw_text
            }
            
        except Exception as e:
            print(f"❌ OCR error: {e}")
            return None
    
    def format_nutrition_info(self, nutriments):
        """Format nutrition information for speech"""
        messages = []
        
        if nutriments:
            # Key nutrients
            if 'energy-kcal_100g' in nutriments:
                calories = nutriments['energy-kcal_100g']
                messages.append(f"Calories: {calories} per 100 grams")
            
            if 'proteins_100g' in nutriments:
                protein = nutriments['proteins_100g']
                messages.append(f"Protein: {protein} grams per 100 grams")
            
            if 'fat_100g' in nutriments:
                fat = nutriments['fat_100g']
                messages.append(f"Fat: {fat} grams per 100 grams")
            
            if 'carbohydrates_100g' in nutriments:
                carbs = nutriments['carbohydrates_100g']
                messages.append(f"Carbohydrates: {carbs} grams per 100 grams")
            
            if 'sugars_100g' in nutriments:
                sugars = nutriments['sugars_100g']
                messages.append(f"Sugars: {sugars} grams per 100 grams")
        
        return messages
    
    def run(self):
        """Main execution flow"""
        print("\n" + "="*50)
        print("🎯 EchoText - Live Product Scanner")
        print("="*50)
        
        self.speak("Welcome to Echo Text. Live barcode scanner ready.")
        
        # Step 1: Live scan for barcode
        barcode = self.live_barcode_scan()
        
        if barcode is None:
            self.speak("Scan cancelled")
            return
        
        barcode_data = barcode['data']
        self.speak(f"Barcode scanned successfully")
        
        # Step 2: Look up product in database
        product_info = self.lookup_product_by_barcode(barcode_data)
        
        if product_info and product_info.get('found'):
            # Success! We have database info
            self.speak(f"Product identified: {product_info['product_name']} by {product_info['brands']}")
            
            # Categories
            if product_info.get('categories'):
                categories = product_info['categories'].split(',')[0]
                self.speak(f"Category: {categories}")
            
            # Nutrition grade
            if product_info.get('nutrition_grade') and product_info['nutrition_grade'] != 'Not available':
                self.speak(f"Nutrition grade: {product_info['nutrition_grade']}")
            
            # Nutrition info
            nutrition_messages = self.format_nutrition_info(product_info.get('nutriments', {}))
            if nutrition_messages:
                self.speak("Nutrition information per 100 grams:")
                for msg in nutrition_messages[:4]:
                    self.speak(msg)
            
            # Allergens
            if product_info.get('allergens'):
                allergens = product_info['allergens'].replace('en:', '').replace('-', ' ')
                self.speak(f"Contains allergens: {allergens}")
        
        else:
            # Database lookup failed, need to use front label OCR
            self.speak("Product not in database. Please show front label for product name")
            
            # Capture front label
            front_frame = self.capture_front_label()
            
            if front_frame:
                # Run OCR on front label
                ocr_result = self.ocr_front_label()
                
                if ocr_result:
                    product_name = ocr_result['product_name']
                    brand = ocr_result['brand']
                    
                    self.speak(f"Product name: {product_name}")
                    if brand:
                        self.speak(f"Brand: {brand}")
                    
                    self.speak("This product is not in our database. Please check the label for detailed information")
            else:
                self.speak("No front label captured. Unable to identify product")
        
        print("\n" + "="*50)
        print("✅ Scan Complete")
        print("="*50)
        self.speak("Scan complete")

if __name__ == "__main__":
    app = EchoText()
    app.run()
