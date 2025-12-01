# Conversation Integration: Frontend ↔ Backend

## Overview
This document explains how the conversation system is integrated between the Angular frontend and Django backend.

## API Endpoints

### 1. List/Create Conversations
**Endpoint:** `GET/POST /api/v1/conversations`
- **GET**: Returns all conversations for the authenticated user
- **POST**: Creates a new conversation with optional title

### 2. Get Conversation Details
**Endpoint:** `GET /api/v1/conversations/<uuid>`
- Returns conversation details including all messages

### 3. Chat (Send Message)
**Endpoint:** `POST /api/v1/conversations/chat`
- Sends a message and gets AI response
- Creates conversation if `conversation_id` not provided

**Request Body:**
```json
{
  "content": "User message text",
  "conversation_id": "uuid-optional",
  "title": "optional-conversation-title"
}
```

**Response:**
```json
{
  "id": "message-uuid",
  "conversation": "conversation-uuid",
  "content": "AI response text",
  "is_user": false,
  "created_at": "2025-12-01T01:00:00Z"
}
```

## Frontend Flow

### ConversationService (`conversation.service.ts`)

1. **Creating Messages**
   - Calls `POST /conversations/chat`
   - Includes `conversation_id` for existing conversations
   - Omits `conversation_id` for new conversations (backend creates it)

2. **Streaming Simulation**
   - Backend returns complete message
   - Frontend breaks it into chunks for typing effect
   - 20-character chunks with 50ms delay

3. **Getting Conversations**
   - Calls `GET /conversations?page=1&limit=20`
   - Returns list of user's conversations

### Conversation Component (`conversation.ts`)

1. **Message Flow**
   - User types message
   - Message added to local array (optimistic UI)
   - Calls `getMessageResponse()`
   - Displays AI response with streaming effect

2. **New vs Existing Conversations**
   - New: No `conversationId` or first message
   - Existing: Has `conversationId` from route params

## Backend Flow

### ConversationChatView (`conversation.py`)

1. **Request Handling**
   ```python
   conversation_id = request.data.get('conversation_id')
   content = request.data.get('content')
   ```

2. **Conversation Creation/Retrieval**
   - If `conversation_id` provided: fetch existing
   - If not provided: create new conversation

3. **Message Processing**
   - Save user message to database
   - Call `AdvisorService.get_ai_response(user, conv, content)`
   - Save AI response to database
   - Return AI message

### AdvisorService (`advisor.py`)

1. **Context Building**
   - Fetches last 10 messages from conversation
   - Builds conversation history
   - Gets user assessment data

2. **Prompt Engineering**
   - Assessment mode (if `user.career_selected == False`)
   - Career mode (if career selected)
   - Includes conversation history

3. **LLM Integration**
   - Calls Google Gemini API
   - Parses JSON updates (for assessment)
   - Returns clean text response

## Data Models

### Conversation Model
```python
class Conversation(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    title = CharField(max_length=500, blank=True)
    summary_data = JSONField(default=dict)
    created_at = DateTimeField(auto_now_add=True)
    last_active_at = DateTimeField(auto_now=True)
```

### Message Model
```python
class Message(models.Model):
    id = UUIDField(primary_key=True)
    conversation = ForeignKey(Conversation)
    content = TextField()
    is_user = BooleanField()
    context_used = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
```

## Testing the Integration

### 1. Start Frontend (Browser)
Navigate to: `http://localhost:4200/conversation/<any-uuid>`

### 2. Send a Message
- Type: "Hello, I'm a veteran looking for career guidance"
- Click Send

### 3. Expected Backend Flow
1. POST to `/api/v1/conversations/chat`
2. Backend creates new conversation (no ID provided)
3. Saves user message
4. Calls AdvisorService
5. Builds prompt with ASSESSMENT_QUESTIONS
6. Calls Gemini API
7. Saves AI response
8. Returns message to frontend

### 4. Expected Frontend Response
- Typing animation shows AI response
- Response added to message list
- Conversation created in backend

## Environment Variables

### Backend (`dev.env`)
```bash
GOOGLE_API_KEY=your-google-api-key
GOOGLE_LLM_MODEL=gemini-1.5-flash
GOOGLE_LLM_SYSTEM_PROMPT=Optional system prompt
```

### Frontend
```typescript
environment.serverURL = "http://localhost:8080/api/v1"
```

## Common Issues

### 1. 404 on `/conversations/chat`
**Cause:** URL pattern order
**Fix:** Ensure `conversations/chat` comes before `conversations/<uuid>`

### 2. Conversation not persisting
**Cause:** Frontend not passing `conversation_id` on subsequent messages
**Fix:** Check conversation component passes correct ID

### 3. No AI response
**Cause:** Missing `GOOGLE_API_KEY`
**Fix:** Set API key in `dev.env`

### 4. CORS errors
**Cause:** `CORS_ALLOWED_ORIGINS` not including frontend URL
**Fix:** Add `http://localhost:4200` to `settings.py`

## Next Steps

1. **Implement SSE Streaming**
   - Replace simulated streaming with real Server-Sent Events
   - Stream tokens as they arrive from Gemini

2. **Add Conversation Creation UI**
   - Button to create new conversation
   - Title input for conversations

3. **Conversation List Sidebar**
   - Display all user conversations
   - Navigation between conversations

4. **Message History Pagination**
   - Load older messages on scroll
   - Implement cursor-based pagination
