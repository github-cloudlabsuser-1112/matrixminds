from fastapi import APIRouter
from fastapi import Request, Form, File, UploadFile, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from core.config import AZURE_OPENAI_DEPLOYMENT
import os
import json
import re
import sqlite3


from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import AzureChatOpenAI
from langchain.chains import RetrievalQA



templates = Jinja2Templates(directory="templates")
general_pages_router = APIRouter()


@general_pages_router.get("/")
async def home(request: Request):
    print('HERE')
    return templates.TemplateResponse("general_pages/index.html",{"request":request})

@general_pages_router.get("/call")
async def home(request: Request):
    return templates.TemplateResponse("general_pages/call.html",{"request":request})


@general_pages_router.post("/summarychart")
async def summarychart(request: Request):
    print('in Summary Chart')
    plotlyCatDataArray=[]
    plotlySentimentDataArray=[]
    plotlyEmotionDataArray=[]
    plotlyAvgTimeDataArray=[]
    try:

        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect('matrix.db')
        cursor = sqliteConnection.cursor()
       
        cursor.execute('''SELECT DISTINCT CATEGORY, COUNT(*) FROM transcript GROUP BY CATEGORY''')
        rows = cursor.fetchall()
        x=[]
        y=[]
        yValue=[]
        for row in rows:    
            title = row[0]
            x.append(title)     
            count = row[1]
            y.append(count)
            yValue.append(str(count))
             
        plotlyCatData={}
        plotlyCatData['x']=x
        plotlyCatData['y']=y
        plotlyCatData['type']='bar'
        plotlyCatData['text']=yValue
        plotlyCatData['textposition']='auto'
        
        plotlyCatDataArray.append(plotlyCatData)
        
        cursor.execute('''SELECT DISTINCT SENTIMENT, COUNT(*) FROM transcript GROUP BY SENTIMENT''')
        rows = cursor.fetchall()
        labels=[]
        values=[]
        for row in rows:    
            title = row[0]
            labels.append(title)     
            count = row[1]
            values.append(count)
             
        plotlySentimentData={}
        plotlySentimentData['labels']=labels
        plotlySentimentData['values']=values
        plotlySentimentData['type']='pie'
        
        plotlySentimentDataArray.append(plotlySentimentData)
        
        cursor.execute('''SELECT DISTINCT EMOTION, COUNT(*) FROM transcript GROUP BY EMOTION''')
        rows = cursor.fetchall()
        emotlabels=[]
        emotvalues=[]
        for row in rows:    
            title = row[0]
            emotlabels.append(title)     
            count = row[1]
            emotvalues.append(count)
             
        plotlyEmotionData={}
        plotlyEmotionData['labels']=emotlabels
        plotlyEmotionData['values']=emotvalues
        plotlyEmotionData['type']='pie'
        
        plotlyEmotionDataArray.append(plotlyEmotionData)
        
        cursor.execute('''SELECT DISTINCT CATEGORY, round(AVG(DURATION), 2) FROM transcript GROUP BY CATEGORY''')
        rows = cursor.fetchall()
        avgtimex=[]
        avgtimey=[]
        avgtimeyValue=[]
        for row in rows:    
            title = row[0]
            avgtimex.append(title)     
            count = row[1]
            avgtimey.append(count)
            avgtimeyValue.append(str(count))
             
        plotlyAvgTimeData={}
        plotlyAvgTimeData['x']=avgtimex
        plotlyAvgTimeData['y']=avgtimey
        plotlyAvgTimeData['type']='bar'
        plotlyAvgTimeData['text']=avgtimeyValue
        plotlyAvgTimeData['textposition']='auto'
        
        plotlyAvgTimeDataArray.append(plotlyAvgTimeData)
        
        cursor.close()
     
    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred - ', error)

    # Close DB Connection irrespective of success
    # or failure
    finally:

        if sqliteConnection:
            sqliteConnection.close()
            print('SQLite Connection closed')
        
    return {"categoryresponse":plotlyCatDataArray,"sentimentresponse":plotlySentimentDataArray,"emotionresponse":plotlyEmotionDataArray,"avgtimeresponse":plotlyAvgTimeDataArray}



