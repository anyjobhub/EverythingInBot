# Middleware Compatibility Guide

## ✅ Aiogram 3.x Immutable Objects

**CRITICAL**: Aiogram 3.x Message and CallbackQuery objects are **FROZEN** (immutable).

### ❌ NEVER DO THIS:
```python
event.text = "modified"  # ValidationError: Instance is frozen
event.caption = "modified"  # ValidationError: Instance is frozen
event.data = "modified"  # ValidationError: Instance is frozen
```

### ✅ ALWAYS DO THIS:
```python
# Store sanitized/modified data in the data dict
data["sanitized_text"] = sanitize(event.text)
data["sanitized_caption"] = sanitize(event.caption)
data["sanitized_callback_data"] = sanitize(event.data)
```

## Handler Usage

### In Handlers - Access Sanitized Data

```python
@router.message()
async def handler(message: Message, **data):
    # Get sanitized text (fallback to original if not sanitized)
    text = data.get("sanitized_text") or message.text
    
    # Or use original if you need it
    original = data.get("original_text") or message.text
```

### Available Data Keys

After middleware processing, `data` dict contains:

- `data["sanitized_text"]` - Sanitized message text
- `data["original_text"]` - Original message text
- `data["sanitized_caption"]` - Sanitized caption
- `data["original_caption"]` - Original caption
- `data["sanitized_callback_data"]` - Sanitized callback data
- `data["original_callback_data"]` - Original callback data
- `data["user_id"]` - User ID (from IP tracking)
- `data["username"]` - Username (from IP tracking)
- `data["chat_id"]` - Chat ID (from IP tracking)

## Middleware Chain

1. **IPTrackingMiddleware** - Tracks user info (no mutations)
2. **InputValidationMiddleware** - Sanitizes input (stores in data dict)
3. **SpamProtectionMiddleware** - Detects spam (no mutations)
4. **RateLimitMiddleware** - Limits requests (no mutations)

All middlewares are safe and never mutate frozen objects.
