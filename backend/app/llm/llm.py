from groq import Groq
from app.config import GROQ_MODEL, GROQ_API_KEY, LLM_TEMPERATURE, LLM_MAX_TOKENS


# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def call_llm(
    prompt: str, 
    model: str = None, 
    temperature: float = None, 
    max_tokens: int = None,
    system_prompt: str = None
) -> str:
    """
    Send a prompt to the LLM and return the response.
    
    Args:
        prompt: The user prompt to send to the LLM
        model: Groq model to use (defaults to GROQ_MODEL from config)
        temperature: Controls randomness (0-1). Lower = more deterministic.
        max_tokens: Maximum length of the response.
        system_prompt: Optional system prompt to set context/behavior.
    
    Returns:
        The LLM's response as a string
    
    Raises:
        Exception: If the Groq API call fails
    """
    # Use defaults from config if not provided
    model = model or GROQ_MODEL
    temperature = temperature if temperature is not None else LLM_TEMPERATURE
    max_tokens = max_tokens or LLM_MAX_TOKENS
    
    # Build messages list
    messages = []
    
    # Add system prompt first if provided
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    # Add user prompt
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        # Log the error (you can add proper logging later)
        print(f"❌ Groq API error: {str(e)}")
        raise Exception(f"LLM service unavailable: {str(e)}")




