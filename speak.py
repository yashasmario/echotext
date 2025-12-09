import pyttsx3

engine = pyttsx3.init()
engine.say("Product name detected: " + product_guess)
engine.say("Here is the information...")
engine.say(info_string)
engine.runAndWait()
