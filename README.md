# Real-time Paraphrase AI with Database Integration
 This is a Flask web application that leverages the Hugging Face Transformers library to perform text paraphrasing using a pre-trained model. Here's a brief explanation of the code:

## Model Initialization:
The code initializes a sequence-to-sequence model for text paraphrasing using the AutoTokenizer and AutoModelForSeq2SeqLM classes from Hugging Face's Transformers library.

## Flask Web Application:
The Flask web application is created with an endpoint to handle paraphrasing requests.

## Paraphrasing Logic:
Paraphrasing is performed using the paraphrase_input and paraphrase functions. The input text is tokenized, and the model generates paraphrased responses based on specified parameters like num_beams, repetition_penalty, and others.

## Database Integration:
The application interacts with a MySQL database to store original and paraphrased texts. The database connection, insertion, and retrieval logic are defined in functions like initialize_database, insert_into_database, and get_latest_paraphrase.

## Web Routes:
The application defines routes for web pages (/ and /paraphrase) and API endpoints (/api/paraphrase and /get_latest_paraphrase). The /paraphrase route handles form submissions for paraphrasing, and the /api/paraphrase endpoint accepts JSON data for API-based paraphrasing.

## Rendering Templates:
The application uses Flask's render_template function to render an HTML template (index.html) for displaying paraphrased responses.

## Execution:
The application can be run locally, and it serves a web interface for users to input text and receive paraphrased responses. The API endpoints allow programmatic access.

This code provides a foundation for building a simple text paraphrasing web application with database integration. Customize it according to your requirements and ensure proper security measures for deployment.

# Explanation of GO
This Go program interacts with a Flask web application (from the previous example) to retrieve the latest paraphrased text, display it, and insert it into a MySQL database. Here's a brief explanation of the code:

## Database Configuration:
Database credentials and connection information are defined as constants (DatabaseUser, DatabasePass, DatabaseName, ConnectionString).

## Data Structure:
The LatestParaphrase struct is defined to represent the structure of the JSON response from the Flask application.

## Main Function:
The main function is the entry point of the program. It continuously makes requests to the Flask application's /get_latest_paraphrase endpoint to retrieve the latest paraphrased text.

## HTTP Request:
The getLatestParaphrase function sends an HTTP GET request to the Flask application and parses the JSON response into a LatestParaphrase struct.

## Database Interaction:
The program maintains a previous response to check if there's a new paraphrase. If a new paraphrase is detected, it prints the input and output, inserts the data into the MySQL database, and updates the previous response.

## Database Insertion:
The insertIntoDatabase function prepares an SQL statement to insert the input and output text into the specified table (paraphrase_golang). It uses placeholders (?) to prevent SQL injection and executes the statement.

## Sleep Duration:
After each iteration, the program waits for a specified duration (3 seconds in this case) before making the next request. Adjust the sleep duration based on your needs.

## Error Handling:
The code includes error handling to manage potential issues with HTTP requests, JSON parsing, database connections, and SQL operations.

### Note:
Ensure that the Flask application is running and accessible at http://localhost:5000 for this Go program to function correctly. Adjust database and connection details as needed.
### Model Link:
[humarin/chatgpt_paraphraser_on_T5_base](https://huggingface.co/humarin/chatgpt_paraphraser_on_T5_base)
