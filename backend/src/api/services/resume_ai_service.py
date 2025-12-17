import logging
import google.generativeai as genai
from django.conf import settings
from api.models.user_assesment import UserAssessment

logger = logging.getLogger(__name__)

class ResumeAIService:
    @staticmethod
    def generate_summary(user, resume_data, extra_instructions=None):
        """
        Generates a professional resume summary using Gemini.
        
        Args:
            user: The user requesting the summary.
            resume_data: Dict containing current resume fields (experience, education, etc.).
            extra_instructions: Optional string with user's specific requests.
            
        Returns:
            str: The generated summary.
        """
        try:
            # 1. Configure Gemini
            api_key = getattr(settings, 'GOOGLE_API_KEY', None)
            if not api_key:
                logger.error("GOOGLE_API_KEY not configured")
                return "Error: AI service not configured."
                
            genai.configure(api_key=api_key)
            model_name = getattr(settings, 'GOOGLE_LLM_MODEL', 'gemini-2.5-flash')
            model = genai.GenerativeModel(model_name)

            # 2. Fetch User Assessment
            assessment_text = "Дані оцінювання відсутні."
            preferred_language = "uk"  # Default to Ukrainian
            try:
                assessment = UserAssessment.objects.filter(user=user).latest('created_at')
                if assessment:
                    if assessment.preferred_language:
                        preferred_language = assessment.preferred_language
                    if assessment.answers:
                        formatted_answers = "\n".join([f"- {k}: {v}" for k, v in assessment.answers.items()])
                        assessment_text = f"Дані оцінювання користувача:\n{formatted_answers}"
            except UserAssessment.DoesNotExist:
                pass
            except Exception as e:
                logger.warning(f"Error fetching assessment: {e}")
            
            # Language mapping for prompts
            language_instructions = {
                'uk': 'ВАЖЛИВО: Відповідайте українською мовою.',
                'en': 'IMPORTANT: Respond in English.',
                'ru': 'ВАЖНО: Отвечайте на русском языке.',
            }
            lang_instruction = language_instructions.get(preferred_language, language_instructions['uk'])

            # 3. Format Resume Data
            experience_text = "Досвід роботи:\n"
            experience_entries = resume_data.get('experience_entries') or resume_data.get('experience') or []
            
            for exp in experience_entries:
                experience_text += f"- {exp.get('job_title', 'N/A')} в {exp.get('employer', 'N/A')} ({exp.get('start_date', '')} - {exp.get('end_date', '')})\n"
                if exp.get('description'):
                    experience_text += f"  Опис: {exp.get('description')}\n"
            
            # 4. Construct Prompt
            prompt = f"""
            Ви — експерт зі складання професійних резюме.
            Ваше завдання — написати переконливе професійне резюме (розділ Профіль/Короткий зміст).
            
            {lang_instruction}
            
            КОНТЕКСТ:
            Користувач, ймовірно, є ветераном, який переходить до цивільного життя або шукає нові можливості.
            
            {assessment_text}
            
            {experience_text}
            
            ІНСТРУКЦІЇ КОРИСТУВАЧА:
            {extra_instructions if extra_instructions else "Створіть сильне професійне резюме, підкреслюючи ключові навички та досвід."}
            
            ВИВІД:
            Надайте ТІЛЬКИ текст резюме. Не включайте "Ось резюме" або лапки.
            ЗРОБІТЬ ЙОГО ДУЖЕ КОРОТКИМ І ЛАКОНІЧНИМ. Максимум 3 речення. Без зайвих слів.
            """

            # 5. Call Gemini
            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating resume summary: {e}")
            raise e
