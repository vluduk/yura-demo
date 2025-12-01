# Enhanced AI Advisor System - Complete Guide

## Overview

The AI Advisor system now features:
- **Conversation-type-specific prompts** with detailed role instructions
- **User assessment updates across ALL conversation types** (not just assessment mode)
- **Enhanced context awareness** - all responses reference user's profile
- **Business idea validation framework** with economics and logic checks
- **RAG (Retrieval-Augmented Generation)** for Education mode
- **Structured data extraction** using JSON blocks

## Key Features by Conversation Type

### 1. **Assessment Mode** (Initial Evaluation)
- Asks questions from ASSESSMENT_QUESTIONS
- Extracts and stores user information in JSON format
- Guides user through career exploration
- Updates user profile progressively

### 2. **HIRING** - Наймана праця

**Enhanced Features:**
- ✅ **Asks what position the user wants** if not specified
- ✅ **References user experience from assessment** profile
- ✅ **Updates assessment** when user shares new information

**Capabilities:**
- Resume creation and improvement (using user's actual experience)
- Job search strategies tailored to user's skills
- Interview preparation based on target position
- Market insights for specific roles

**Flow:**
1. Check if user has specified target position
2. If not → Ask "Яку позицію ви шукаєте?"
3. Review user's experience from profile
4. Provide personalized advice based on:
   - Military experience → Civilian role translation
   - Skills → Job requirements matching
   - Education → Qualification assessment
   - Location → Local market insights

### 3. **SELF_EMPLOYMENT** - Самозайнятість

**Enhanced Features:**
- ✅ Same as HIRING but for freelance/self-employment
- ✅ Asks about target freelance niche
- ✅ References user skills and experience
- ✅ Updates assessment with new info

**Capabilities:**
- Portfolio building (based on actual skills)
- Finding clients in relevant niche
- Legal and tax guidance
- Pricing strategy based on market and experience level

### 4. **BUSINESS** - Власний бізнес

**Enhanced Features:**
- ✅ **HARD validation of business ideas** using economic/business logic
- ✅ **Takes user experience into account** from assessment
- ✅ Updates assessment with business-related info

**Business Validation Framework:**

#### 1. Market Analysis
- Is there real demand?
- Who is the target audience?
- Market size estimation
- Competitor analysis

#### 2. Skills & Resources Assessment
- Does user have necessary skills? ✓ (checks profile)
- Sufficient experience? ✓ (uses assessment data)
- Required resources (money, equipment, people)
- What can be leveraged from existing experience?

#### 3. Financial Viability
- Startup costs calculation
- Ongoing expenses
- Realistic revenue model
- Break-even analysis
- ROI and payback period

#### 4. Risk Analysis
- Main challenges and risks
- Risk mitigation plan
- Plan B if it doesn't work

#### 5. Reality Check
- Are financial projections realistic?
- Time to develop considered?
- Is user ready for challenges?

**Validation Example:**
```
User: "Хочу відкрити ресторан"

AI Analysis:
✓ Market demand - analyzed
✓ User skills - check profile (has hospitality experience?)
✗ Startup cost - HIGH (~$100k-500k)
✗ Break-even - typically 2-3 years
⚠ Risk - high failure rate (60% in first 3 years)

Honest Feedback: 
"Ідея ресторану має високі початкові витрати та ризики. 
З вашим досвідом у [MILITARY ROLE], розгляньте спочатку:
1. Food truck (lower startup cost)
2. Catering service (flexible, scalable)
3. Work in restaurant first to learn business"
```

### 5. **EDUCATION** - Навчання

**Enhanced Features:**
- ✅ RAG search in knowledge base + articles
- ✅ References user's learning goals from profile
- ✅ Updates assessment with new skills/interests

**RAG Implementation:**
- Searches KnowledgeDocuments and Articles
- Keyword matching (top 3 words from query)
- Provides relevant snippets with sources
- LLM synthesizes information and cites sources

### 6. **CAREER_PATH** - Вибір напрямку

**Features:**
- Career exploration based on user profile
- Objective recommendations using assessment data
- Updates profile as user explores options

## Assessment Updates Across All Modes

### How It Works

**In EVERY conversation type**, the AI now:

1. **Monitors for new information** about the user:
   - Skills, certifications, education
   - Work experience, goals
   - Constraints, preferences
   - Location, availability

2. **Extracts structured data** using JSON:
```json
{
    "updates": {
        "primary_skills": "Python, Django, PostgreSQL",
        "current_goals": "Знайти роботу Python developer",
        "locality": "Київ"
    }
}
```

3. **Automatically updates UserAssessment** model

4. **Uses updated data** in subsequent responses

### Extractable Fields

From ASSESSMENT_QUESTIONS:
- `service_branch`, `service_role`, `rank`
- `years_of_service`, `discharge_date`
- `deployment_experience`, `leadership_experience`
- `primary_skills`, `civilian_certifications`
- `education_level`, `disabilities_or_limits`
- `security_clearance`
- `current_goals`, `long_term_goals`
- `work_preferences`, `financial_needs`
- `locality`, `available_time`
- `benefits_awareness`, `support_needs`
- `additional_info`

### Example Flow (HIRING mode)

```
User: "Я шукаю роботу Python розробника. Маю 2 роки досвіду з Django."

AI Response:
```json
{
    "updates": {
        "primary_skills": "Python, Django",
        "experience_level": "Junior-Middle (2 роки)",
        "current_goals": "Знайти роботу Python розробника"
    }
}
```
[This JSON is hidden from user]

Відмінно! Бачу, ви маєте 2 роки досвіду з Python та Django. 
З вашим військовим досвідом у [MILITARY ROLE FROM PROFILE] та навичками Django,
я рекомендую орієнтуватися на Middle Python Developer позиції...
```

## User Profile Context in Prompts

Every response now **automatically includes** user context:

```
ПРОФІЛЬ КОРИСТУВАЧА:
- Військова спеціальність: Зв'язківець
- Років служби: 5
- Основні навички: Python, Django, PostgreSQL
- Освіта: Bachelors
- Короткострокові цілі: Знайти роботу Python developer
- Регіон: Київ
- Має досвід лідерства
```

This allows the AI to:
- Make **personalized recommendations**
- **Validate ideas** against user's actual skills
- Provide **realistic** career advice
- Identify **skill gaps** and suggest training

## Technical Implementation

### Key Methods

1. `_format_assessment_context(assessment)` 
   - Formats user profile for LLM context
   - Highlights key skills, experience, goals

2. `_process_response(assessment, raw_text)`
   - Extracts JSON updates from ALL responses
   - Updates UserAssessment automatically
   - Removes JSON block before showing to user

3. `_build_business_prompt(...)`
   - Adds validation framework
   - Includes user skills/experience context
   - Emphasizes honest, critical analysis

4. `_build_typed_prompt(...)`
   - Used for HIRING, SELF_EMPLOYMENT, CAREER_PATH
   - Includes user context
   - Adds JSON extraction instructions

### JSON Extraction Pattern

Used in **all conversation types**:

```python
json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
if json_match:
    data = json.loads(json_match.group(1))
    updates = data.get('updates', {})
    assessment.answers.update(updates)
    assessment.save()
```

## LangChain Integration (Future Enhancement)

While the current implementation uses regex for JSON extraction, you can enhance it with LangChain:

### Option 1: Structured Output Parsing
```python
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class AssessmentUpdate(BaseModel):  
    updates: dict[str, str] = Field(description="Assessment fields to update")

parser = PydanticOutputParser(pydantic_object=AssessmentUpdate)
# Use parser in prompt and extraction
```

### Option 2: Business Validation Chain
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

validation_chain = LLMChain(
    llm=gemini_llm,
    prompt=business_validation_template
)
```

### Option 3: RAG with Vector Store
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import GoogleGenerativeAIEmbeddings

# Replace keyword search with semantic search
embeddings = GoogleGenerativeAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)
relevant_docs = vectorstore.similarity_search(query, k=3)
```

## Examples

### HIRING Conversation
```
User: "Привіт, шукаю роботу"
AI: "Вітаю! Бачу з вашого профілю, що ви служили [ROLE] протягом [YEARS] років. 
     Яку саме позицію ви розглядаєте? В якій сфері хочете працювати?"

User: "Хочу бути project manager"
AI: ```json{"updates": {"current_goals": "Project Manager"}}```
    "Чудовий вибір! Ваш досвід лідерства у військах добре перекладається в PM роль.
     Давайте почнемо зі створення резюме. Розкажіть про ваші основні досягнення..."
```

### BUSINESS Conversation with Validation
```
User: "Хочу відкрити онлайн-школу програмування"
AI: ```json{"updates": {"long_term_goals": "Відкрити онлайн-школу програмування"}}```
    
    "Проаналізую вашу ідею:
    
    ✓ РИНОК: Попит зростає, EdTech активно розвивається
    ✓ ВАШІ НАВИЧКИ: Маєте досвід з Python, Django - це плюс
    ⚠ ВИКЛИКИ: 
      - Висока конкуренція (Coursera, Udemy, Prometheus)
      - Потрібні навички: викладання, маркетинг, продаж
      - Початкові витрати: ~$10-20K (платформа, контент, маркетинг)
    
    ✗ КРИТИЧНІ ПИТАННЯ:
      - Чим ваш курс буде кращим за існуючі?
      - Чи маєте досвід викладання?
      - Хто ваша цільова аудиторія?
    
    РЕКОМЕНДАЦІЯ: Почніть з створення 1-2 курсів на існуючих платформах (Udemy).
    Це дасть:
    - Досвід створення контенту
    - Валідацію ідеї
    - Перші продажі без великих інвестицій
    - Розуміння ринку
    
    Як набереться аудиторія - можна думати про власну платформу."
```

## Best Practices

1. **Always include user context** in prompts for personalized advice
2. **Be honest in validations** - better to discourage bad ideas early
3. **Extract incremental information** - update profile as conversation progresses
4. **Reference profile data** explicitly in responses to show understanding
5. **Provide actionable steps** based on user's actual capabilities

## Future Enhancements

1. **Vector embeddings for RAG** - better semantic search
2. **LangChain validation chains** - structured business analysis
3. **Resume builder integration** - auto-generate from profile
4. **Job matching** - match profile to actual vacancies
5. **Learning path generator** - skill gap analysis + course recommendations
