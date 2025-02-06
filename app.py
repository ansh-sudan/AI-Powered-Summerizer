import streamlit as st
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from openai import OpenAI
LOGO_URL_LARGE = "https://docs.streamlit.io/logo.svg"
LOGO_URL_SMALL = "https://docs.streamlit.io/logo.svg"

load_dotenv()
st.title('Summerizer App')
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

# llm = ChatOpenAI(model="gpt-4o-mini", api_key="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" )
# llm = ChatOpenAI(model="gpt-4o-mini" )
llm = ChatGroq(model="deepseek-r1-distill-llama-70b", api_key="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")
# llm = ChatGroq(model="deepseek-r1-distill-llama-70b")
# llm = OpenAI(api_key="sk-aed332429b37491faa6c05a90e4499f1", base_url="https://api.deepseek.com")


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

            print("FINAL SUMMARY: ",final_summary)
            container.write(final_summary)

        except Exception as e:
            print("error creating final summary",e)
            st.error(f"Error creating final summary: {e}")
