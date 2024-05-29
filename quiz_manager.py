import streamlit as st
import os
import sys
import json
sys.path.append(os.path.abspath('../../'))
from pdf_processing import DocumentProcessor
from embedding_client import EmbeddingClient
from chroma_collection_creator import ChromaCollectionCreator
from quiz_generator import QuizGenerator

class QuizManager:
    """
    QuizManager class for managing and navigating through a list of quiz questions.

    Attributes:
        questions (list): A list of dictionaries, where each dictionary represents a quiz question along with its choices, correct answer, and an explanation.
        total_questions (int): The total number of quiz questions.
    """
    def __init__(self, questions: list):
        """
        Initializes the QuizManager class with a list of quiz questions.

        :param questions: A list of dictionaries, where each dictionary represents a quiz question along with its choices, correct answer, and an explanation.
        """
        self.questions = questions
        self.total_questions = len(questions)

    def get_question_at_index(self, index: int):
        """
        Retrieves the quiz question object at the specified index. If the index is out of bounds,
        it restarts from the beginning index.

        :param index: The index of the question to retrieve.
        :return: The quiz question object at the specified index, with indexing wrapping around if out of bounds.
        """
        valid_index = index % self.total_questions
        return self.questions[valid_index]
    
    def next_question_index(self, direction=1):
        """
        Adjusts the current quiz question index based on the specified direction.

        :param direction: An integer indicating the direction to move in the quiz questions list (1 for next, -1 for previous).
        """
        if "question_index" not in st.session_state:
            st.session_state["question_index"] = 0
        
        st.session_state["question_index"] = (st.session_state["question_index"] + direction) % self.total_questions


# Test Generating the Quiz
if __name__ == "__main__":
    
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "gemini-quizify-423920",
        "location": "us-central1"
    }
    
    screen = st.empty()
    with screen.container():
        st.header("Quiz Builder")
        processor = DocumentProcessor()
        processor.ingest_documents()
    
        embed_client = EmbeddingClient(**embed_config) 
    
        chroma_creator = ChromaCollectionCreator(processor, embed_client)
    
        question = None
        question_bank = None
    
        with st.form("Load Data to Chroma"):
            st.subheader("Quiz Builder")
            st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
            
            topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
            questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)
            
            submitted = st.form_submit_button("Submit")
            if submitted:
                chroma_creator.create_chroma_collection()
                
                st.write(topic_input)
                
                # Test the Quiz Generator
                generator = QuizGenerator(topic_input, questions, chroma_creator)
                question_bank = generator.generate_quiz()

    if question_bank:
        screen.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            
            quiz_manager = QuizManager(question_bank)  # Use QuizManager class

            # Initialize question_index in session state if not present
            if "question_index" not in st.session_state:
                st.session_state["question_index"] = 0

            # Format the question and display
            with st.form("Multiple Choice Question"):
                index_question = quiz_manager.get_question_at_index(st.session_state["question_index"]) # Use the get_question_at_index method to set the 0th index
                
                # Unpack choices for radio
                choices = []
                for choice in index_question['choices']: # For loop unpack the data structure
                    # Set the key from the index question 
                    key = choice["key"]
                    # Set the value from the index question
                    value = choice["value"]
                    choices.append(f"{key}) {value}")
                
                # Display the question onto streamlit
                st.write(index_question["question"])
                
                answer = st.radio( # Display the radio button with the choices
                    'Choose the correct answer',
                    choices
                )
                st.form_submit_button("Submit")
                
                if submitted: # On click submit 
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key): # Check if answer is correct
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")