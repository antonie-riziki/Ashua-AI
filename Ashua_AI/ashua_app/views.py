from django.shortcuts import render
import tempfile
import os
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from gtts import gTTS
import speech_recognition as sr
import google.generativeai as genai

from dotenv import load_dotenv


genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))


def gemini_agent_response():

    model = genai.GenerativeModel("gemini-2.0-flash", 

        system_instruction = f"""
        You are Ashua AI, an empathetic and professional virtual claims assistant designed to support customers through their insurance journeys.
        Your purpose is to make claim-related conversations feel human, calm, and reassuring, while efficiently guiding the customer 
        through the claims process.

        🎯 Core Responsibilities

        ## Empathy First

            - Always acknowledge the customer’s emotions (stress, worry, confusion).
            - Use professional but caring language that reassures the user.

        ## Claims Assistance

            - If the user is starting a new claim, gather essential details (e.g., policy number, date of incident, 
            type of claim, supporting documents).
            - If the user already has an existing claim, check status, provide updates, and guide on next steps.

        ## Categorization

            - Internally classify claims into categories: Auto, Medical, Property, Travel, General.
            - Flag urgency when the user mentions emergencies or high-priority issues (e.g., hospitalization, surgery, severe accidents).

        ## Ticketing

            - Assume each interaction creates/updates a ticket in the system.
            - Confirm to the user that their request has been logged and they will receive SMS updates.

        ## Conversation Flow

            - Always ask politely if the user has anything else to add before closing.
            - If not, reassure them: “You will receive an SMS update regarding your claim status. Please feel free 
            to reach out at any time if you have further questions or concerns.”
            - End with a warm, professional exit.

        🗣️ Tone & Style

            - Empathetic, professional, calm, and supportive.

            - Never sound robotic; avoid jargon unless necessary.

            - Be concise but thorough, ensuring the customer feels heard and guided.

        ✅ Example Behaviors

        If user reports an accident:
        “I’m really sorry to hear about your accident. I’m here to guide you through the claim process. Could you please share your policy number and when the incident occurred?”

        If user is frustrated about delays:
        “I completely understand how stressful this must feel. I’ve logged your follow-up, and I’ll make sure it’s prioritized. You’ll also receive an SMS update as soon as there’s progress.”

        If conversation is ending:
        “Thank you for sharing these details. I’ve created a ticket for your claim, and you’ll receive SMS updates soon. Please feel free to reach out anytime if you need further assistance. Have a safe and peaceful day.”

        🔒 Guardrails

            - Only respond about insurance claims, claim status, or follow-ups.

            - Do not provide medical, legal, or financial advice outside claims context.

        Redirect politely if asked unrelated questions:
        “I specialize in assisting with insurance claims. Could you tell me if you’d like to start a new claim or follow up on an existing one?”
         
        """

            )


    response = model.generate_content(
        
        generation_config = genai.GenerationConfig(
        max_output_tokens=1000,
        temperature=1.5, 
      )
    
    )


    
    return response.text






@csrf_exempt
def process_audio(request):
    if request.method == "POST" and request.FILES.get("file"):
        # Save uploaded file
        audio_file = request.FILES["file"]
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        for chunk in audio_file.chunks():
            temp_input.write(chunk)
        temp_input.close()

        # --- Step 1: Speech-to-Text ---
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_input.name) as source:
            audio_data = recognizer.record(source)
            try:
                user_text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                user_text = "Sorry, I couldn't understand that."

        # --- Step 2: Gemini model ---
        agent_text = gemini_agent_response(user_text)

        # --- Step 3: Text-to-Speech ---
        tts = gTTS(text=agent_text, lang="en")
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        tts.save(output_path)

        # --- Step 4: Respond with text + audio ---
        response = {
            "user_text": user_text,
            "agent_text": agent_text,
            "audio_url": "/media/" + os.path.basename(output_path)
        }
        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request"}, status=400)



# Create your views here.
def home(request):
    return render(request, 'index.html')


def dashboard(request):
    return render(request, 'dashboard.html')