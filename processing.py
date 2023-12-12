# pip install pyngrok==4.1.1
# pip install flask_ngrok

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from flask import Flask, render_template, request, jsonify
from flask_ngrok import run_with_ngrok

app = Flask(__name__, template_folder='template')
run_with_ngrok(app)  # Start ngrok when the app is run

# Global variable to store the latest paraphrased entry
latest_entry = {'original_text': '', 'paraphrased_texts': []}

def initialize_model(device="cuda"):
    tokenizer = AutoTokenizer.from_pretrained("chatgpt_paraphraser_on_T5_base")
    model = AutoModelForSeq2SeqLM.from_pretrained("chatgpt_paraphraser_on_T5_base").to(device)
    return tokenizer, model

def paraphrase_input(text, num_beams, num_beam_groups, num_return_sequences,
                     repetition_penalty, diversity_penalty, no_repeat_ngram_size,
                     temperature, max_length):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer, model = initialize_model(device)

    paraphrased_responses = paraphrase(
        tokenizer, model, text,
        num_beams, num_beam_groups, num_return_sequences,
        repetition_penalty, diversity_penalty, no_repeat_ngram_size,
        temperature, max_length
    )

    return paraphrased_responses

def paraphrase(tokenizer, model, text, num_beams, num_beam_groups, num_return_sequences,
               repetition_penalty, diversity_penalty, no_repeat_ngram_size, temperature, max_length):
    input_ids = tokenizer(
        f'paraphrase: {text}',
        return_tensors="pt", padding="longest",
        max_length=max_length,
        truncation=True,
    ).input_ids

    input_ids = input_ids.to(model.device)  # Ensure input_ids are on the same device as the model

    outputs = model.generate(
        input_ids, temperature=temperature, repetition_penalty=repetition_penalty,
        num_return_sequences=num_return_sequences, no_repeat_ngram_size=no_repeat_ngram_size,
        num_beams=num_beams, num_beam_groups=num_beam_groups,
        max_length=max_length, diversity_penalty=diversity_penalty
    )

    res = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    return res

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/paraphrase', methods=['POST'])
def paraphrase_endpoint():
    data = request.form

    text = data.get('text', '')
    num_beams = int(data.get('num_beams', 5))
    num_beam_groups = int(data.get('num_beam_groups', 5))
    num_return_sequences = int(data.get('num_return_sequences', 5))
    repetition_penalty = float(data.get('repetition_penalty', 10.0))
    diversity_penalty = float(data.get('diversity_penalty', 3.0))
    no_repeat_ngram_size = int(data.get('no_repeat_ngram_size', 2))
    temperature = float(data.get('temperature', 0.7))
    max_length = int(data.get('max_length', 128))

    paraphrased_responses = paraphrase_input(
        text, num_beams, num_beam_groups, num_return_sequences,
        repetition_penalty, diversity_penalty, no_repeat_ngram_size,
        temperature, max_length
    )

    # Update the latest entry
    global latest_entry
    latest_entry = {'original_text': text, 'paraphrased_texts': paraphrased_responses}

    return render_template('index.html', text=text, paraphrased_responses=paraphrased_responses)

# New route for API endpoint
@app.route('/api/paraphrase', methods=['POST'])
def paraphrase_api_endpoint():
    # Get the 'text' parameter from the request body
    text = request.form.get('text', '')

    # Default values for other parameters
    num_beams = 5
    num_beam_groups = 5
    num_return_sequences = 5
    repetition_penalty = 10.0
    diversity_penalty = 3.0
    no_repeat_ngram_size = 2
    temperature = 0.7
    max_length = 128

    # Call the paraphrase_input function
    paraphrased_responses = paraphrase_input(
        text, num_beams, num_beam_groups, num_return_sequences,
        repetition_penalty, diversity_penalty, no_repeat_ngram_size,
        temperature, max_length
    )

    # Update the latest entry
    global latest_entry
    latest_entry = {'original_text': text, 'paraphrased_texts': paraphrased_responses}

    # Return processed input and output in JSON format
    return jsonify({'input_text': text, 'paraphrased_responses': paraphrased_responses})

# Route to get the latest paraphrase without using a database
@app.route('/get_latest_paraphrase', methods=['GET'])
def get_latest_paraphrase():
    global latest_entry

    if latest_entry['original_text']:
        paraphrased_texts = '\n'.join(latest_entry['paraphrased_texts'])
        return jsonify({
            'input_text': latest_entry['original_text'],
            'paraphrased_texts': paraphrased_texts
        })
    else:
        return jsonify({'message': 'No paraphrased entries found'})


if __name__ == '__main__':
    app.run()
