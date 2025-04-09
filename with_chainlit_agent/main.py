import os
import requests
import chainlit as cl
from dotenv import load_dotenv
import PyPDF2
import io
from typing import List, Dict, Optional

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Store for PDF contents
pdf_store = {}

@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history", [])
    cl.user_session.set("uploaded_pdfs", {})

    welcome_message = """
    # [Altaf Sajdi](https://github.com/altaf-sajdi)

    Hello! I'm your AI assistant. How can I help you today?
    You can:
    1. Upload PDF books for me to read
    2. Ask questions about uploaded PDFs
    3. Get information about Altaf Sajdi
    """

    await cl.Message(content=welcome_message).send()

def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extract text from PDF content."""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        text = f"Error processing PDF: {str(e)}"
    return text

@cl.on_file_upload(accept=["application/pdf"])
async def handle_pdf_upload(file: cl.File):
    """Handle PDF file uploads."""
    # Read PDF content
    pdf_content = await file.read()
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_content)
    
    # Store PDF text in user session
    pdfs = cl.user_session.get("uploaded_pdfs", {})
    pdfs[file.name] = pdf_text
    cl.user_session.set("uploaded_pdfs", pdfs)
    
    await cl.Message(
        content=f"✅ Successfully processed PDF: {file.name}"
    ).send()

def get_altaf_data() -> str:
    """Get Altaf Sajdi's profile information."""
    try:
        response = requests.get("https://github.com/altaf-sajdi")
        if response.status_code == 200:
            return "Altaf Sajdi is a software developer. You can find more information on his GitHub profile."
        else:
            return f"Error fetching data: Status code {response.status_code}"
    except Exception as e:
        return f"Error fetching data: {str(e)}"

def search_pdfs(query: str, pdfs: Dict[str, str]) -> str:
    """Search through uploaded PDFs for relevant information."""
    if not pdfs:
        return "No PDFs have been uploaded yet."
    
    results = []
    for filename, content in pdfs.items():
        if query.lower() in content.lower():
            # Get context around the match
            idx = content.lower().find(query.lower())
            start = max(0, idx - 100)
            end = min(len(content), idx + len(query) + 100)
            context = content[start:end]
            results.append(f"From {filename}:\n{context}\n")
    
    if not results:
        return f"No relevant information found in PDFs for: {query}"
    
    return "\n".join(results)

@cl.on_message
async def handle_message(message: cl.Message):
    msg = message.content.lower()
    
    # Get uploaded PDFs from session
    pdfs = cl.user_session.get("uploaded_pdfs", {})
    
    if "hello" in msg or "hi" in msg:
        await cl.Message(content="Salam from Altaf Sajdi").send()
    
    elif "bye" in msg or "goodbye" in msg:
        await cl.Message(content="Allah Hafiz from Altaf Sajdi").send()
    
    elif "altaf" in msg or "profile" in msg or "github" in msg:
        info = get_altaf_data()
        await cl.Message(content=info).send()
    
    elif pdfs and ("pdf" in msg or "book" in msg or "search" in msg or "find" in msg):
        results = search_pdfs(msg, pdfs)
        await cl.Message(content=results).send()
    
    else:
        help_message = """I can help you with:
1. Greeting you
2. Providing information about Altaf Sajdi
3. Searching through uploaded PDF books
4. Saying goodbye

You can also upload PDF files and I'll help you extract information from them."""
        await cl.Message(content=help_message).send()