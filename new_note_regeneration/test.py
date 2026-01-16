import tiktoken
from transformers import AutoTokenizer
import prompts

#When it iterateed and the tokens is reaching for max for that blob of text, cap at 700, not 800 to allow for the error of the base model we used for counting token

def num_tokens_from_string(string: str, model_name: str) -> int:
    
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to a default encoding if the model name is not found
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = len(encoding.encode(string))
    return num_tokens

# Example usage
text_blob = prompts.regeneration_system_prompt#"I have a blob of text and I want to count the number of tokens in python."
# Use an appropriate model name, e.g., "gpt-4o-mini", "gpt-3.5-turbo", or "gpt-4"


model = "llama-3.1-8b-instant" 
token_count = num_tokens_from_string(text_blob, model)

print(f"The text has {token_count} tokens for the model {model}.")
