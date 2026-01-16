"""
QuestionTool - Herramienta para responder preguntas usando OpenAI directamente
"""
import os
from openai import OpenAI


class QuestionTool:
    """
    Herramienta simple para responder preguntas usando ChatGPT.
    """
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no configurada")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
    
    def run(self, question: str = None, **kwargs) -> str:
        """
        Responde una pregunta usando ChatGPT.
        
        Args:
            question: La pregunta a responder
            
        Returns:
            str: La respuesta generada por ChatGPT
        """
        if not question:
            question = kwargs.get('query') or kwargs.get('text') or kwargs.get('objective')
        
        if not question:
            return "Error: No se proporcionó ninguna pregunta"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres CODI, un asistente inteligente. Responde de forma clara y concisa."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            return answer
            
        except Exception as e:
            return f"Error al generar respuesta: {str(e)}"
    
    def answer_question(self, question: str) -> dict:
        """
        Alias para mantener compatibilidad con el intent answer_question.
        """
        answer = self.run(question=question)
        return {
            "status": "success",
            "answer": answer,
            "question": question
        }
