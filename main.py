import cv2
import pytesseract
import pyttsx3
import requests
import re
from datetime import datetime
import numpy as np

class EchoText:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.current_frame = None
        
        # Initialize OpenCV barcode detector
        try:
            self.barcode_detector = cv2.barcode.BarcodeDetector()
            print("✅ OpenCV barcode detector initialized")
        except AttributeError:
            print("⚠️  Warning: OpenCV barcode module not available")
            print("Install with: pip install opencv-contrib-python")
            self.barcode_detector = None
        
    def speak(self, text):
        """Convert text to speech"""
        print(f"🔊 {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def detect_barcode_opencv(self, frame):
        """Detect barcode using OpenCV's built-in detector"""
        if not self.barcode_detector:
            return None
        
        try:
            # Detect and decode barcodes
            retval, decoded_info, decoded_type, points = self.barcode_detector.detectAndDecode(frame)
            
            if retval and decoded_info:
                results = []
                # Handle both single and multiple barcodes
                if isinstance(decoded_info, str):
                    decoded_info = [decoded_info]
                    decoded_type = [decoded_type]
                    points = [points]
                
                for info, btype, pts in zip(decoded_info, decoded_type, points):
                    if info:  # Only add if barcode data exists
                        results.append({
                            'data': info,
                            'type': btype,
                            'points': pts
                        })
                
                return results if results else None
            return None
            
        except Exception as e:
            print(f"Barcode detection error: {e}")
            return None
    
    def capture_with_preview(self):
        """Capture image with live preview and barcode detection overlay"""
        print("\n📷 Starting camera...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return None
        
        self.speak("Position barcode in center of frame. Press space to capture, or escape to exit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            display_frame = frame.copy()
            
            # Try to detect barcodes in real-time
            barcodes = self.detect_barcode_opencv(frame)
            
            if barcodes:
                for barcode in barcodes:
                    # Draw rectangle around barcode
                    pts = barcode['points']
                    if pts is not None and len(pts) > 0:
                        pts = pts.astype(np.int32)
                        cv2.polylines(display_frame, [pts], True, (0, 255, 0), 3)
                        
                        # Show barcode data
                        x, y = int(pts[0][0]), int(pts[0][1])
                        barcode_data = barcode['data']
                        cv2.putText(display_frame, f"FOUND: {barcode_data}", 
                                  (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Show instructions
            instructions = "SPACE: Capture | ESC: Exit"
            cv2.putText(display_frame, instructions, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('EchoText Scanner', display_frame)
            
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                cap.release()
                cv2.destroyAllWindows()
                return None
            elif key == 32:  # SPACE
                cv2.imwrite("capture.jpg", frame)
                self.current_frame = frame
                print("✅ Image captured!")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return frame
    
    def detect_barcode(self, image_path="capture.jpg"):
        """Detect and decode barcode from saved image"""
        if not self.barcode_detector:
            print("ℹ️  Barcode scanning not available")
            return None
            
        try:
            img = cv2.imread(image_path)
            barcodes = self.detect_barcode_opencv(img)
            
            if barcodes:
                for barcode in barcodes:
                    print(f"📊 Barcode detected: {barcode['data']} (Type: {barcode['type']})")
                return barcodes
            else:
                print("ℹ️  No barcode detected")
                return None
                
        except Exception as e:
            print(f"❌ Barcode detection error: {e}")
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
    
    def ocr_fallback(self, image_path="capture.jpg"):
        """Use OCR as fallback when barcode fails"""
        try:
            # Preprocess image
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Try multiple preprocessing approaches for better OCR
            # Method 1: Adaptive threshold
            thresh1 = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Method 2: Simple threshold with blur
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh2 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Save both versions
            cv2.imwrite("processed_adaptive.jpg", thresh1)
            cv2.imwrite("processed_otsu.jpg", thresh2)
            
            # Try OCR on both and combine results
            text1 = pytesseract.image_to_string(thresh1)
            text2 = pytesseract.image_to_string(thresh2)
            text3 = pytesseract.image_to_string(gray)  # Original grayscale
            
            # Use the longest result (usually more accurate)
            raw_text = max([text1, text2, text3], key=len)
            
            print(f"\n📄 OCR Text Extracted:\n{raw_text}\n")
            
            # Parse product name (usually first significant line)
            lines = [l.strip() for l in raw_text.split("\n") if len(l.strip()) > 3]
            product_name = lines[0] if lines else "Unknown Product"
            
            return {
                'source': 'OCR',
                'product_name': product_name,
                'raw_text': raw_text
            }
            
        except Exception as e:
            print(f"❌ OCR error: {e}")
            return None
    
    def search_product_by_name(self, product_name):
        """Search OpenFoodFacts by product name"""
        try:
            url = f"https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                'search_terms': product_name,
                'search_simple': 1,
                'action': 'process',
                'json': 1,
                'page_size': 3
            }
            
            print(f"🔍 Searching for: {product_name}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                if products:
                    # Return first result
                    product = products[0]
                    info = {
                        'source': 'OpenFoodFacts Search',
                        'found': True,
                        'product_name': product.get('product_name', 'Unknown'),
                        'brands': product.get('brands', 'Unknown'),
                        'categories': product.get('categories', ''),
                        'nutrition_grade': product.get('nutrition_grades', 'Not available'),
                        'nutriments': product.get('nutriments', {})
                    }
                    print(f"✅ Found match: {info['product_name']}")
                    return info
                    
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        return None
    
    def extract_expiry_date_from_ocr(self, text):
        """Extract expiry date from OCR text"""
        patterns = [
            r'(?:exp|expiry|best before|use by)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:exp|expiry|best before|use by)[:\s]*(\d{2}\s*[A-Z]{3}\s*\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
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
        print("🎯 EchoText - Accessible Product Reader")
        print("="*50)
        
        if not self.barcode_detector:
            print("\n⚠️  WARNING: Barcode detection not available!")
            print("Install with: pip install opencv-contrib-python")
            print("Continuing in OCR-only mode...\n")
        
        self.speak("Welcome to Echo Text")
        
        # Step 1: Capture image
        frame = self.capture_with_preview()
        if frame is None:
            self.speak("Capture cancelled")
            return
        
        self.speak("Processing image")
        
        # Step 2: Try barcode detection first (MOST RELIABLE)
        barcodes = self.detect_barcode()
        
        product_info = None
        
        if barcodes:
            # Use first barcode found
            barcode_data = barcodes[0]['data']
            self.speak(f"Barcode detected")
            
            # Step 3: Look up product in database
            product_info = self.lookup_product_by_barcode(barcode_data)
            
            if product_info and product_info.get('found'):
                # Success! We have reliable database info
                self.speak(f"Product found: {product_info['product_name']} by {product_info['brands']}")
                
                # Categories
                if product_info.get('categories'):
                    categories = product_info['categories'].split(',')[0]  # First category
                    self.speak(f"Category: {categories}")
                
                # Nutrition grade
                if product_info.get('nutrition_grade') and product_info['nutrition_grade'] != 'Not available':
                    self.speak(f"Nutrition grade: {product_info['nutrition_grade']}")
                
                # Nutrition info
                nutrition_messages = self.format_nutrition_info(product_info.get('nutriments', {}))
                if nutrition_messages:
                    self.speak("Nutrition information per 100 grams:")
                    for msg in nutrition_messages[:4]:  # Limit to top 4 nutrients
                        self.speak(msg)
                
                # Allergens
                if product_info.get('allergens'):
                    allergens = product_info['allergens'].replace('en:', '').replace('-', ' ')
                    self.speak(f"Allergens: {allergens}")
            else:
                self.speak("Product not found in database. Trying OCR fallback")
                product_info = None
        else:
            self.speak("No barcode detected. Using OCR")
        
        # Step 4: OCR Fallback (if barcode failed or not found)
        if not product_info or not product_info.get('found'):
            self.speak("Reading product label with OCR")
            ocr_result = self.ocr_fallback()
            
            if ocr_result:
                product_name = ocr_result['product_name']
                self.speak(f"Product detected: {product_name}")
                
                # Try to search by name
                search_result = self.search_product_by_name(product_name)
                
                if search_result and search_result.get('found'):
                    self.speak(f"Found in database: {search_result['product_name']} by {search_result['brands']}")
                    
                    if search_result.get('nutrition_grade') and search_result['nutrition_grade'] != 'Not available':
                        self.speak(f"Nutrition grade: {search_result['nutrition_grade']}")
                    
                    # Nutrition info
                    nutrition_messages = self.format_nutrition_info(search_result.get('nutriments', {}))
                    if nutrition_messages:
                        self.speak("Nutrition information:")
                        for msg in nutrition_messages[:3]:
                            self.speak(msg)
                else:
                    self.speak("Could not find product in database")
                
                # Try to extract expiry date from OCR
                expiry = self.extract_expiry_date_from_ocr(ocr_result['raw_text'])
                if expiry:
                    self.speak(f"Expiry date found: {expiry}")
                else:
                    self.speak("No expiry date detected in visible text")
        
        print("\n" + "="*50)
        print("✅ Processing Complete")
        print("="*50)
        self.speak("Scan complete")

if __name__ == "__main__":
    app = EchoText()
    app.run()
