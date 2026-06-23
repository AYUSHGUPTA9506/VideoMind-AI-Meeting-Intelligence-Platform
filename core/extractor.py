#EXTRACT THE BELOW
#Actionableitems - can give some queries of doing specific tasks
#decision
#questions

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.2,
        max_retries=3,
    )

def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200
    )
    return splitter.split_text(transcript)


#system prompt?- each prompt have specific outcomes like actionables,decisions,questions
#In simple terms, this line is a data formatter. It takes a raw string and packages it into a dictionary so that the next step in your LangChain pipeline can read it properly.
def build_chain(system_prompt : str):
    llm = get_llm()
    return (
        RunnablePassthrough() | RunnableLambda(lambda x : {"text" : x}) | ChatPromptTemplate.from_messages([
        ("system",system_prompt),
        ("human","{text}"),
    ]) | llm |StrOutputParser()
    ) 
    
    
def extract_over_chunks(transcript: str, system_prompt: str, merge_prompt: str) -> str:
    chunks = split_transcript(transcript)

    # if transcript is short enough — no chunking needed
    if len(chunks) == 1:
        chain = build_chain(system_prompt)
        return chain.invoke(transcript)

    # Step 1 — extract from each chunk separately
    chain = build_chain(system_prompt)
    chunk_results = [chain.invoke(chunk) for chunk in chunks]

    # Step 2 — merge all results into one final output
    combined = "\n\n".join(chunk_results)
    merge_chain = build_chain(merge_prompt)
    return merge_chain.invoke(combined)
    

def extract_action_items(transcript: str) -> str:
    return extract_over_chunks(
        transcript,
        system_prompt=(
            "You are an expert meeting analyst. From the meeting transcript, "
            "extract all action items. For each provide:\n"
            "- Task description\n"
            "- Owner (who is responsible)\n"
            "- Deadline (if mentioned, else write 'Not specified')\n\n"
            "Format as a numbered list. If none found say 'No action items found.'"
        ),
        merge_prompt=(
            "You are given multiple sets of action items extracted from different "
            "parts of a long meeting. Merge them into one clean, deduplicated "
            "numbered list of action items."
        )
    )


def extract_decisions(transcript: str) -> str:
    return extract_over_chunks(
        transcript,
        system_prompt=(
            "You are an expert meeting analyst. Extract all key decisions made "
            "in this meeting transcript.\n"
            "Format as a numbered list. If none found say 'No decisions found.'"
        ),
        merge_prompt=(
            "You are given decisions extracted from different parts of a long meeting. "
            "Merge them into one clean, deduplicated numbered list of decisions."
        )
    )
    
    
def extract_questions(transcript: str) -> str:
    return extract_over_chunks(
        transcript,
        system_prompt=(
            "You are an expert meeting analyst. Extract all important questions "
            "raised in this meeting transcript.\n"
            "Format as a numbered list. If none found say 'No questions found.'"
        ),
        merge_prompt=(
            "You are given questions extracted from different parts of a long meeting. "
            "Merge them into one clean, deduplicated numbered list of questions."
        )
    )
    









































"""LangChain's ChatPromptTemplate components almost always expect their inputs to be formatted as dictionaries so they know exactly which variables to fill in.

If your prompt template looks like this:
("human", "{text}")

The template will crash if you just hand it a raw string like "Here is the transcript". It doesn't know where that string belongs. By using this line of code, you transform the raw string into {"text": "Here is the transcript"}. When the prompt template sees that dictionary, it knows exactly how to plug it into the {text} placeholder."""