# Conversation Type Integration

## Overview
Successfully integrated conversation type (`conv_type`) throughout the application, allowing users to create different types of conversations (Business, Self-Employment, Hiring, Career Path, Education).

## Changes Made

### Backend

#### 1. Database Model (`conversation.py`)
```python
class Conversation(models.Model):
    # ... existing fields ...
    conv_type = models.CharField(max_length=50, blank=True)
```

#### 2. Migration
- Created: `0005_add_conv_type_to_conversation.py`
- Migration applied successfully

#### 3. Serializer (`conversation.py`)
```python
fields = ('id', 'user', 'title', 'summary_data', 'conv_type', 
          'created_at', 'last_active_at', 'messages')
```

#### 4. View (`conversation.py`)
```python
# In ConversationChatView.post()
conv = Conversation.objects.create(
    user=user, 
    title=request.data.get('title', ''),
    conv_type=request.data.get('conv_type', '')
)
```

Accepts `conv_type` in request body:
```json
{
  "content": "message",
  "conv_type": "Business",
  "title": "optional"
}
```

#### 5. Admin (`registry.py`)
```python
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'conv_type', 'last_active_at')
    search_fields = ('title', 'user__email', 'conv_type')
    list_filter = ('conv_type',)
```

### Frontend

#### 1. TypeScript Type (`ConversationType.ts`)
```typescript
export type ConversationType = {
    id: string;
    title: string;
    conv_type?: ConversationTypeEnum;
    created_at?: Date;
    last_active_at?: Date;
};
```

#### 2. Service (`conversation.service.ts`)

**createConversation:**
```typescript
public async createConversation(
    title?: string, 
    convType?: ConversationTypeEnum
): Promise<ConversationType> {
    const body: any = { title: title || "" };
    if (convType) {
        body.conv_type = convType;
    }
    return await firstValueFrom<ConversationType>(
        this.httpClient.post<ConversationType>(
            environment.serverURL + "/conversations", 
            body
        ),
    );
}
```

**getMessageResponse:**
```typescript
public getMessageResponse(
    conversationId: string,
    messageId: string,
    requestText: string,
    convType?: ConversationTypeEnum,
    file?: File,
): Observable<string> {
    const body: any = { content: requestText };
    
    if (conversationId) {
        body.conversation_id = conversationId;
    }
    
    // Add conv_type for new conversations
    if (convType && !conversationId) {
        body.conv_type = convType;
    }
    // ...
}
```

#### 3. Conversation Component (`conversation.ts`)
```typescript
this.conversationService.getMessageResponse(
    this.currentConversationId(),
    messageId,
    requestText,
    this.currentConversationType() || undefined
).subscribe(/* ... */);
```

#### 4. Conversation Type Page (`conversation-type.ts`)
Already implemented - creates conversations with type via query params:
```typescript
protected createConversation(type: ConversationTypeEnum): void {
    const newId = crypto.randomUUID();
    this.router.navigate(["/conversation", newId], {
        queryParams: { type: type },
    });
}
```

## Conversation Type Enum

The following types are available:

```typescript
export enum ConversationTypeEnum {
    Bussiness = "Bussiness",
    Hiring = "Hiring",
    SelfEmployment = "SelfEmployment",
    Education = "Education",
    CareerPath = "CareerPath",
}
```

## User Flow

### Creating a Typed Conversation

1. **User clicks conversation type button**
   - "Власний бізнес" → `ConversationTypeEnum.Bussiness`
   - "Самозайнятість" → `ConversationTypeEnum.SelfEmployment`
   - "Наймана праця" → `ConversationTypeEnum.Hiring`
   - "Вибір напрямку" → `ConversationTypeEnum.CareerPath`
   - "Навчання" → `ConversationTypeEnum.Education`

2. **Frontend navigates to conversation page**
   - URL: `/conversation/<uuid>`
   - Query params: `?type=<ConversationType>`

3. **User sends first message**
   - Frontend calls: `POST /conversations/chat`
   - Request body includes:
     ```json
     {
       "content": "User's message",
       "conv_type": "Bussiness"
     }
     ```

4. **Backend creates conversation**
   - New `Conversation` record created
   - `conv_type` field populated
   - User message saved
   - AI response generated

5. **Conversation persisted with type**
   - All future messages in this conversation linked to same type
   - Type visible in admin panel
   - Filterable and searchable

## Database Example

After creating conversations:

```
| id   | user | title              | conv_type       | created_at |
|------|------|--------------------|-----------------|------------|
| uuid1| john | Career guidance    | CareerPath      | 2025-12-01 |
| uuid2| jane | Starting business  | Bussiness       | 2025-12-01 |
| uuid3| bob  | Freelance help     | SelfEmployment  | 2025-12-01 |
```

## API Request Examples

### Create New Typed Conversation via Chat
```bash
curl -X POST http://localhost:8080/api/v1/conversations/chat \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=..." \
  -d '{
    "content": "I want to start my own business",
    "conv_type": "Bussiness",
    "title": "Business Planning"
  }'
```

### Response
```json
{
  "id": "message-uuid",
  "conversation": "conversation-uuid",
  "content": "Great! I can help you with starting your business...",
  "is_user": false,
  "created_at": "2025-12-01T03:00:00Z"
}
```

### Fetch Conversation with Type
```bash
curl http://localhost:8080/api/v1/conversations/<uuid> \
  -H "Cookie: access_token=..."
```

Response includes `conv_type`:
```json
{
  "id": "uuid",
  "user": 1,
  "title": "Business Planning",
  "conv_type": "Bussiness",
  "messages": [/* ... */],
  "created_at": "2025-12-01T03:00:00Z",
  "last_active_at": "2025-12-01T03:05:00Z"
}
```

## Future Enhancements

1. **Type-Specific AI Behavior**
   - Different system prompts per conversation type
   - Specialized knowledge bases
   - Custom response templates

2. **Analytics**
   - Track conversation types popularity
   - Success metrics per type
   - User journey analysis

3. **UI Improvements**
   - Show conversation type badge in UI
   - Filter conversations by type in sidebar
   - Type-specific icons and colors

## Testing Checklist

- [x] Migration created and applied
- [x] Backend accepts `conv_type` parameter
- [x] Conversation saved with correct type
- [x] Type visible in Django admin
- [x] Frontend passes type from buttons
- [x] Type persisted across messages
- [x] API returns type in responses
- [x] TypeScript types updated

## Notes

- `conv_type` is optional (blank=True) for backward compatibility
- Existing conversations without type will have empty string
- Frontend gracefully handles missing type (uses undefined)
- All 5 conversation types from UI mapped correctly
