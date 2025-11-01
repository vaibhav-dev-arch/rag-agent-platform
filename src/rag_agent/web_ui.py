from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from typing import List, Dict, Any

app = Flask(__name__)

# Global storage for documents (in a real app, you'd use a database)
documents = [
    "Python is a high-level programming language known for its simplicity and readability. It's widely used in data science, web development, and automation.",
    "Machine learning is a subset of artificial intelligence that enables computers to learn and make predictions from data without being explicitly programmed.",
    "LlamaIndex is a data framework for LLM applications that helps you ingest, structure, and access your data for LLMs.",
    "OpenAI provides powerful language models like GPT-3.5 and GPT-4 that can understand and generate human-like text.",
    "Vector databases store and retrieve data using vector embeddings, enabling semantic search and similarity matching.",
    "Retrieval-Augmented Generation (RAG) combines information retrieval with text generation to provide more accurate and contextual responses."
]

def simple_retrieve(query: str, docs: List[str], top_k: int = 3) -> List[str]:
    """Simple keyword-based document retrieval"""
    import re
    query_words = set(re.findall(r'\w+', query.lower()))
    
    scored_docs = []
    for i, doc in enumerate(docs):
        doc_words = set(re.findall(r'\w+', doc.lower()))
        overlap = len(query_words.intersection(doc_words))
        scored_docs.append((overlap, doc, i))
    
    scored_docs.sort(reverse=True)
    return [doc for score, doc, idx in scored_docs[:top_k]]

def query_ollama(prompt: str) -> str:
    """Query the local Ollama model"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response from model")
        else:
            return f"Error: {response.status_code}"
            
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

@app.route('/')
def index():
    return render_template('index.html', documents=documents)

@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'No question provided'})
    
    # Step 1: Retrieve relevant documents
    relevant_docs = simple_retrieve(question, documents, top_k=3)
    
    # Step 2: Create prompt with context
    context = "\n".join(relevant_docs)
    prompt = f"""Based on the following information, answer the question:

Information:
{context}

Question: {question}

