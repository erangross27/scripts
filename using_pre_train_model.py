import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

# Load the GPT-2 model and tokenizer
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

# Define a function to generate answers to questions
def generate_answer(question):
    # Preprocess the input question
    inputs = tokenizer.encode_plus(question, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]

    # Generate the answer using the GPT-2 model
    outputs = model(**inputs)
    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits
    answer_start = torch.argmax(answer_start_scores)
    answer_end = torch.argmax(answer_end_scores) + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))

    return answer

# Test the function with some example questions
print(generate_answer("What is the capital of France?"))
print(generate_answer("Who wrote the book '1984'?"))