@general_pages_router.post("/rfpsummary")
async def rfpsummary(file: UploadFile = File(...)):
  
    #file.save(app.config['UPLOAD_FOLDER_PATH']+'datafile.pdf')
    with open(UPLOAD_FOLDER_PATH+file.filename, "wb+") as file_object:
        file_object.write(file.file.read())
    
    loader = PyPDFLoader(UPLOAD_FOLDER_PATH+file.filename)
    pages = loader.load_and_split()

    embeddings = AzureOpenAIEmbeddings()
    chromaVecStore = Chroma.from_documents(pages, embeddings)

    llm = AzureChatOpenAI(
                deployment_name=AZURE_OPENAI_DEPLOYMENT,
                temperature=0)
    

    query_prompt = """As a sales executive, prepare a summary of the RFP document\n
                    Answer:
                    """

    qa_chain = RetrievalQA.from_chain_type(
    llm, retriever=chromaVecStore.as_retriever(), chain_type="stuff"
    )
    query = "As a sales executive, prepare a summary of the RFP document"
    result = qa_chain({"query": query})
    result["result"]

    print(result)
    return {"response":result["result"]}

# @general_pages_router.get("/search")
# async def search(q: str):

#     splitstr = q.split('##')
    
#     api_to_use = splitstr[0]
#     print(api_to_use)
#     jobTitle= splitstr[1]
#     spoc=splitstr[2]
#     exp=splitstr[3]
#     role=splitstr[4]+' '
#     jobDesc=''
#     ####SECTION FOR PROMPT TEMPLATE###
#     job_prompt_template = """As an executive recruiter working for Capgemini, use the skills from context to prepare answer. 
#                                 Create Job title, years of experience, Key Responsibilities and required skills sections only.\n\n
#                                 Context: \n"""+role+""" {context}?\n
#                                 Question: \n create job description for title :{question} with """+spoc+""" skills 
#                                 and experience of """+exp+""" \n
#                                 Include about """+role+"""in the answer\n
#                                 Answer:
#                                 """

#     #####
#     vllm = VertexAI(model_name="text-bison@001")

#     if api_to_use=='OPENAI':
#         embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", chunk_size=1)
#         db = ElasticVectorSearch(
#         elasticsearch_url=ESURL,
#         index_name=INDEX_NAME,
#         embedding=embeddings,
#         )
#         llm = AzureChatOpenAI(
#                 openai_api_base=OPENAI_API_BASE,
#                 deployment_name=OPENAI_DEPLOYMENT, 
#                 model_name=OPENAI_MODEL,
#                 temperature=0.4,
#                 openai_api_version=OPENAI_API_VERSION,
#                 openai_api_type="azure")

        
#         query=spoc+' '+jobTitle
#         headerprompt = PromptTemplate(
#             template=header_prompt_template, input_variables=["context", "question"]
#         )
        
#         chain_type_kwargs = {"prompt": headerprompt}
#         qa = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=db.as_retriever(
#                 search_type="similarity",
#                 search_kwargs={"k":3}),
#             chain_type_kwargs=chain_type_kwargs
#         )

#         header_result = qa({'query':query})
#         jobDesc=header_result["result"]+'\n\n'

#         jobprompt = PromptTemplate(
#             template=job_prompt_template, input_variables=["context", "question"]
#         )
       

#         chain_type_kwargs = {"prompt": jobprompt}
#         qa = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=db.as_retriever(
#                 search_type="similarity",
#                 search_kwargs={"k":3}),
#             chain_type_kwargs=chain_type_kwargs
#         )
        
        
#         summary = qa({"query":query})
#         summary = os.linesep.join([s for s in summary["result"].splitlines() if s])
        
#         footerprompt = PromptTemplate(
#             template=footer_prompt_template, input_variables=["context", "question"]
#         )
#         chain_type_kwargs = {"prompt": footerprompt}
#         qa = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=db.as_retriever(
#                 search_type="similarity",
#                 search_kwargs={"k":3}),
#             chain_type_kwargs=chain_type_kwargs
#         )
#         query='Life at Capgemini'
#         footer=qa({"query":query})

