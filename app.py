import streamlit as st
from agent import generate_document  # Import from backend
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import re

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
    pdf_file = f"{filename}.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    # Customize styles
    heading1 = styles['Heading1']
    heading2 = styles['Heading2']
    normal = styles['Normal']
    normal.leading = 14  # Line spacing
    
    # Elements to build into PDF
    story = []
    
    # Split Markdown into lines and process
    lines = markdown_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 12))  # Add space between paragraphs
            continue
        
        # Handle headers
        if line.startswith('# '):
            story.append(Paragraph(line[2:], heading1))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], heading2))
        else:
            # Handle inline <sub> and <sup> tags
            def replace_tags(match):
                tag = match.group(0)
                content = match.group(1)
                if '<sub>' in tag:
                    return f'<sub>{content}</sub>'  # Reportlab uses <sub> directly
                elif '<sup>' in tag:
                    return f'<sup>{content}</sup>'
                return tag
            
            formatted_line = re.sub(r'(<sub>.*?</sub>|<sup>.*?</sup>)', replace_tags, line)
            story.append(Paragraph(formatted_line, normal))
    
    # Build PDF
    doc.build(story)
    with open(pdf_file, 'rb') as f:
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