Answer:"""
    
    # Step 3: Get response from Ollama
    answer = query_ollama(prompt)
    
    return jsonify({
        'answer': answer,
        'sources': relevant_docs,
        'question': question
    })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    return jsonify({'documents': documents})

@app.route('/api/documents', methods=['POST'])
def add_document():
    data = request.get_json()
    new_doc = data.get('document', '')
    
    if new_doc:
        documents.append(new_doc)
        return jsonify({'success': True, 'message': 'Document added successfully'})
    else:
        return jsonify({'error': 'No document provided'})

@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    if 0 <= doc_id < len(documents):
        deleted_doc = documents.pop(doc_id)
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
    else:
        return jsonify({'error': 'Invalid document ID'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Chat Interface</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            height: 90vh;
        }
        .chat-section, .documents-section {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chat-section {
            display: flex;
            flex-direction: column;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #fafafa;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
        }
        .user-message {
            background-color: #007bff;
            color: white;
            margin-left: 20%;
        }
        .bot-message {
            background-color: #e9ecef;
            color: #333;
            margin-right: 20%;
        }
        .sources {
            font-size: 0.8em;
            color: #666;
            margin-top: 10px;
            padding: 5px;
            background-color: #f8f9fa;
            border-radius: 3px;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        input[type="text"], textarea {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #6c757d;
            cursor: not-allowed;
        }
        .documents-list {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            background-color: #fafafa;
        }
        .document-item {
            padding: 10px;
            margin-bottom: 10px;
            background-color: white;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .document-item:last-child {
            margin-bottom: 0;
        }
        .delete-btn {
            background-color: #dc3545;
            padding: 5px 10px;
            font-size: 12px;
        }
        .delete-btn:hover {
            background-color: #c82333;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        h2 {
            color: #333;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <h1>🤖 RAG Chat Interface</h1>
    
    <div class="container">
        <div class="chat-section">
            <h2>💬 Chat with RAG</h2>
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    Hello! I'm your RAG assistant. Ask me anything about the documents in the knowledge base.
                </div>
            </div>
            <div class="input-group">
                <input type="text" id="questionInput" placeholder="Ask a question..." onkeypress="handleKeyPress(event)">
                <button onclick="askQuestion()" id="askBtn">Ask</button>
            </div>
        </div>
        
        <div class="documents-section">
            <h2>📚 Knowledge Base</h2>
            <div class="input-group">
                <textarea id="newDocument" placeholder="Add a new document to the knowledge base..." rows="3"></textarea>
                <button onclick="addDocument()">Add</button>
            </div>
            <div class="documents-list" id="documentsList">
                <!-- Documents will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        // Load documents on page load
        loadDocuments();

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                askQuestion();
            }
        }

        async function askQuestion() {
            const questionInput = document.getElementById('questionInput');
            const askBtn = document.getElementById('askBtn');
            const question = questionInput.value.trim();
            
            if (!question) return;
            
            // Disable input and button
            questionInput.disabled = true;
            askBtn.disabled = true;
            
            // Add user message
            addMessage(question, 'user');
            questionInput.value = '';
            
            // Add loading message
            const loadingId = addMessage('Thinking...', 'bot', 'loading');
            
            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                
                // Remove loading message
                document.getElementById(loadingId).remove();
                
                if (data.error) {
                    addMessage('Error: ' + data.error, 'bot');
                } else {
                    let sourcesText = '';
                    if (data.sources && data.sources.length > 0) {
                        sourcesText = '<div class="sources"><strong>Sources:</strong><br>' + 
                                    data.sources.map((source, i) => `${i+1}. ${source.substring(0, 100)}...`).join('<br>') + 
                                    '</div>';
                    }
                    addMessage(data.answer + sourcesText, 'bot');
                }
            } catch (error) {
                document.getElementById(loadingId).remove();
                addMessage('Error: ' + error.message, 'bot');
            } finally {
                // Re-enable input and button
                questionInput.disabled = false;
                askBtn.disabled = false;
                questionInput.focus();
            }
        }

        function addMessage(text, type, className = '') {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            const messageId = 'msg-' + Date.now();
            messageDiv.id = messageId;
            messageDiv.className = `message ${type}-message ${className}`;
            messageDiv.innerHTML = text;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return messageId;
        }

        async function loadDocuments() {
            try {
                const response = await fetch('/api/documents');
                const data = await response.json();
                displayDocuments(data.documents);
            } catch (error) {
                console.error('Error loading documents:', error);
            }
        }

        function displayDocuments(documents) {
            const documentsList = document.getElementById('documentsList');
            documentsList.innerHTML = '';
            
            documents.forEach((doc, index) => {
                const docDiv = document.createElement('div');
                docDiv.className = 'document-item';
                docDiv.innerHTML = `
                    <div>${doc.substring(0, 150)}...</div>
                    <button class="delete-btn" onclick="deleteDocument(${index})">Delete</button>
                `;
                documentsList.appendChild(docDiv);
            });
        }

        async function addDocument() {
            const newDocument = document.getElementById('newDocument');
            const documentText = newDocument.value.trim();
            
            if (!documentText) return;
            
            try {
                const response = await fetch('/api/documents', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ document: documentText })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    newDocument.value = '';
                    loadDocuments();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        async function deleteDocument(docId) {
            if (!confirm('Are you sure you want to delete this document?')) return;
            
            try {
                const response = await fetch(`/api/documents/${docId}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    loadDocuments();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
    </script>
</body>
</html>'''
    
    # Write the HTML template to a file
    with open('templates/index.html', 'w') as f:
        f.write(html_template)
    
    print("🌐 Starting RAG Web UI...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("💡 Make sure Ollama is running with the tinyllama model")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 