# API Reference Guide

## Base URL
```
http://localhost:3000/api
```

## Endpoints

### 1. Generate Custom Filters
**Endpoint:** `POST /api/generate-filters`

**Request:**
```json
{
  "naivePrompt": "string (required)",
  "extractedText": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "filters": {
    "custom_filters": [
      {
        "type": "text_input" | "radio" | "checkbox" | "selectbox",
        "label": "string",
        "key": "string",
        "options": ["string"] // optional
      }
    ]
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:3000/api/generate-filters \
  -H "Content-Type: application/json" \
  -d '{
    "naivePrompt": "Create a recipe for chocolate cake"
  }'
```

---

### 2. Refine Prompt
**Endpoint:** `POST /api/refine-prompt`

**Request:**
```json
{
  "naivePrompt": "string (required)",
  "defaultFilters": {
    "answerFormat": "Paragraph" | "Bullet Points",
    "toneOfResponse": "Formal" | "Informal" | "Neutral",
    "outputDetail": 1-5,
    "audienceLevel": "General" | "Beginner" | "Intermediate" | "Expert",
    "purpose": "Learning/Education" | "Professional/Work" | "Personal Interest" | "Research",
    "includeVisuals": boolean,
    "responseStructure": "Concise" | "Structured with Headings" | "Step-by-Step"
  },
  "customFilters": {
    "key": "value"
  },
  "extractedText": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "refinedPrompt": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:3000/api/refine-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "naivePrompt": "Write about AI",
    "defaultFilters": {
      "answerFormat": "Paragraph",
      "toneOfResponse": "Formal",
      "outputDetail": 5,
      "audienceLevel": "Expert",
      "purpose": "Research",
      "includeVisuals": true,
      "responseStructure": "Structured with Headings"
    }
  }'
```

---

### 3. Chat
**Endpoint:** `POST /api/chat`

**Request:**
```json
{
  "message": "string (required)",
  "conversationHistory": [
    {
      "role": "user" | "assistant",
      "content": "string"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "response": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "conversationHistory": []
  }'
```

---

### 4. Upload Files
**Endpoint:** `POST /api/upload`

**Request:** FormData
```
files: File[] (required)
```

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "filename": "string",
      "type": "string",
      "text": "string",
      "success": boolean,
      "error": "string (optional)"
    }
  ],
  "combinedText": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "files=@document.pdf" \
  -F "files=@image.png"
```

---

## Error Responses

### Validation Error (400)
```json
{
  "success": false,
  "error": "Validation failed",
  "details": [
    {
      "code": "string",
      "message": "string",
      "path": ["string"]
    }
  ]
}
```

### Server Error (500)
```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Supported File Types

| Extension | MIME Type | Processor |
|-----------|-----------|-----------|
| .pdf | application/pdf | pdf-parse |
| .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document | mammoth |
| .png, .jpg, .jpeg | image/* | Tesseract OCR |
| .txt | text/plain | UTF-8 decoder |

---

## Rate Limits

- OpenAI API: Subject to your API key limits
- Gemini API: Subject to your API key limits
- File Upload: No artificial limits (system memory dependent)

---

## Best Practices

1. **Always validate inputs** before sending requests
2. **Handle errors gracefully** on the client side
3. **Use conversation history** for context in chat
4. **Combine extracted text** with prompts for better results
5. **Check file types** before uploading
6. **Monitor API usage** to avoid rate limits

---

## Testing

### Test Generate Filters
```javascript
const response = await fetch('/api/generate-filters', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    naivePrompt: 'Create a workout plan'
  })
});
const data = await response.json();
```

### Test File Upload
```javascript
const formData = new FormData();
formData.append('files', file1);
formData.append('files', file2);

const response = await fetch('/api/upload', {
  method: 'POST',
  body: formData
});
const data = await response.json();
```

---

## Environment Variables Required

```env
OPENAI_API_KEY=your_openai_key
GOOGLE_GEMINI_API_KEY=your_gemini_key
```

---

## Status Codes

- `200` - Success
- `400` - Bad Request (validation error)
- `500` - Internal Server Error

---

For more details, see the full documentation in `FILE_PROCESSING_AND_API_COMPLETE.md`
