"""
AI Tasks Module
Handles AI generation tasks (text, images, vision, etc.)
Replaces worker.tasks AI functions after Celery removal
"""

import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_ai_response(
    prompt: str,
    model: str = "gpt-4o",
    user_id: Optional[int] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate AI text response using selected model
    
    Args:
        prompt: User's input prompt
        model: AI model to use (gpt-4o, claude, gemini, ollama)
        user_id: Telegram user ID for logging
        context: Optional conversation context
    
    Returns:
        Dict with response text and metadata
    """
    try:
        logger.info(f"Generating AI response for user {user_id} with model {model}")
        
        # Model-specific implementations
        if model.startswith("gpt"):
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": context or "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": model,
                "tokens": response.usage.total_tokens
            }
        
        elif model.startswith("claude"):
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            response = await client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "success": True,
                "response": response.content[0].text,
                "model": model,
                "tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        
        elif model.startswith("gemini"):
            import google.generativeai as genai
            genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
            model_instance = genai.GenerativeModel(model)
            
            response = await model_instance.generate_content_async(prompt)
            
            return {
                "success": True,
                "response": response.text,
                "model": model,
                "tokens": None
            }
        
        elif model.startswith("ollama"):
            from ollama import AsyncClient
            client = AsyncClient(host=settings.OLLAMA_BASE_URL)
            
            response = await client.chat(
                model=model.replace("ollama-", ""),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "success": True,
                "response": response['message']['content'],
                "model": model,
                "tokens": None
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown model: {model}"
            }
    
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def generate_image(
    prompt: str,
    model: str = "dall-e-3",
    user_id: Optional[int] = None,
    size: str = "1024x1024",
    quality: str = "standard"
) -> Dict[str, Any]:
    """
    Generate image using AI
    
    Args:
        prompt: Image description
        model: Image model (dall-e-3, dall-e-2)
        user_id: Telegram user ID for logging
        size: Image size
        quality: Image quality
    
    Returns:
        Dict with image URL and metadata
    """
    try:
        logger.info(f"Generating image for user {user_id} with model {model}")
        
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = await client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        
        return {
            "success": True,
            "image_url": response.data[0].url,
            "revised_prompt": response.data[0].revised_prompt,
            "model": model
        }
    
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def analyze_image(
    image_url: str,
    prompt: str = "Describe this image in detail",
    model: str = "gpt-4o",
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Analyze image using vision AI
    
    Args:
        image_url: URL or base64 of image
        prompt: Analysis prompt
        model: Vision model to use
        user_id: Telegram user ID for logging
    
    Returns:
        Dict with analysis and metadata
    """
    try:
        logger.info(f"Analyzing image for user {user_id} with model {model}")
        
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=500
        )
        
        return {
            "success": True,
            "analysis": response.choices[0].message.content,
            "model": model
        }
    
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