#         jobDesc+=summary+'\n\n'+footer["result"]
#         docList=[]
#     else:
#         vertex_embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@001")
#         db = ElasticVectorSearch(
#         elasticsearch_url=ESURL,
#         index_name="vertexgptjobdesc",
#         embedding=vertex_embeddings,
#         )
   
        
#         query=spoc+' '+jobTitle

#         headerprompt = PromptTemplate(
#             template=header_prompt_template, input_variables=["context", "question"]
#         )

#         chain_type_kwargs = {"prompt": headerprompt}
#         qa = RetrievalQA.from_chain_type(
#             llm=vllm,
#             chain_type="stuff",
#             retriever=db.as_retriever(
#                 search_type="similarity",
#                 search_kwargs={"k":3}),
#             chain_type_kwargs=chain_type_kwargs
#         )

#         header_result = qa({"query":query})
#         jobDesc=header_result["result"]+'\n\n'

#         jobprompt = PromptTemplate(
#             template=job_prompt_template, input_variables=["context", "question"]
#         )
        
#         chain_type_kwargs = {"prompt": jobprompt}
#         qa = RetrievalQA.from_chain_type(
#             llm=vllm,
#             chain_type="stuff",
#             retriever=db.as_retriever(
#             search_type="similarity"),
#             chain_type_kwargs=chain_type_kwargs,
#             return_source_documents=True
#         )
        
#         summary = qa({"query":query})
#         footer=vllm(prompt=footer_prompt_template)
#         summary = os.linesep.join([s for s in summary["result"].splitlines() if s])
#         jobDesc+=summary+'\n\n'+footer
#         docList=[]


#     # Perform a search for the query
#     #results = es.searchDocuments(q)
#     # docList = results['docList']
#     # summary = results['Summary']
#     #print(results)
#     # Stream the search results to the client
#     #result =os.linesep.join([s for s in jobDesc.splitlines() if s])
#     json_prompt_template = """Respond in JSON for the below.\n
#                               -----------------------\n """+jobDesc+"""\n
#                               -----------------------"""
#     jsonResp=vllm(prompt=json_prompt_template)
#     with open(JSON_FOLDER_PATH+'jobDesc.json', "w+") as file_object:
#         file_object.write(jsonResp)

#     #print('result: '+result)
#     async def stream_response():
#         for hit in docList:
#             print(hit)
#             yield "data: " + json.dumps(hit) + "\n\n"
#         yield "data:"+json.dumps(jobDesc)+"\n\n"
#         yield "[DONE]"

#     return StreamingResponse(stream_response(), media_type="text/event-stream")



# @general_pages_router.post("/jdreplace")
# async def jdreplace(file: UploadFile = File(...),aiengine:str=Form(...)):
  
#     #file.save(app.config['UPLOAD_FOLDER_PATH']+'datafile.pdf')
#     with open(UPLOAD_FOLDER_PATH+file.filename, "wb+") as file_object:
#         file_object.write(file.file.read())
    
#     loader = PyPDFLoader(UPLOAD_FOLDER_PATH+file.filename)
#     pages = loader.load_and_split()

#     print(aiengine)
#     vllm = VertexAI(model_name="text-bison@001")
#     if aiengine=='OPENAI':
        
#         embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", chunk_size=1)
#         faissIndex = FAISS.from_documents(pages, embeddings)

#         docs = faissIndex.similarity_search("projects worked")

#         llm = AzureOpenAI(
#                     deployment_name=OPENAI_DEPLOYMENT, 
#                     model_name=OPENAI_MODEL,
#                     temperature=0,
#                     openai_api_version=OPENAI_API_VERSION)
#         chain = load_qa_chain(llm, chain_type="stuff")
#         skills=chain.run(input_documents=docs, question="skills")
#         domain=chain.run(input_documents=docs, question="domain experience,total experience")
#         responsibility=chain.run(input_documents=docs, question="summary, responsibilities")
#         context = responsibility+' '+domain+' ' +skills 
                
#         header_prompt = """Use the context to prepare a summarised job description for Capgemini in 100 words.\n\n
#                             Context: \n """+context+"""?\n
#                             Answer:
#                             """
        
