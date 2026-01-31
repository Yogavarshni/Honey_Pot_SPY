import google.generativeai as genai
genai.configure(api_key="AIzaSyBQwcyTwfmw1Oem9PA-tJBtH90QFCuzwpI")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)