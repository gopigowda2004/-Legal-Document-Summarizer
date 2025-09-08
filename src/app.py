import streamlit as st
from document_processor import DocumentProcessor
from summarizer import LegalSummarizer
import os
import tempfile
import time

def initialize_session_state():
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'download_ready' not in st.session_state:
        st.session_state.download_ready = False

st.set_page_config(
    page_title="Legal Document Summarizer",
    page_icon="⚖️",
    layout="wide"
)

def main():
    initialize_session_state()
    st.title("Legal Document Summarizer")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    max_length = st.sidebar.number_input(
        "Maximum Summary Length (characters)",
        min_value=100,
        max_value=5000,
        value=2000,
        step=100
    )
    
    show_preprocessing = st.sidebar.checkbox("Show Preprocessing Steps", False)
    show_metadata = st.sidebar.checkbox("Show Document Metadata", True)

    # Initialize processors
    doc_processor = DocumentProcessor()
    summarizer = LegalSummarizer()

    # File upload with supported formats info
    st.info("Supported formats: PDF, DOCX, TXT")
    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'docx', 'pdf'])

    if uploaded_file:
        # Progress bar container
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        try:
            # Process document with progress updates
            status_text.text("Reading document...")
            progress_bar.progress(20)
            text = doc_processor.read_document(temp_path)

            if text:
                # Extract metadata
                status_text.text("Extracting metadata...")
                progress_bar.progress(40)
                metadata = doc_processor.extract_metadata(text)

                # Preprocess text
                status_text.text("Preprocessing text...")
                progress_bar.progress(60)
                processed_text = doc_processor.preprocess_text(text)

                with col1:
                    st.subheader("Original Document")
                    st.text_area("", text, height=400)

                    if show_preprocessing:
                        st.subheader("Preprocessed Text")
                        st.text_area("", processed_text, height=200)

                    if show_metadata:
                        st.subheader("Document Metadata")
                        for key, value in metadata.items():
                            if value:
                                st.write(f"**{key.title()}:**")
                                if isinstance(value, list):
                                    for item in value:
                                        st.write(f"- {item}")
                                else:
                                    st.write(value)

                with col2:
                    # Generate summary
                    status_text.text("Generating summary...")
                    progress_bar.progress(80)
                    summary = summarizer.generate_summary(processed_text, max_length, metadata)

                    st.subheader("Document Summary")
                    st.markdown(summary)

                    # Add to history
                    if summary not in [h['summary'] for h in st.session_state.history]:
                        st.session_state.history.append({
                            'filename': uploaded_file.name,
                            'summary': summary,
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    # Download options
                    st.subheader("Export Options")
                    col_download1, col_download2 = st.columns(2)
                    
                    with col_download1:
                        st.download_button(
                            label="Download Summary",
                            data=summary,
                            file_name=f"summary_{uploaded_file.name}.txt",
                            mime="text/plain"
                        )
                    
                    with col_download2:
                        # Export both summary and metadata
                        export_data = f"""Document Summary Report
Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
Original File: {uploaded_file.name}

{'-'*50}
METADATA
{'-'*50}
"""
                        for key, value in metadata.items():
                            if value:
                                export_data += f"\n{key.title()}:\n"
                                if isinstance(value, list):
                                    export_data += "\n".join(f"- {item}" for item in value)
                                else:
                                    export_data += str(value)
                                export_data += "\n"
                        
                        export_data += f"\n{'-'*50}\nSUMMARY\n{'-'*50}\n{summary}"
                        
                        st.download_button(
                            label="Download Full Report",
                            data=export_data,
                            file_name=f"report_{uploaded_file.name}.txt",
                            mime="text/plain"
                        )

                # Complete progress bar
                progress_bar.progress(100)
                status_text.text("Processing complete!")

            else:
                st.error("Error reading the document. Please try again.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            # Clean up temporary file
            os.unlink(temp_path)

    # Show processing history
    if st.session_state.history:
        st.sidebar.header("Processing History")
        for item in reversed(st.session_state.history):
            with st.sidebar.expander(f"{item['filename']} - {item['timestamp']}"):
                st.write(item['summary'][:200] + "...")

if __name__ == "__main__":
    main()