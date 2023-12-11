# file name: processing.py

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__, template_folder='template')

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

    input_ids = input_ids.to(model.device)

    outputs = model.generate(
        input_ids, temperature=temperature, repetition_penalty=repetition_penalty,
        num_return_sequences=num_return_sequences, no_repeat_ngram_size=no_repeat_ngram_size,
        num_beams=num_beams, num_beam_groups=num_beam_groups,
        max_length=max_length, diversity_penalty=diversity_penalty
    )

    res = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    return res

# Function to initialize the database connection
def initialize_database():
    db_username = "wilson1"
    db_password = "2004@w"
    db_name = "paraphrase_ai"

    connection = mysql.connector.connect(
        host="localhost",
        user=db_username,
        password=db_password,
        database=db_name
    )

    return connection

# Function to insert data into the database
def insert_into_database(connection, original_text, paraphrased_text):
    cursor = connection.cursor()
    sql = "INSERT INTO paraphrase_log (original_text, paraphrased_text) VALUES (%s, %s)"
    val = (original_text, paraphrased_text)
    cursor.execute(sql, val)
    connection.commit()
    cursor.close()

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

    # Insert data into the database
    connection = initialize_database()
    for response in paraphrased_responses:
        insert_into_database(connection, text, response)
    connection.close()

    # Render the template without returning JSON
    return render_template('index.html', text=text, paraphrased_responses=paraphrased_responses)

@app.route('/api/paraphrase', methods=['POST'])
def paraphrase_api():
    data = request.json

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

    # Insert data into the database
    connection = initialize_database()
    for response in paraphrased_responses:
        insert_into_database(connection, text, response)
    connection.close()

    response_data = {
        'input_text': text,
        'paraphrased_responses': paraphrased_responses
    }

    return jsonify(response_data)

@app.route('/get_latest_paraphrase', methods=['GET'])
def get_latest_paraphrase():
    # Retrieve the latest entry from the database
    connection = initialize_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT original_text, paraphrased_text FROM paraphrase_log ORDER BY id DESC LIMIT 1")
    
    latest_entry = cursor.fetchone()
    
    if latest_entry:
        # Fetch the first 5 paraphrased entries for the latest input text
        cursor.execute("SELECT paraphrased_text FROM paraphrase_log WHERE original_text = %s LIMIT 6", (latest_entry['original_text'],))
        paraphrases = cursor.fetchall()

        if paraphrases:
            # Concatenate the first 5 paraphrased texts into one line
            paraphrased_texts = '\n'.join(entry['paraphrased_text'] for entry in paraphrases)

            return jsonify({
                'input_text': latest_entry['original_text'],
                'paraphrased_text': paraphrased_texts
            })
    
    connection.close()
    return jsonify({'message': 'No paraphrased entries found'})

if __name__ == '__main__':
    app.run()
