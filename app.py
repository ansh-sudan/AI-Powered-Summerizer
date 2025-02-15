import streamlit as st
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
LOGO_URL_LARGE = "https://docs.streamlit.io/logo.svg"
LOGO_URL_SMALL = "https://docs.streamlit.io/logo.svg"

load_dotenv()
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    .custom-title {
        font-size: 38px;
        color: rgb(255, 99, 71);
        font-family: 'Montserrat', sans-serif;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Using HTML to display the customized title
st.markdown('<h1 class="custom-title">NEURAL SUMM.AI</h1>', unsafe_allow_html=True)
st.divider()
# Add the logo
st.logo(
    LOGO_URL_LARGE,
    link="https://www.linkedin.com/in/ansh-sudan-7aa596229/",
    icon_image=LOGO_URL_SMALL
    )
st.markdown("## Start Summarizing your document here")

# Upload File
uploaded_file = st.file_uploader("Choose a Text, PDF or CSV File",type=['txt','pdf','csv'])
API_KEY = os.getenv("GRDQ_API_KEY")

# Use the API key in your code
llm = ChatGroq(model="deepseek-r1-distill-llama-70b", api_key=API_KEY)
# llm = ChatOpenAI(model="gpt-4o-mini")
# llm = ChatGroq(model="deepseek-r1-distill-llama-70b", api_key="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")
# llm = ChatGroq(model="deepseek-r1-distill-llama-70b")

parser = StrOutputParser()

prompt_template = ChatPromptTemplate.from_template("Summarize the following document {document}")

# Chain
chain = prompt_template | llm | parser

if uploaded_file is not None:
    with st.spinner("Processing"):
        try:
            print("File: ",uploaded_file)
            print("File Type: ",uploaded_file.type)

            temp_file_path = uploaded_file.name
            print("File Path: ",temp_file_path)

            #Save uploaded file
            with open(temp_file_path,"wb") as f:
                f.write(uploaded_file.getbuffer())


            #Create document loader
            if uploaded_file.type == 'text/plain':
                loader = TextLoader(temp_file_path)
            elif uploaded_file.type == 'application/pdf':
                loader = PyPDFLoader(temp_file_path)
            elif uploaded_file.type == 'text/csv':
                loader = CSVLoader(temp_file_path)
            else: 
                st.error("File Type Not Supported")
                st.stop()

            # Create document
            doc = loader.load()
            print(doc)


            #Create text splitter
            text_splitter  = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

            #Document Chunks
            chunks = text_splitter.split_documents(doc)
            print(chunks)

        except Exception as e:
            print(e)

    st.success("File Uploaded Successfully")




# Summarize Chunks
if st.button('Summarize'):
    container = st.empty()
    chunk_summaries = []
    # Summarize Chunks
    with st.spinner('Summarizing Chunks'):
        try:
            for i, chunk in enumerate(chunks):
                print(f"Proessing Chunk {i + 1}/{len(chunks)}")
                

                #prompt
                chunk_prompt = ChatPromptTemplate.from_template("You are a highly skilled AI that can summarize text. Please summarize the following text:\n \n {document}")
                
                #chain
                chunk_chain = chunk_prompt | llm | parser
                chunk_summary = chunk_chain.invoke({"document": chunk})
                chunk_summaries.append(chunk_summary)
        except Exception as e:
            print("Error Summarizing Chunks:",e)
            st.error(f"Error Summarizing Chunks: {e}")
            st.stop()
    # print("CHUNKS SUMMARIES", chunk_summaries)


    # Final Summary
    with st.spinner("Creating final summary..."):
        try:
            #  Combine Summaries
            combined_summary = "\n".join(chunk_summaries)

            #Final summary prompt
            final_prompt = ChatPromptTemplate.from_template("You are a highly skilled AI that can summarize text. Please summarize the following text:\n \n {document}")

            final_chain = final_prompt | llm | parser
            final_summary = final_chain.invoke({"document": combined_summary})
            final_summary_cleaned = final_summary.replace('<think>', '').replace('</think>', '') 

            print("FINAL SUMMARY: ",final_summary_cleaned)
            container.write(final_summary_cleaned)

        except Exception as e:
            print("error creating final summary",e)
            st.error(f"Error creating final summary: {e}")
        

if st.button("Connect with me on LinkedIn"):
    st.markdown(
        """
    <style>
    .linkedin-button {
        background-color: #0072b1;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        border: none;
    }
    .linkedin-button:hover {
        background-color: #005f91;
    }
    </style>
    <a href="https://www.linkedin.com/in/ansh-sudan-7aa596229/" target="_blank">
        <button class="linkedin-button">Visit my LinkedIn Profile</button>
    </a>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
        ### ABOUT ME
        - **Name:** Ansh Sudan
        - **Profession:** AI/ML Enthusiast / Developer
        - **GitHub:** [GitHub Profile](https://github.com/ansh-sudan)
             """)

    #     try:
    #         response = client.chat.completions.create(
    #     model="gpt-4o",  
    #     messages=[{"role": "user", "content": f"Summarize this: {document_text}"}],
    #     max_tokens=200
    # )
    #         summary = response.choices[0].message.content
    #     except openai.OpenAIError as e:
    #         st.error(f"OpenAI API error: {e}")
    #     except Exception as e:
    #         st.error(f"Connection error: {e}")


        

