import json
import re
import os
import logging
import google.generativeai as genai
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from api.models.user_assesment import UserAssessment, ASSESSMENT_QUESTIONS, DEFAULT_LANGUAGE
from api.models.conversation import ConversationType

class AdvisorService:
    """Service to handle AI advisor logic, including prompt engineering and response processing."""

    # Language instruction mapping
    LANGUAGE_INSTRUCTIONS = {
        'uk': 'ВАЖЛИВО: Відповідайте українською мовою.',
        'en': 'IMPORTANT: Respond in English.',
        'ru': 'ВАЖНО: Отвечайте на русском языке.',
    }

    @staticmethod
    def _get_language_instruction(assessment):
        """Get language instruction based on user's preferred language."""
        if assessment and assessment.preferred_language:
            return AdvisorService.LANGUAGE_INSTRUCTIONS.get(
                assessment.preferred_language, 
                AdvisorService.LANGUAGE_INSTRUCTIONS[DEFAULT_LANGUAGE]
            )
        return AdvisorService.LANGUAGE_INSTRUCTIONS[DEFAULT_LANGUAGE]

    # System prompts for each conversation type
    SYSTEM_PROMPTS = {
        'assessment': """
Ви — кар'єрний радник для українського ветерана, що переходить до цивільної кар'єри.
Користувач ще НЕ обрав конкретний кар'єрний шлях. Ваша задача — опитати його щоб заповнити профіль оцінювання.
Будьте доброзичливими, підтримуючими та поважайте конфіденційність користувача.
""",
        ConversationType.HIRING: """
Ви — кар'єрний радник для українського ветерана, що шукає найману роботу.

ВАШІ ОСНОВНІ ЗАВДАННЯ:
1. Уточніть, яку позицію шукає користувач (якщо ще не визначено)
2. Проаналізуйте досвід користувача з профілю оцінювання
3. Допоможіть створити або покращити резюме
4. Надайте стратегії пошуку роботи
5. Підготуйте до співбесід
6. Поділіться інсайтами про ринок праці

ВАЖЛИВО: Використовуйте інформацію з профілю користувача для персоналізованих порад.
Якщо користувач ділиться новою важливою інформацією про себе, видайте JSON-блок з оновленнями.
""",
        ConversationType.SELF_EMPLOYMENT: """
Ви — кар'єрний радник для українського ветерана, що хоче стати самозайнятим/фрілансером.

ВАШІ ОСНОВНІ ЗАВДАННЯ:
1. Уточніть, в якій сфері користувач хоче працювати як фрілансер
2. Проаналізуйте досвід та навички з профілю оцінювання
3. Допоможіть побудувати портфоліо
4. Надайте поради щодо пошуку клієнтів
5. Поясніть юридичні та податкові аспекти
6. Допоможіть з ціноутворенням послуг

ВАЖЛИВО: Використовуйте інформацію з профілю користувача для персоналізованих порад.
Якщо користувач ділиться новою важливою інформацією про себе, видайте JSON-блок з оновленнями.
""",
        ConversationType.BUSINESS: """
Ви — кар'єрний радник та бізнес-консультант для українського ветерана, що хоче розпочати власний бізнес.

ВАШІ ОСНОВНІ ЗАВДАННЯ:
1. ЖОРСТКО ВАЛІДУЙТЕ бізнес-ідеї на основі економіки та бізнес-логіки
2. Враховуйте досвід та навички користувача з профілю оцінювання
3. Аналізуйте ринок та конкурентів
4. Оцінюйте фінансову життєздатність ідеї
5. Вказуйте на потенційні ризики та виклики
6. Допомагайте розробити реалістичний бізнес-план

КРИТЕРІЇ ВАЛІДАЦІЇ ІДЕЇ:
- Чи є реальний попит на ринку?
- Чи має користувач необхідні навички/ресурси?
- Чи фінансово життєздатна ідея?
- Які основні ризики та як їх мітигувати?
- Чи реалістичні очікування користувача?

ВАЖЛИВО: 
- Будьте чесними і реалістичними, навіть якщо доведеться відхилити ідею
- Використовуйте дані з профілю для оцінки відповідності
- Якщо користувач ділиться новою інформацією, видайте JSON-блок з оновленнями
""",
        ConversationType.EDUCATION: """
Ви — кар'єрний радник та навчальний консультант для українського ветерана.

ВАШІ ОСНОВНІ ЗАВДАННЯ:
1. Допомагайте знайти релевантні навчальні матеріали
2. Використовуйте базу знань для надання точної інформації
3. Рекомендуйте курси та ресурси
4. Створюйте навчальні плани
5. Відстежуйте прогрес

ВАЖЛИВО:
- Використовуйте доступні статті та документи з бази знань
- Цитуйте джерела
- Якщо користувач ділиться новою інформацією про навички чи інтереси, видайте JSON-блок
""",
        ConversationType.CAREER_PATH: """
Ви — кар'єрний радник, що допомагає українському ветерану обрати кар'єрний шлях.

ВАШІ ОСНОВНІ ЗАВДАННЯ:
1. Оцініть навички та досвід користувача
2. Дослідіть різні кар'єрні опції
3. Зрозумійте переваги та недоліки кожного шляху
4. Допоможіть прийняти обґрунтоване рішення

ВАЖЛИВО: Використовуйте профіль користувача для об'єктивних рекомендацій.
Якщо користувач ділиться новою інформацією, видайте JSON-блок з оновленнями.
"""
    }

    @staticmethod
    def get_ai_response(user, conversation, user_content, file_content=None):
        """
        Generates a response from the AI advisor.
        Returns the text response.
        """
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return f"(LLM не налаштовано) Ехо: {user_content}"

        try:
            genai.configure(api_key=api_key)
            model_name = getattr(settings, 'GOOGLE_LLM_MODEL', 'models/gemini-2.5-flash.5-flash')
            
            # Get or create assessment for the user
            try:
                assessment, _ = UserAssessment.objects.get_or_create(user=user)
            except MultipleObjectsReturned:
                assessments = UserAssessment.objects.filter(user=user).order_by('-updated_at')
                assessment = assessments.first()
            
            # Fetch conversation history
            from api.models.message import Message
            recent_messages = conversation.messages.order_by('-created_at')[:10]
            recent_messages = reversed(recent_messages)
            
            history_text = ""
            for msg in recent_messages:
                role = "Користувач" if msg.is_user else "Радник"
                history_text += f"{role}: {msg.content}\n"

            # Build the prompt
            build_result = AdvisorService._build_prompt(
                user, 
                assessment, 
                conversation, 
                history_text, 
                user_content,
                file_content
            )
            
            # Handle different return types
            if isinstance(build_result, tuple):
                full_prompt, direct_response = build_result
                if direct_response:
                    return direct_response
            else:
                full_prompt = build_result
            
            # Call LLM
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(full_prompt)

            if not response.parts:
                return "(Немає відповіді — ймовірно, заблоковано фільтрами безпеки)"

            raw_ai_text = response.text

            # Process response - ALWAYS extract JSON updates if present
            final_text = AdvisorService._process_response(assessment, raw_ai_text)

            return final_text

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception('Error in AdvisorService.get_ai_response')
            err_text = str(e)
            return f"(Помилка LLM) {err_text}"

    @staticmethod
    def get_ai_response_stream(user, conversation, user_content, file_content=None):
        """
        Generates a streaming response from the AI advisor.
        Yields chunks of text.
        """
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            sample = user_content[:1000]
            yield f"(LLM не налаштовано) Ехо: {sample}"
            return

        try:
            genai.configure(api_key=api_key)
            model_name = getattr(settings, 'GOOGLE_LLM_MODEL', 'models/gemin-2.5-flash')
            
            # Get or create assessment for the user
            try:
                assessment, _ = UserAssessment.objects.get_or_create(user=user)
            except MultipleObjectsReturned:
                assessments = UserAssessment.objects.filter(user=user).order_by('-updated_at')
                assessment = assessments.first()
            
            # Fetch conversation history
            from api.models.message import Message
            recent_messages = conversation.messages.order_by('-created_at')[:10]
            recent_messages = reversed(recent_messages)
            
            history_text = ""
            for msg in recent_messages:
                role = "Користувач" if msg.is_user else "Радник"
                history_text += f"{role}: {msg.content}\n"

            # Build the prompt
            build_result = AdvisorService._build_prompt(
                user, 
                assessment, 
                conversation, 
                history_text, 
                user_content,
                file_content
            )
            
            # Handle different return types
            if isinstance(build_result, tuple):
                full_prompt, direct_response = build_result
                if direct_response:
                    yield direct_response
                    return
            else:
                full_prompt = build_result
            
            # Call LLM with streaming
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(full_prompt, stream=True)

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception('Error in AdvisorService.get_ai_response_stream')
            yield f"(Помилка LLM) {str(e)}"

    @staticmethod
    def _build_prompt(user, assessment, conversation, history_text, user_content, file_content=None):
        """Build prompt based on conversation type or assessment state."""
        
        # If user hasn't selected career and conversation has no type, use assessment mode
        if not user.career_selected and not conversation.conv_type:
            return AdvisorService._build_assessment_prompt(assessment, history_text, user_content)
        
        # Otherwise, use conversation type specific prompt
        conv_type = conversation.conv_type
        system_prompt = AdvisorService.SYSTEM_PROMPTS.get(
            conv_type, 
            AdvisorService.SYSTEM_PROMPTS[ConversationType.CAREER_PATH]
        )

        # Append file content if present
        if file_content:
            user_content = f"{user_content}\n\n[ВКЛАДЕНИЙ ФАЙЛ]:\n{file_content}\n[КІНЕЦЬ ФАЙЛУ]"
        
        # For EDUCATION type, use RAG
        if conv_type == ConversationType.EDUCATION:
            return AdvisorService._build_education_prompt(
                system_prompt,
                assessment, 
                history_text, 
                user_content
            )
        
        # For BUSINESS type, add validation instructions
        if conv_type == ConversationType.BUSINESS:
            return AdvisorService._build_business_prompt(
                user,
                system_prompt,
                assessment,
                history_text,
                user_content
            )
        
        # For other types, build standard prompt
        return AdvisorService._build_typed_prompt(
            system_prompt,
            conv_type,
            assessment,
            history_text,
            user_content
        )

    @staticmethod
    def _build_assessment_prompt(assessment, history_text, user_content):
        """Build prompt for initial assessment phase."""
        system_prompt = AdvisorService.SYSTEM_PROMPTS['assessment']
        # Determine next unanswered question (in order)
        answers = assessment.answers or {}
        next_q = None
        for q in ASSESSMENT_QUESTIONS:
            qid = q.get('id')
            if qid not in answers or answers.get(qid) in (None, '', []):
                next_q = q
                break

        # If all questions answered, return a prompt that acknowledges completion
        if not next_q:
            prompt = f"{system_prompt}\nВиглядає так, що профіль оцінювання вже заповнений. Підтвердіть, якщо потрібно оновити дані або продовжити розмову. Повідомлення користувача: {user_content}"
            return prompt

        # Build a focused prompt that asks ONLY the next question and instructs the LLM
        current_answers_json = json.dumps(answers, indent=2, ensure_ascii=False)
        question_text = next_q.get('question')
        question_id = next_q.get('id')

        prompt = f"""{system_prompt}

ПОТОЧНИЙ СТАН ОЦІНЮВАННЯ (JSON):
{current_answers_json}

НАСТУПНЕ ПИТАННЯ (тільки ОДНЕ):
ID: {question_id}
Питання: {question_text}

ІНСТРУКЦІЇ ДЛЯ МОДЕЛІ:
1) Проаналізуйте останнє повідомлення користувача ("{user_content}"). Якщо воно містить відповідь на вищезгадане питання — ВИПИШІТЬ ЛИШЕ JSON-блок на початку відповіді у форматі:
```json
{{
    "updates": {{
        "{question_id}": "extracted answer value"
    }}
}}
```
2) Якщо користувач не дав відповіді на це питання, НЕ надавайте жодних інших питань і дайте лише коротку підказку (1-2 речення), щоб уточнити.
3) НЕ ЗАДАВАЙТЕ декілька питань одночасно. Задавайте ТІЛЬКИ вказане питання або просіть уточнення.
4) Після JSON-блоку (якщо він є) — підтвердіть отримані дані коротко і не додавайте інші питання.

ІСТОРІЯ РОЗМОВИ:
{history_text}

Повідомлення користувача: {user_content}
"""
        return prompt

    @staticmethod
    def _build_typed_prompt(system_prompt, conv_type, assessment, history_text, user_content):
        """Build prompt for specific conversation type with assessment context."""
        
        # Add user context from assessment
        user_context = AdvisorService._format_assessment_context(assessment)
        
        # Get language instruction
        lang_instruction = AdvisorService._get_language_instruction(assessment)
        
        # Add JSON extraction instructions for ALL conversation types
        json_instructions = """

ОНОВЛЕННЯ ПРОФІЛЮ КОРИСТУВАЧА:
Якщо користувач надає нову важливу інформацію (навички, досвід, освіта, цілі, обмеження тощо), 
ВИ МАЄТЕ видати JSON-блок НА ПОЧАТКУ відповіді:
```json
{{
    "updates": {{
        "field_id": "нове значення"
    }}
}}
```

Можливі поля: primary_skills, experience_level, current_goals, long_term_goals, work_preferences, 
locality, civilian_certifications, education_level, disabilities_or_limits, support_needs та інші з оцінювання.
"""
        
        prompt = f"""{system_prompt}

{lang_instruction}

{user_context}
{json_instructions}

ІСТОРІЯ РОЗМОВИ:
{history_text}

Повідомлення користувача: {user_content}

Надайте корисну, практичну відповідь відповідно до вашої ролі.
"""
        return prompt

    @staticmethod
    def _build_business_prompt(user, system_prompt, assessment, history_text, user_content):
        """Build enhanced prompt for business validation with multi-step chain support."""
        
        user_context = AdvisorService._format_assessment_context(assessment)
        
        try:
            from api.models.business import BusinessIdea
            from api.services.langchain_service import BusinessValidationChain
            
            # 1. Find active business idea
            active_idea = BusinessIdea.objects.filter(
                user=user, 
                status__in=['BRAINSTORM', 'IN_PROGRESS']
            ).order_by('-updated_at').first()

            # 2. Check for new idea creation intent
            validation_keywords = ['ідея', 'бізнес', 'відкрити', 'запустити', 'стартап', 'хочу']
            user_content_lower = user_content.lower()
            is_new_idea = any(k in user_content_lower for k in validation_keywords) and len(user_content) > 15

            chain = BusinessValidationChain()

            # CASE A: Start new validation
            if not active_idea and is_new_idea:
                # Create new idea
                active_idea = BusinessIdea.objects.create(
                    user=user,
                    title=user_content[:100],
                    status='IN_PROGRESS',
                    business_canvas={'raw_idea': user_content}
                )
                # Run Step 1: Market
                analysis = chain.validate_market(user_content)
                active_idea.market_analysis = analysis
                active_idea.save()
                
                response = f"💡 **Крок 1: Аналіз Ринку**\n\n{analysis}\n\n🤔 **Що скажете?** Переходимо до фінансового аналізу?"
                return None, response

            # CASE B: Continue validation
            if active_idea:
                # Check for "next step" intent
                next_keywords = ['так', 'далі', 'продовжуй', 'фінанс', 'наступн', 'ok', 'добре', 'yes', 'next', 'ага', 'плюс', '+']
                wants_next = any(k in user_content_lower for k in next_keywords)
                
                raw_idea = active_idea.business_canvas.get('raw_idea', active_idea.title)

                # Step 2: Financials
                if not active_idea.financial_analysis:
                    if wants_next:
                        analysis = chain.validate_financials(raw_idea, active_idea.market_analysis)
                        active_idea.financial_analysis = analysis
                        active_idea.save()
                        return None, f"💰 **Крок 2: Фінансовий Аналіз**\n\n{analysis}\n\n🤔 **Як вам цифри?** Переходимо до оцінки навичок?"
                    # Else: fall through to discuss market analysis

                # Step 3: Skills
                elif not active_idea.skills_match:
                    if wants_next:
                        analysis = chain.validate_skills(raw_idea, user_context)
                        active_idea.skills_match = analysis
                        active_idea.save()
                        return None, f"🛠 **Крок 3: Відповідність Навичок**\n\n{analysis}\n\n🤔 **Чи згодні ви з оцінкою?** Переходимо до ризиків?"

                # Step 4: Risks
                elif not active_idea.risk_assessment:
                    if wants_next:
                        analysis = chain.validate_risks(
                            raw_idea,
                            active_idea.market_analysis,
                            active_idea.financial_analysis,
                            active_idea.skills_match
                        )
                        active_idea.risk_assessment = analysis
                        active_idea.save()
                        return None, f"⚠️ **Крок 4: Оцінка Ризиків**\n\n{analysis}\n\n🤔 **Чи готові почути фінальний вердикт?**"

                # Step 5: Verdict
                elif not active_idea.final_verdict:
                    if wants_next:
                        analysis = chain.validate_verdict(
                            raw_idea,
                            active_idea.market_analysis,
                            active_idea.financial_analysis,
                            active_idea.skills_match,
                            active_idea.risk_assessment
                        )
                        active_idea.final_verdict = analysis
                        active_idea.status = 'VALIDATED'
                        active_idea.save()
                        return None, f"✅ **Фінальний Вердикт**\n\n{analysis}\n\n🎉 **Валідацію завершено!**"

            # Inject context if we are in a validation flow but not advancing
            context_injection = ""
            if active_idea:
                context_injection = f"""
ПОТОЧНИЙ СТАН ВАЛІДАЦІЇ БІЗНЕСУ (Ідея: {active_idea.title}):
1. Ринок: {'✅ ' + active_idea.market_analysis[:50] + '...' if active_idea.market_analysis else '⏳ Очікується'}
2. Фінанси: {'✅ ' + active_idea.financial_analysis[:50] + '...' if active_idea.financial_analysis else '⏳ Очікується'}
3. Навички: {'✅ ' + active_idea.skills_match[:50] + '...' if active_idea.skills_match else '⏳ Очікується'}
4. Ризики: {'✅ ' + active_idea.risk_assessment[:50] + '...' if active_idea.risk_assessment else '⏳ Очікується'}
5. Вердикт: {'✅ ' + active_idea.final_verdict[:50] + '...' if active_idea.final_verdict else '⏳ Очікується'}

ВАЖЛИВО: Користувач зараз знаходиться на певному етапі. Відповідайте на його питання. 
Якщо він погоджується або каже "далі" — це сигнал для переходу до наступного кроку (який обробить система).
"""
                return f"{system_prompt}\n{context_injection}\n{history_text}\nПовідомлення користувача: {user_content}"

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception('Validation error in _build_business_prompt')
            # Fallback if LangChain fails or imports fail
            pass
        
        # Standard business validation prompt (fallback)
        validation_framework = """

ФРЕЙМВОРК ВАЛІДАЦІЇ БІЗНЕС-ІДЕЇ:

1. АНАЛІЗ РИНКУ:
   - Чи існує реальний попит?
   - Хто цільова аудиторія?
   - Наскільки великий ринок?
   - Хто конкуренти?

2. ОЦІНКА НАВИЧОК ТА РЕСУРСІВ:
   - Чи має користувач необхідні навички? (перевірте профіль)
   - Чи достатньо досвіду?
   - Які ресурси потрібні (фінанси, обладнання, люди)?
   - Що можна використати з існуючого досвіду?

3. ФІНАНСОВА ЖИТТЄЗДАТНІСТЬ:
   - Скільки коштує запуск?
   - Які постійні витрати?
   - Реалістична модель доходів?
   - Коли досягнення беззбитковості?
   - ROI та період окупності?

4. АНАЛІЗ РИЗИКІВ:
   - Основні виклики та ризики?
   - План мітигації ризиків?
   - План Б якщо не спрацює?

5. РЕАЛІСТИЧНІСТЬ ОЧІКУВАНЬ:
   - Чи реалістичні фінансові прогнози?
   - Чи враховано час на розвиток?
   - Чи готовий користувач до викликів?

БУДЬТЕ ЧЕСНИМИ: Якщо ідея має критичні недоліки, вкажіть на них прямо.
Надайте конструктивну критику та альтернативи.
"""

        json_instructions = """

ОНОВЛЕННЯ ПРОФІЛЮ:
Якщо користувач надає нову інформацію про досвід, навички чи бізнес-ідею, видайте JSON:
```json
{{
    "updates": {{
        "field_id": "value"
    }}
}}
```
"""
        
        prompt = f"""{system_prompt}
{user_context}
{validation_framework}
{json_instructions}

ІСТОРІЯ РОЗМОВИ:
{history_text}

Повідомлення користувача: {user_content}

Проаналізуйте та надайте чесну, обґрунтовану оцінку з використанням фреймворку валідації.
"""
        return prompt, None  # Return prompt, no direct response


    @staticmethod
    def _build_education_prompt(system_prompt, assessment, history_text, user_content):
        """Build prompt for education/learning mode with RAG (vector or keyword)."""
        
        # Try vector RAG first (OPTIONAL - falls back to keyword if unavailable)
        relevant_docs = None
        knowledge_context = "" # Initialize knowledge_context
        try:
            from api.services.langchain_service import VectorRAG
            
            vector_rag = VectorRAG()
            vector_rag.initialize_vectorstore()
            results = vector_rag.search(user_content, k=3)
            
            if results:
                # Format vector search results
                knowledge_context = vector_rag.format_rag_context(results)
            else:
                # No results from vector search, try keyword
                relevant_docs = AdvisorService._search_knowledge_base(user_content)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception('Vector RAG initialization/search failed; falling back to keyword search')
            # Vector RAG not available, use keyword search
            relevant_docs = AdvisorService._search_knowledge_base(user_content)
        
        # If using keyword search (fallback)
        if relevant_docs:
            knowledge_context = "\n\nРЕЛЕВАНТНІ МАТЕРІАЛИ З БАЗИ ЗНАНЬ:\n"
            for doc in relevant_docs:
                knowledge_context += f"\n[{doc['type'].upper()}] {doc['title']}\n"
                knowledge_context += f"Зміст: {doc['summary']}\n"
                if doc['url']:
                    knowledge_context += f"URL: {doc['url']}\n"
        elif not knowledge_context: # Only if vector RAG also didn't find anything
            knowledge_context = "\n\nМатеріали з бази знань не знайдено по цьому запиту.\n"
        
        user_context = AdvisorService._format_assessment_context(assessment)
        
        json_instructions = """

ОНОВЛЕННЯ ПРОФІЛЮ:
Якщо користувач розповідає про нові навички, інтереси або навчальні цілі, видайте JSON:
```json
{{
    "updates": {{
        "field_id": "value"
    }}
}}
```
"""
        
        prompt = f"""{system_prompt}
{user_context}
{knowledge_context}
{json_instructions}

ІСТОРІЯ РОЗМОВИ:
{history_text}

Повідомлення користувача: {user_content}

Використовуйте матеріали з бази знань для точних відповідей. Цитуйте джерела.
"""
        return prompt

    @staticmethod
    def _format_assessment_context(assessment):
        """Format assessment data for LLM context."""
        if not assessment or not assessment.answers:
            return "\n\nПРОФІЛЬ КОРИСТУВАЧА: Дані ще не заповнені.\n"
        
        context_parts = ["\n\nПРОФІЛЬ КОРИСТУВАЧА:"]
        
        # Key fields to highlight
        if assessment.service_branch:
            context_parts.append(f"- Військова спеціальність: {assessment.service_branch}")
        if assessment.service_role:
            context_parts.append(f"- Військова роль: {assessment.service_role}")
        if assessment.years_of_service:
            context_parts.append(f"- Років служби: {assessment.years_of_service}")
        if assessment.primary_skills:
            context_parts.append(f"- Основні навички: {assessment.primary_skills}")
        if assessment.education_level:
            context_parts.append(f"- Освіта: {assessment.education_level}")
        if assessment.work_preferences:
            context_parts.append(f"- Робочі переваги: {assessment.work_preferences}")
        
        # Goals
        current_goals = assessment.answers.get('current_goals')
        if current_goals:
            context_parts.append(f"- Короткострокові цілі: {current_goals}")
        long_term = assessment.answers.get('long_term_goals')
        if long_term:
            context_parts.append(f"- Довгострокові цілі: {long_term}")
        
        # Add other important fields
        if assessment.leadership_experience:
            context_parts.append("- Має досвід лідерства")
        if assessment.civilian_certifications:
            context_parts.append(f"- Сертифікації: {assessment.civilian_certifications}")
        if assessment.locality:
            context_parts.append(f"- Регіон: {assessment.locality}")
        
        return "\n".join(context_parts) + "\n"

    @staticmethod
    def _search_knowledge_base(query, max_results=3):
        """Search for relevant documents and articles in the knowledge base."""
        try:
            from api.models.knowledge import KnowledgeDocument
            from api.models.article import Article
            from django.db.models import Q
            
            # Simple keyword search
            search_terms = query.lower().split()[:3]
            
            results = []
            
            # Search in KnowledgeDocuments
            q_objects = Q()
            for term in search_terms:
                q_objects |= Q(title__icontains=term) | Q(raw_text_content__icontains=term)
            
            docs = KnowledgeDocument.objects.filter(q_objects).distinct()[:max_results]
            
            for doc in docs:
                content_snippet = doc.raw_text_content[:300] + "..." if len(doc.raw_text_content) > 300 else doc.raw_text_content
                results.append({
                    'title': doc.title,
                    'summary': content_snippet,
                    'url': doc.source_url or '',
                    'type': 'document'
                })
            
            # Also search in published Articles
            if len(results) < max_results:
                remaining = max_results - len(results)
                q_articles = Q(is_published=True)
                for term in search_terms:
                    q_articles &= Q(title__icontains=term) | Q(content__icontains=term)
                
                articles = Article.objects.filter(q_articles).distinct()[:remaining]
                
                for article in articles:
                    content_snippet = article.content[:300] + "..." if len(article.content) > 300 else article.content
                    results.append({
                        'title': article.title,
                        'summary': content_snippet,
                        'url': f'/articles/{article.slug}',
                        'type': 'article'
                    })
            
            return results
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception('Error searching knowledge base')
            return []

    @staticmethod
    def _process_response(assessment, raw_text):
        """
        Parses the raw LLM response for JSON updates, applies them to the assessment,
        and returns the clean text to show to the user.
        Works for ALL conversation types now, not just assessment mode.
        """
        # Parse for JSON updates
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_text, re.DOTALL)

        if not json_match:
            return raw_text

        # Always try to strip the JSON block first so the user doesn't see it
        clean_text = raw_text.replace(json_match.group(0), '').strip()

        try:
            data = json.loads(json_match.group(1))
            updates = data.get('updates', {})
            if updates:
                if not assessment.answers:
                    assessment.answers = {}
                assessment.answers.update(updates)
                assessment.save()

            return clean_text
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception('Failed to parse or save JSON updates from LLM response')
            # Even if saving fails, return the clean text without the JSON block
            return clean_text

    @staticmethod
    def generate_initial_message(user, conversation):
        """
        Generate an initial assistant message for a newly created conversation.
        """
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return "Вітаю! Я ваш кар'єрний радник. Радий(а), що ви тут. Чим можу допомогти?"

        try:
            genai.configure(api_key=api_key)
            model_name = getattr(settings, 'GOOGLE_LLM_MODEL', 'models/gemin-2.5-flash')

            # Get or create assessment
            try:
                assessment, _ = UserAssessment.objects.get_or_create(user=user)
            except MultipleObjectsReturned:
                assessments = UserAssessment.objects.filter(user=user).order_by('-updated_at')
                assessment = assessments.first()

            # Get the appropriate system prompt based on conversation type
            conv_type = conversation.conv_type
            if conv_type and conv_type in AdvisorService.SYSTEM_PROMPTS:
                system_prompt = AdvisorService.SYSTEM_PROMPTS[conv_type]
            else:
                system_prompt = AdvisorService.SYSTEM_PROMPTS['assessment']
            
            # Add user context
            user_context = AdvisorService._format_assessment_context(assessment)
            
            prompt = f"""{system_prompt}
{user_context}

Коротко представтесь і поставте лаконічне вступне питання відповідно до вашої ролі та профілю користувача.
"""

            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)

            if not response.parts:
                return "(Немає відповіді від LLM)"

            return response.text
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception('Error generating initial message from LLM; returning fallback greeting')
            return "Вітаю! Я ваш кар'єрний радник. Радий(а), що ви тут. Чим можу допомогти?"

    @staticmethod
    def generate_conversation_title(conversation):
        """
        Generate a short, descriptive title for the conversation based on the first 3 exchanges.
        Called after the 3rd user message.
        """
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return  # Skip if no LLM configured
        
        try:
            genai.configure(api_key=api_key)
            model_name = getattr(settings, 'GOOGLE_LLM_MODEL', 'models/gemin-2.5-flash')
            
            # Get the first 6 messages (3 user + 3 AI)
            from api.models.message import Message
            messages = conversation.messages.order_by('created_at')[:6]
            
            # Build conversation summary
            conversation_text = ""
            for msg in messages:
                role = "Користувач" if msg.is_user else "Радник"
                # Truncate long messages
                content = msg.content[:200] if len(msg.content) > 200 else msg.content
                conversation_text += f"{role}: {content}\n"
            
            # Get conversation type label
            conv_type_label = ""
            if conversation.conv_type:
                conv_type_label = dict(ConversationType.choices).get(conversation.conv_type, "")
            
            prompt = f"""На основі цієї розмови створіть ДУЖЕ КОРОТКУ назву (максимум 2-3 слова).
Назва має відображати ОСНОВНУ ТЕМУ розмови.

Тип розмови: {conv_type_label or 'Загальна консультація'}

Розмова:
{conversation_text}

ВИМОГИ:
- Максимум 4-5 слів
- Українською мовою
- БЕЗ лапок, БЕЗ префіксів типу "Назва:", просто текст
- Описує СУТЬ розмови (наприклад: "Пошук роботи Python developer", "Валідація ідеї ресторану", "Навчання веб-розробці")

Назва:"""

            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            if response.parts and response.text:
                # Clean up the response
                title = response.text.strip()
                # Remove quotes if present
                title = title.strip('"').strip("'").strip()
                # Limit length
                if len(title) > 60:
                    title = title[:57] + "..."
                
                # Update conversation
                conversation.title = title
                conversation.save(update_fields=['title'])
                
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception('Error generating conversation title')

    @staticmethod
    def generate_resume_content(user, resume, field, context=None):
        """
        Generates content for a specific resume field using AI.
        """
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return "AI configuration missing."

        try:
            genai.configure(api_key=api_key)
            model_name = getattr(settings, 'GOOGLE_LLM_MODEL', 'models/gemin-2.5-flash')
            
            # Get user assessment
            try:
                assessment = UserAssessment.objects.get(user=user)
                assessment_text = f"""
                Skills: {assessment.primary_skills}
                Experience: {assessment.experience_years} years
                Preferences: {assessment.work_preferences}
                """
            except UserAssessment.DoesNotExist:
                assessment_text = "No assessment data available."

            # Build prompt based on field
            prompt = f"""
            You are an expert resume writer helping a Ukrainian veteran transition to a civilian career.
            
            User Profile:
            {assessment_text}
            
            Current Resume Title: {resume.title}
            
            Task: Write a professional and compelling content for the resume field: "{field}".
            """
            
            if context:
                prompt += f"\nContext/Details provided by user: {context}"
                
            if field == 'summary':
                prompt += "\nWrite a professional summary (3-5 sentences) highlighting the user's strengths and career goals."
            elif field == 'experience_description':
                prompt += "\nWrite a concise description of the work experience. Use MAX 3-4 bullet points. Focus on key achievements. Keep it brief."
            elif field == 'skills':
                prompt += "\nList relevant technical and soft skills based on the profile."
            
            prompt += "\nReturn ONLY the content for the field, no explanations or markdown formatting unless requested."

            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            return response.text.strip()

        except Exception as e:
            logging.getLogger(__name__).error(f"Error generating resume content: {e}")
            return "Failed to generate content."
