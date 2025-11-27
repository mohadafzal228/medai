import google.generativeai as genai
from app.core.config import settings
import logging
import asyncio
from typing import List, Dict
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)

# Fixed: Validate API key before configuration
if not settings.GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY is not set")
    # Don't raise here to avoid crashing app on startup if key is missing, 
    # but chat won't work.
else:
    genai.configure(api_key=settings.GOOGLE_API_KEY)

SYSTEM_PROMPT = """
You are Med AI, a highly advanced and professional Medical AI Assistant.
Your primary goal is to provide accurate, evidence-based medical information to users.

STRICT RULES:
1. "No-Chat" Policy: You must STRICTLY REFUSE to answer any non-medical queries.
   - If a user asks "Who is the President?", "Write code", or "Tell me a joke", reply with:
     "I am Med AI, a specialized medical assistant. I can only assist with health and medical-related inquiries."
2. Verified Consensus: Do NOT hallucinate cures or treatments.
   - Base your answers ONLY on globally accepted medical standards (W.H.O., CDC, NIH, Standard Medical Textbooks).
   - If a condition is serious, ALWAYS advise the user to consult a real doctor.
3. Structured Output: You MUST format your response in Markdown.
   - Use **Bold** for symptoms or key terms.
   - Use Lists (bullet points or numbered) for steps, advice, or symptoms.
   - Use ### Headers for sections (e.g., ### Symptoms, ### Treatment, ### When to see a doctor).
4. References: You MUST include a "References" section at the end of every medical response.
   - Cite verified sources such as W.H.O., CDC, NIH, or standard medical textbooks.
   - Provide links if available, or book titles/authors.
5. Tone: Maintain a Clinical, Professional, and Empathetic tone.
   - Be concise but thorough.
   - Avoid slang or overly casual language.

Example Interaction:
User: "I have a headache and fever."
Med AI:
### Potential Causes
Based on your symptoms, this could be:
*   **Common Cold**: Viral infection.
*   **Flu (Influenza)**: Sudden onset of fever and body aches.
*   **Tension Headache**: Stress-related.

### Recommendations
1.  **Rest**: Get plenty of sleep.
2.  **Hydration**: Drink water.
3.  **Medication**: Over-the-counter pain relievers (e.g., Paracetamol) if appropriate.

> **Note**: If symptoms persist or worsen, please consult a healthcare professional immediately.

### References
*   World Health Organization (WHO) - Headache Disorders
*   CDC - Influenza (Flu)
"""

# Fixed: Initialize model with error handling
model = None
try:
    if settings.GOOGLE_API_KEY:
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 2048,
            },
            system_instruction=SYSTEM_PROMPT
        )
        logger.info("Gemini model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {str(e)}")

async def generate_medical_response(chat_history: List[Dict], user_message: str) -> str:
    """
    Generate medical response from Gemini API with retry logic.
    """
    if not model:
        return "I apologize, but the AI service is not currently configured. Please contact the administrator."

    # Fixed: Validate inputs
    if not user_message or not user_message.strip():
        raise ValueError("User message cannot be empty")
    
    # Convert chat history to Gemini format
    history_gemini = []
    for msg in chat_history:
        role = "user" if msg.get("role") == "user" else "model"
        content = msg.get("content", "")
        if content:  # Only add non-empty messages
            history_gemini.append({"role": role, "parts": [content]})
    
    # Fixed: Add safety check for history length
    if len(history_gemini) > 100:  # Limit history to prevent token overflow
        logger.warning("Chat history too long, truncating to last 100 messages")
        history_gemini = history_gemini[-100:]
    
    # Retry configuration
    max_retries = 3
    base_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            # Start chat with history
            chat = model.start_chat(history=history_gemini)
            
            # Send message asynchronously
            response = await asyncio.to_thread(
                chat.send_message,
                user_message
            )
            
            # Fixed: Validate response
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            logger.info("Successfully generated Gemini response")
            return response.text
            
        except google_exceptions.ResourceExhausted as e:
            # Rate limit error
            logger.error(f"Gemini API rate limit exceeded: {str(e)}")
            return (
                "I apologize, but the service is currently experiencing high demand. "
                "Please try again in a few moments."
            )
            
        except google_exceptions.InvalidArgument as e:
            # Invalid request error - don't retry
            logger.error(f"Invalid request to Gemini API: {str(e)}")
            return (
                "I apologize, but I couldn't process your request. "
                "Please try rephrasing your question."
            )
            
        except Exception as e:
            logger.warning(f"Gemini API attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                delay = base_delay * (2 ** attempt)
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                # All retries exhausted
                logger.error(f"Gemini API failed after {max_retries} attempts: {str(e)}")
                return (
                    "I apologize, but I am unable to process your request at the moment due to a technical issue. "
                    "Please try again in a few moments. If the problem persists, please contact support."
                )