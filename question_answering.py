from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, TrainingArguments, Trainer

# Load the pre-trained model and tokenizer
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

# Load the SQuAD dataset
squad_dataset = load_dataset('squad')

# Define the training and validation datasets
train_dataset = squad_dataset['train']
val_dataset = squad_dataset['validation']

# Define the data collator
data_collator = lambda data: {'input_ids': tokenizer(data['question'], data['context'], truncation=True, padding='max_length')['input_ids'], 'attention_mask': tokenizer(data['question'], data['context'], truncation=True, padding='max_length')['attention_mask'], 'start_positions': data['start_positions'], 'end_positions': data['end_positions']}

# Define the training arguments
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy='epoch',
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    push_to_hub=False,
    logging_dir='./logs',
    logging_steps=500,
    save_strategy='epoch',  # Add this line
    load_best_model_at_end=True,
    metric_for_best_model='eval_f1',
    greater_is_better=True
)

# Define the trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

# Fine-tune the model on the training set
trainer.train()

# Evaluate the fine-tuned model on the validation set
trainer.evaluate(val_dataset)

# Test the model on a few examples
context = "The quick brown fox jumps over the lazy dog."
question = "What animal jumps over the dog?"
inputs = tokenizer(question, context, add_special_tokens=True, return_tensors="pt")
start_positions = torch.tensor([1])
end_positions = torch.tensor([4])
outputs = model(**inputs, start_positions=start_positions, end_positions=end_positions)
answer_start = torch.argmax(outputs.start_logits)
answer_end = torch.argmax(outputs.end_logits) + 1
answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))
print(f"Question: {question}")
print(f"Answer: {answer}")