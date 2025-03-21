import streamlit as st
from agent import generate_document  # Import from backend
import markdown
import pdfkit

# Set wide layout
st.set_page_config(
    page_title="DocLearn",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Callback for progress updates
def update_progress(message):
    status_placeholder.text(message)

# Function to convert Markdown to PDF
def convert_to_pdf(markdown_content, filename):
    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['extra'])  # 'extra' supports tables, etc.
    # Convert HTML to PDF
    output_file = f"{filename}.pdf"
    pdfkit.from_string(html_content, output_file)
    with open(output_file, 'rb') as f:
        return f.read()

# Sidebar for inputs
with st.sidebar:
    st.header("Input Options")
    
    topic = st.text_input(
        "📝 Topic",
        placeholder="e.g., Machine Learning, Quantum Physics",
        help="Enter the topic you want to learn about."
    )
    
    knowledge_level = st.radio(
        "🧠 Complexity Level",
        ["Basic", "Intermediate", "Expert"],
        captions=["Fundamental concepts", "In-depth knowledge", "Advanced topics"], 
        help="Choose your current understanding."
    )

    output_format = st.radio(
        "📄 Output Format",
        ["Markdown", "PDF"],
        captions=["Easy to read", "Easy to share"],
        help="Choose your download format."
    )
    
    generate_clicked = st.button("Generate Document", type="primary")

# Main content
st.title("DocLearn")
st.write("Generate Learning Documents with ease!")

if generate_clicked:
    if not topic:
        st.error("Please enter a topic to proceed.")
    else:
        # Progress indicator
        status_placeholder = st.empty()
        with st.spinner("Generating your document..."):
            document = generate_document(topic, knowledge_level, update_progress)
        
        # Preview as Markdown (default)
        status_placeholder.text("Ready! Here’s your document:")
        st.markdown(document, unsafe_allow_html=True)
        
        # Download logic based on output format
        if output_format == "Markdown":
            st.download_button(
                label="Download Document",
                data=document,
                file_name=f"{topic}_guide.md",
                mime="text/markdown",
                type="secondary"
            )
        else:  # PDF
            try:
                pdf_data = convert_to_pdf(document, topic)
                st.download_button(
                    label="Download Document",
                    data=pdf_data,
                    file_name=f"{topic}_guide.pdf",
                    mime="application/pdf",
                    type="secondary"
                ) 
            except Exception as e:
                st.error(f"PDF conversion failed: {str(e)}. Try Markdown instead.")
                st.download_button(
                label="Download Document",
                data=document,
                file_name=f"{topic}_guide.md",
                mime="text/markdown",
                type="secondary"
                )