#         jobDesc=llm(prompt=header_prompt)    
    
#         job_prompt = """As an executive recruiter working for Capgemini, use the context to prepare answer.\n
#                         Create Job title, years of experience, Key Responsibilities and required skills sections.\n\n
#                         Context: \n"""+context+"""\n
#                         Answer:
#                         """
#         summary=llm(prompt=job_prompt)
#         summary = os.linesep.join([s for s in summary.splitlines() if s])
#         footer=llm(prompt=footer_prompt_template)
#         jobDesc =jobDesc+'\n\n'+ summary+'\n\n'+footer
    
#     else:
#         vertex_embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@001")
#         faissIndex = FAISS.from_documents(pages, vertex_embeddings)
#         docs = faissIndex.similarity_search("projects worked")
#         chain = load_qa_chain(vllm, chain_type="stuff")
#         skills=chain.run(input_documents=docs, question="skills")
#         domain=chain.run(input_documents=docs, question="domain experience,total experience")
#         responsibility=chain.run(input_documents=docs, question="summary, responsibilities")
#         context = responsibility+' '+domain+' ' +skills 
#         header_prompt = """Use the context to prepare a summarised job description for Cagpgemini in 100 words.\n\n
#                     Context: \n """+context+"""?\n
#                     Answer:
#                     """

#         jobHeader=vllm(prompt=header_prompt)    
    
#         job_prompt = """As an executive recruiter working for Capgemini, use the context to prepare answer.\n
#                         Create Job title, years of experience, Key Responsibilities and required skills sections.\n\n
#                         Context: \n"""+context+"""\n
#                         Answer:
#                         """
#         summary=vllm(prompt=job_prompt)
#         summary=os.linesep.join([s for s in summary.splitlines() if s])
#         footer=vllm(prompt=footer_prompt_template)
#         jobDesc =jobHeader+'\n\n'+ summary+'\n\n'+footer

#     json_prompt_template = """Respond in JSON for the below.\n
#                         -----------------------\n """+jobDesc+"""\n
#                         -----------------------"""
#     jsonResp=vllm(prompt=json_prompt_template)
#     with open(JSON_FOLDER_PATH+'jobDesc.json', "w+") as file_object:
#         file_object.write(jsonResp)

#     return {"response":jobDesc}


# @general_pages_router.get("/modify")
# async def search(q: str):

#     splitstr = q.split('###')
    
#     modifyStr = splitstr[0]
#     jobDesc = splitstr[1]
    
    
#     headerDesc=re.split(r'(?:\r?\n){2,}',jobDesc)

#     print(headerDesc[1])
#     ####SECTION FOR PROMPT TEMPLATE###
#     header_prompt_template = """Modify as per the question\n
#                              Question: """+modifyStr+""" \n
#                              -----------\n"""+headerDesc[0]+"""\n
#                              ------------"""

#     job_prompt_template = """Keep content as provided. Only modify or add as per question\n
#                              Question: """+modifyStr+""" \n
#                             -----------\n"""+headerDesc[1]+"""\n
#                             ------------"""

#     #####
    
#     llm = AzureChatOpenAI(
#                 openai_api_base=OPENAI_API_BASE,
#                 deployment_name=OPENAI_DEPLOYMENT, 
#                 model_name=OPENAI_MODEL,
#                 temperature=1,
#                 openai_api_version=OPENAI_API_VERSION,
#                 openai_api_type="azure")

#     msg = HumanMessage(content=header_prompt_template)
#     headerSection=llm(messages=[msg]).content

#     msg = HumanMessage(content=job_prompt_template)
#     jobDescSection=llm(messages=[msg]).content

#     msg = HumanMessage(content=footer_prompt_template_1)
#     lacSection= llm(messages=[msg]).content

#     jobDesc=headerSection+'\n\n'+jobDescSection+'\n\n'+lacSection

#     async def stream_response():
#         yield "data:"+json.dumps(jobDesc)+"\n\n"
#         yield "[DONE]"

#     return StreamingResponse(stream_response(), media_type="text/event-stream")