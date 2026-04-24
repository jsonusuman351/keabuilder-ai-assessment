# Q2: Multi-Provider Content Routing Architecture

## System Flow
User (KeaBuilder UI)
|
| POST /api/generate { type, prompt, style }
v
API Gateway (FastAPI)
|
v
Content Router
|--- type="image" ---> Image Provider (DALL-E / SDXL)
|--- type="video" ---> Video Provider (Runway / Pika)
|--- type="voice" ---> Voice Provider (ElevenLabs / TTS)
|
v
Cloud Storage (S3 / CloudFlare R2)
|
v
Asset Library (User's KeaBuilder Dashboard)


## Frontend ↔ Backend Interaction

1. User selects content type in builder UI
2. Frontend sends POST with type + prompt
3. Backend returns job_id immediately
4. Frontend polls /api/status/{job_id} or listens via WebSocket
5. Once complete, asset URL returned
6. Asset appears in user's asset library
7. User drags into funnel/website

## Output Management

- All assets stored in cloud with metadata
- Each asset: { asset_id, type, provider, user_id, prompt, url, created_at }
- Version history maintained
- User can regenerate without losing previous versions
