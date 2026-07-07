import os
import logging
import base64
from django.shortcuts import render
from .models import MarketPrice, GovernmentScheme

try:
    from google import genai
    from google.genai import types
    gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
except Exception as e:
    logging.warning(f"Could not configure Gemini API: {e}")
    gemini_client = None

def home(request):
    return render(request, 'home.html')

def assistant(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    if request.method == 'POST':
        user_msg = request.POST.get('message', '').strip()
        if 'reset' in request.POST:
            request.session['chat_history'] = []
        elif user_msg:
            if gemini_client and os.environ.get("GEMINI_API_KEY") not in [None, "", "YOUR_API_KEY_HERE"]:
                try:
                    system_prefix = "You are an intelligent agricultural assistant designed to help farmers in Tamil Nadu. You support both Tamil and English. Always respond fully in the same language the farmer uses. Keep it simple and practical. End your response with: 'For more help, contact your nearest Krishi Vigyan Kendra (KVK).'\n\nFarmer Query: "
                    response = gemini_client.models.generate_content(
                        model='gemini-flash-latest',
                        contents=system_prefix + user_msg
                    )
                    formatted_text = response.text.replace('\n', '<br>')
                    ai_msg = f"🤖 <strong>AgriAssist:</strong><br>{formatted_text}"
                except Exception as e:
                    ai_msg = f"🤖 <strong>AgriAssist (Error):</strong> The AI service is currently unavailable. Ensure your API key is correct and you have an active network connection. ({e})"
            else:
                ai_msg = "🤖 <strong>AgriAssist (Offline):</strong> Live AI integration is pending. Please paste your Gemini API Key into the `.env` file located in the project root and restart the server to enable dynamic AI responses."
            
            request.session['chat_history'].append({'sender': 'farmer', 'text': user_msg})
            request.session['chat_history'].append({'sender': 'ai', 'text': ai_msg})
            request.session.modified = True

    return render(request, 'assistant.html', {'chat_history': request.session.get('chat_history', [])})

def tools(request):
    recommendation = None
    upload_msg = None
    yield_prediction = None

    if request.method == 'POST':
        if 'recommend' in request.POST:
            loc = request.POST.get('location')
            month = request.POST.get('month')
            recommendation = f"Recommendation for {loc} in {month}: Plant Cotton or Maize. Soil requirements: Well-drained black or red soil."
        elif 'upload' in request.FILES:
            uploaded_file = request.FILES['upload']
            if gemini_client and os.environ.get("GEMINI_API_KEY") not in [None, "", "YOUR_API_KEY_HERE"]:
                try:
                    mime_type = uploaded_file.content_type
                    if not mime_type.startswith('image/'):
                        upload_msg = "❌ Invalid file. Please upload an image."
                    else:
                        img_bytes = uploaded_file.read()
                        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                        filename = uploaded_file.name
                        prompt = f"You are an expert agricultural botanist. Analyze the uploaded image named '{filename}'. First, briefly describe exactly what you see in the image to prove you are looking at it. Then, identify the crop, any diseases, and provide detailed treatments in English and Tamil."
                        
                        response = gemini_client.models.generate_content(
                            model='gemini-flash-latest',
                            contents=[
                                prompt,
                                types.Part.from_bytes(data=img_b64, mime_type=mime_type)
                            ]
                        )
                        formatted_text = response.text.replace('\n', '<br>')
                        upload_msg = f"📸 <strong>Analysis for {filename}:</strong><br>{formatted_text}"
                except Exception as e:
                    upload_msg = f"❌ <strong>Analysis Failed:</strong> Error communicating with AI Vision model. ({e})"
            else:
                upload_msg = "📸 <strong>AI Vision Offline:</strong> Please configure your Gemini API Key in `.env` to enable true image analysis."
        elif 'predict_yield' in request.POST:
            try:
                n = float(request.POST.get('n', 0))
                p = float(request.POST.get('p', 0))
                k = float(request.POST.get('k', 0))
                ph = float(request.POST.get('ph', 7))
                
                base_yield = 2000
                n_factor = (n / 100.0) * 500
                p_factor = (p / 50.0) * 300
                k_factor = (k / 50.0) * 300
                ph_penalty = abs(6.5 - ph) * 200
                
                calculated = max(0, base_yield + n_factor + p_factor + k_factor - ph_penalty)
                yield_prediction = f"📊 Predicted Yield: {calculated:.1f} kg per acre based on given soil parameters."
            except Exception as e:
                yield_prediction = "Error calculating prediction. Ensure all fields are numbers."

    return render(request, 'tools.html', {
        'recommendation': recommendation, 
        'upload_msg': upload_msg,
        'yield_prediction': yield_prediction
    })

def info(request):
    prices = MarketPrice.objects.all()
    schemes = GovernmentScheme.objects.all()
    return render(request, 'info.html', {'prices': prices, 'schemes': schemes})
