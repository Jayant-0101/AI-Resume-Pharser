# Usage Guide

## Quick Start Examples

### 1. Upload and Parse a Resume

**Using Python:**
```python
import requests

url = "http://localhost:8000/api/v1/resumes/upload"

with open("resume.pdf", "rb") as f:
    response = requests.post(url, files={"file": f})
    result = response.json()
    
    print(f"Resume ID: {result['resume_id']}")
    print(f"Confidence: {result['confidence_score']}%")
    print(f"Name: {result['parsed_data']['personal_info']['full_name']}")
    print(f"Email: {result['parsed_data']['personal_info']['email']}")
```

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"
```

**Using JavaScript (Fetch):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/v1/resumes/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Resume ID:', data.resume_id);
  console.log('Parsed data:', data.parsed_data);
});
```

### 2. Retrieve Parsed Resume

```python
import requests

resume_id = 1
response = requests.get(f"http://localhost:8000/api/v1/resumes/{resume_id}")
data = response.json()

print(f"Name: {data['structured_data']['full_name']}")
print(f"Experience: {data['structured_data']['experience']}")
print(f"Skills: {data['structured_data']['skills']}")
```

### 3. List All Resumes

```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/resumes/",
    params={"skip": 0, "limit": 10}
)
data = response.json()

print(f"Total resumes: {data['total']}")
for resume in data['resumes']:
    print(f"  - {resume['filename']} (ID: {resume['id']})")
```

### 4. Delete a Resume

```python
import requests

resume_id = 1
response = requests.delete(f"http://localhost:8000/api/v1/resumes/{resume_id}")

if response.status_code == 204:
    print("Resume deleted successfully")
```

## Response Format

### Successful Upload Response
```json
{
  "success": true,
  "resume_id": 1,
  "parsed_data": {
    "personal_info": {
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1-234-567-8900",
      "location": "San Francisco, CA",
      "linkedin": "linkedin.com/in/johndoe",
      "github": "github.com/johndoe"
    },
    "experience": [
      {
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "start_date": "2020-01",
        "end_date": "Present",
        "description": "..."
      }
    ],
    "education": [
      {
        "degree": "Bachelor of Science",
        "institution": "University",
        "year": "2018"
      }
    ],
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "summary": "Experienced software engineer...",
    "confidence_score": 87.5
  },
  "processing_time": 2.3
}
```

## Error Handling

### File Too Large
```json
{
  "detail": "File size exceeds 5MB limit"
}
```

### Unsupported Format
```json
{
  "success": false,
  "error": "Unsupported file type: application/x-zip"
}
```

### Resume Not Found
```json
{
  "detail": "Resume with ID 999 not found"
}
```

## Best Practices

1. **File Size**: Keep files under 5MB for optimal performance
2. **Format**: Use PDF or DOCX for best results
3. **Quality**: For scanned documents, ensure good image quality
4. **Error Handling**: Always check `success` field in response
5. **Rate Limiting**: Implement rate limiting in production
6. **Validation**: Validate parsed data before using in production

## Integration Examples

### Flask Integration
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
PARSER_API = "http://localhost:8000/api/v1"

@app.route('/parse', methods=['POST'])
def parse_resume():
    file = request.files['resume']
    files = {'file': (file.filename, file.stream, file.content_type)}
    response = requests.post(f"{PARSER_API}/resumes/upload", files=files)
    return jsonify(response.json())
```

### Django Integration
```python
from django.http import JsonResponse
import requests

def parse_resume(request):
    if request.method == 'POST':
        file = request.FILES['resume']
        files = {'file': (file.name, file.read(), file.content_type)}
        response = requests.post(
            "http://localhost:8000/api/v1/resumes/upload",
            files=files
        )
        return JsonResponse(response.json())
```

