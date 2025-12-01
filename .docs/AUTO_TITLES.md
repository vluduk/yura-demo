# Auto-Generated Conversation Titles

## Feature Overview

After a user sends their **3rd message** in a conversation, the system automatically generates a short, descriptive title based on the conversation content.

## How It Works

### Trigger Condition
- **When**: After the 3rd user message
- **Only if**: Current title is empty OR ends with "- Чат" (auto-generated generic title)

### Title Generation Process

1. **Extract Context**: Gets first 6 messages (3 user + 3 AI responses)
2. **LLM Summarization**: Uses Google Gemini to create 4-5 word summary
3. **Update**: Replaces generic title with descriptive summary

### Example Transformations

| Before (Generic) | After 3 Messages | New Title |
|-----------------|------------------|-----------|
| "Наймана праця - Чат" | User asks about Python developer jobs | "Пошук роботи Python developer" |
| "Власний бізнес - Чат" | User discusses restaurant idea | "Валідація ідеї ресторану" |
| "Навчання - Чат" | User asks about web development courses | "Навчання веб-розробці" |
| "Самозайнятість - Чат" | User discusses freelance design | "Фріланс графічний дизайн" |

## Implementation

### Backend - Conversation View
```python
# /backend/src/api/views/conversation.py

# After saving AI message
user_message_count = conv.messages.filter(is_user=True).count()
if user_message_count == 3 and (not conv.title or conv.title.endswith('- Чат')):
    AdvisorService.generate_conversation_title(conv)
```

### Backend - AdvisorService
```python
# /backend/src/api/services/advisor.py

@staticmethod
def generate_conversation_title(conversation):
    """Generate short title based on first 3 exchanges"""
    # Gets first 6 messages
    # Creates summary prompt for LLM
    # Updates conversation.title
```

## LLM Prompt Template

```
На основі цієї розмови створіть ДУЖЕ КОРОТКУ назву (максимум 4-5 слів).
Назва має відображати ОСНОВНУ ТЕМУ розмови.

Тип розмови: {conv_type_label}

Розмова:
{conversation_text}

ВИМОГИ:
- Максимум 4-5 слів
- Українською мовою
- БЕЗ лапок, БЕЗ префіксів типу "Назва:", просто текст
- Описує СУТЬ розмови

Назва:
```

## Title Characteristics

### Length
- **Target**: 4-5 words
- **Maximum**: 60 characters (truncated if longer)

### Language
- **Ukrainian only**

### Format
- No quotes or prefixes
- Clean, descriptive text
- Captures conversation essence

## Error Handling

### Silent Failures
- If LLM is unavailable → keeps generic title
- If generation fails → no error shown to user
- Conversation continues normally regardless

### Fallback Behavior
- Generic title remains if:
  - No GOOGLE_API_KEY configured
  - LLM generation fails
  - Response is empty

## User Experience

### Timeline
```
Message 1 (User):   "Привіт, шукаю роботу"
Message 1 (AI):     "Вітаю! Яку позицію..."
Title:              "Наймана праця - Чат" ← Generic

Message 2 (User):   "Хочу бути Python developer"  
Message 2 (AI):     "Чудовий вибір..."
Title:              "Наймана праця - Чат" ← Still generic

Message 3 (User):   "Маю 2 роки досвіду Django"
Message 3 (AI):     "Відмінно! З вашим..."
Title:              "Пошук роботи Python developer" ← Auto-generated! ✨
```

### Frontend Display
- Title updates automatically in sidebar
- No reload required (if using live updates)
- Users see descriptive, meaningful names

## Benefits

### For Users
- ✅ **Easy conversation identification** in sidebar
- ✅ **No manual title entry** required
- ✅ **Meaningful context** at a glance
- ✅ **Better organization** of multiple chats

### For System
- ✅ **Automated** - no user action needed
- ✅ **Context-aware** - based on actual conversation
- ✅ **Efficient** - only runs once per conversation
- ✅ **Graceful degradation** - fails silently

## Configuration

### Environment Variables
- `GOOGLE_API_KEY` - Required for title generation
- `GOOGLE_LLM_MODEL` - Model used (default: `gemini-2.0-flash-exp`)

### Customization
To modify title generation behavior, edit:
```python
# /backend/src/api/services/advisor.py
# Method: generate_conversation_title()

# Adjust:
- Number of messages used (currently 6)
- Prompt template
- Length limits
- Language
```

## Testing

### Manual Test
1. Create new conversation (any type)
2. Send 3 user messages
3. Check conversation title updates after 3rd message
4. Verify title is descriptive and short

### Expected Outcomes
- Title changes from generic to specific
- Title is in Ukrainian
- Title is 4-5 words (max 60 chars)
- Title describes conversation topic

### Test Cases

**HIRING Conversation:**
```
Messages:
1. "Шукаю роботу junior developer"
2. "Знаю JavaScript та React"  
3. "Потрібна допомога з резюме"

Expected Title: "Резюме Junior JavaScript developer"
```

**BUSINESS Conversation:**
```
Messages:
1. "Хочу відкрити онлайн-магазин"
2. "Продавати handmade вироби"
3. "Скільки потрібно для старту?"

Expected Title: "Онлайн-магазин handmade виробів"
```

## Future Enhancements

### Potential Improvements
1. **Regenerate Title** - Allow users to regenerate if unsatisfied
2. **Custom Titles** - Let users edit auto-generated titles
3. **Multi-language** - Support English/other languages  
4. **Better Timing** - Option to delay until more messages
5. **Title History** - Track title evolution

### Advanced Features
- **Conversation Tags** - Extract topics/keywords
- **Smart Grouping** - Group similar conversations
- **Search Enhancement** - Use titles for better search

## Troubleshooting

### Title Doesn't Update
**Check:**
- Is GOOGLE_API_KEY set?
- Did user send exactly 3 messages?
- Was original title generic (ends with "- Чат")?
- Check Django logs for errors

### Title Is Too Long
**Cause**: LLM generated >60 chars
**Fix**: Auto-truncated to 57 chars + "..."

### Title Not Descriptive
**Cause**: Conversation too generic/vague
**Solution**: LLM does its best with available context

### Title In Wrong Language
**Cause**: LLM ignored language instruction
**Fix**: Prompt emphasizes Ukrainian strongly

## Summary

Auto-generated titles provide a seamless UX improvement:
- No user effort required
- Meaningful conversation names
- Automatic after 3 messages
- Fails gracefully if LLM unavailable

This feature enhances conversation organization without adding complexity to the user flow.
