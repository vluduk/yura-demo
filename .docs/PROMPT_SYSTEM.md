# AI Advisor System - Prompt Structure

## Overview

The AI Advisor system now uses conversation-type-specific prompts instead of a separate database model. Each conversation type has its own tailored system prompt that guides the AI's behavior and expertise.

## Conversation Types & Prompts

### 1. **Assessment Mode** (No conversation type selected)
- **When**: User hasn't selected a career path yet
- **Purpose**: Gather user information through conversational assessment
- **Behavior**: 
  - Asks questions from ASSESSMENT_QUESTIONS
  - Extracts answers and stores them in JSON format
  - Guides user toward selecting appropriate career path

### 2. **HIRING** - Наймана праця
- **Focus**: Finding employment
- **Services**:
  - Resume creation and improvement
  - Job search strategies
  - Interview preparation
  - Labor market insights
- **Tone**: Practical and concrete

### 3. **SELF_EMPLOYMENT** - Самозайнятість
- **Focus**: Freelancing and self-employment
- **Services**:
  - Resume/portfolio building
  - Finding freelance opportunities
  - Legal and tax guidance
  - Personal branding
- **Tone**: Practical and concrete
- **Note**: Currently same approach as HIRING

### 4. **BUSINESS** - Власний бізнес
- **Focus**: Starting and running a business
- **Services**:
  - Business idea validation
  - Business plan development
  - Market and competitor analysis
  - Financial planning
  - Funding opportunities
- **Tone**: Practical, realistic, and supportive

### 5. **EDUCATION** - Навчання
- **Focus**: Learning and skill development
- **Services**:
  - Finding relevant learning materials
  - Course recommendations
  - Resource guidance
- **Special Feature**: **RAG (Retrieval-Augmented Generation)**
  - Searches knowledge database for relevant articles and documents
  - Provides accurate information from knowledge base
  - Cites sources when available
- **Tone**: Informative and supportive

### 6. **CAREER_PATH** - Вибір напрямку
- **Focus**: Career path selection
- **Services**:
  - Skills and experience assessment
  - Exploring career options
  - Understanding pros/cons of each path
  - Making informed decisions
- **Tone**: Objective, informative, and supportive

## Chat Title Generation

Conversations now automatically generate titles in the format:
```
{ConversationType Label} - Чат
```

Examples:
- "Власний бізнес - Чат"
- "Навчання - Чат"
- "Наймана праця - Чат"

This happens automatically when a conversation is created with a `conv_type` but no explicit title.

## RAG Implementation (Education Mode)

When `conv_type` is `EDUCATION`, the system:

1. **Searches Knowledge Base**: 
   - Looks for relevant KnowledgeDocuments
   - Searches published Articles
   - Uses keyword matching (3 most important words from query)

2. **Provides Context**:
   - Includes snippets from relevant materials
   - Adds source URLs when available
   - Labels sources as 'document' or 'article'

3. **LLM Integration**:
   - Passes relevant materials to the prompt
   - Instructs LLM to cite sources
   - Ensures accuracy based on knowledge base

### Future Improvements for RAG:
- Implement vector embeddings for semantic search
- Use cosine similarity for better relevance
- Cache frequently accessed documents
- Add relevance scoring

## Code Structure

### AdvisorService Methods

- `get_ai_response()` - Main entry point
- `_build_prompt()` - Routes to appropriate prompt builder
- `_build_assessment_prompt()` - For initial assessment
- `_build_typed_prompt()` - For standard conversation types
- `_build_education_prompt()` - For learning mode with RAG
- `_search_knowledge_base()` - RAG search implementation
- `_process_response()` - Handles JSON updates from assessment

## Prompt Customization

To modify prompts for each conversation type, edit the `SYSTEM_PROMPTS` dictionary in `/backend/src/api/services/advisor.py`:

```python
SYSTEM_PROMPTS = {
    'assessment': "...",
    ConversationType.HIRING: "...",
    ConversationType.SELF_EMPLOYMENT: "...",
    ConversationType.BUSINESS: "...",
    ConversationType.EDUCATION: "...",
    ConversationType.CAREER_PATH: "..."
}
```

## Migration Notes

- Removed Prompt model dependency
- All prompts are now hardcoded in AdvisorService
- Easier to version control
- Faster execution (no database queries for prompts)
- Clear separation of concerns by conversation type
