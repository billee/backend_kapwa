# app.py

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import logging
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

# Remove all existing handlers to control logging strictly
for handler in app.logger.handlers:
    app.logger.removeHandler(handler)

# Only add a stream handler for direct output
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO) # Set to INFO or DEBUG if you want general Flask logs,
                                  # but we'll use specific print statements for the requested logs.

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai_llm(messages_for_llm):
    try:
        start_time = time.time()
        chat_completion = openai_client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages_for_llm,
            temperature=0.7,
            max_tokens=500,
        )
        llm_response = chat_completion.choices[0].message.content
        end_time = time.time() # End timer
        app.logger.info(f"OpenAI LLM call took {end_time - start_time:.2f} seconds.") # Log duration
        return llm_response
    except Exception as e:
        app.logger.error(f"Error calling OpenAI LLM: {e}")
        return f"Error: Failed to get response from AI. Details: {e}"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages')
    if not messages:
        return jsonify({"error": "No messages provided"}), 400
    # app.logger.info(f"Received chat request with {len(messages)} messages.") # Removed as requested
    openai_messages = []
    for msg in messages:
        role = msg.get('role')
        content = msg.get('content')
        if role and content:
            openai_messages.append({"role": role, "content": content})
        # else:
            # app.logger.warning(f"Skipping malformed message: {msg}") # Removed as requested
    if not openai_messages:
        return jsonify({"error": "No valid messages for LLM"}), 400
    llm_response = call_openai_llm(openai_messages)
    return jsonify({"response": llm_response})

@app.route('/summarize_chat', methods=['POST'])
def summarize_chat():
    data = request.json
    messages = data.get('messages')

    print(f"\nMessages: \n{messages}\n") 


    if not messages:
        return jsonify({"error": "No messages provided for summarization"}), 400

    print(f"Received summarization request with {len(messages)} messages.\n") 
    

    previous_summary_content = None
    conversation_messages_for_llm = [] 


    for msg in messages:
        if msg.get('role') == 'system' and "Continuing from our last conversation:" in msg.get('content', ''):
            previous_summary_content = msg['content'].replace("Continuing from our last conversation: ", "").strip()
        else:
            role = msg.get('role')
            content = msg.get('content')
            sender_name = msg.get('senderName', 'Participant')
            if role and content:
                if role == 'user':
                    conversation_messages_for_llm.append({"role": "user", "content": f"{sender_name}: {content}"})
                elif role == 'assistant':
                    conversation_messages_for_llm.append({"role": "assistant", "content": content}) 
            # else:
                # app.logger.warning(f"Summarization: Skipping malformed message in current conversation: {msg}") 

    print(f"\nprevious_summary_content: \n{previous_summary_content}\n")
    print(f"\nconversation_messages_for_llm: \n{conversation_messages_for_llm}\n") 

    conversation_text = ""
    for msg in conversation_messages_for_llm:
        if msg['role'] == 'user':
            conversation_text += f"User: {msg['content']}\n"
        elif msg['role'] == 'assistant':
            conversation_text += f"Assistant: {msg['content']}\n"

    summary_prompt_messages = [
        {
            "role": "system", 
            "content": "You are a highly skilled summarization AI. Your primary goal is to create a single, comprehensive, and concise summary of a conversation. **The final summary MUST be a single, continuous paragraph without line breaks or bullet points.**"
        },
        {
            "role": "user",
            "content": f"""Please create a comprehensive summary of this conversation:

{f"Previous summary: {previous_summary_content}" if previous_summary_content and previous_summary_content != "No sufficient conversation to summarize." else ""}

Current conversation:
{conversation_text}

Create a single paragraph summary that captures all the key points, topics discussed, and important details from {'both the previous summary and ' if previous_summary_content else ''}the current conversation."""
        }
    ]

    print(f"\nsummary_prompt_messages: \n{summary_prompt_messages}\n") 

    if not previous_summary_content and not conversation_messages_for_llm:
        return jsonify({"summary": "No sufficient conversation to summarize."})

    summary = call_openai_llm(summary_prompt_messages)
    summary = summary.replace('\n', ' ').strip()
    
    # print(f"\nsummary: \n{summary}\n") 
    # print('###############################################################################')
    # exit()

    # Log the LLM output for summarization
    print("\n--- LLM RETURNED CUMULATIVE SUMMARY (CLEANED) ---")
    print(f"Summary: {summary}")
    print("--------------------------------------------------")
    
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)