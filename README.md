# AI Long-Form Video → Post-Ready Shorts SaaS
## MASTER TECHNICAL README (AUTHORITATIVE SINGLE SOURCE OF TRUTH)

This README defines the complete technical, architectural, and execution blueprint for a web-based SaaS that converts long-form video into post-ready short-form vertical clips. This file exists so that any AI model, developer, or future version of the author can immediately understand what to build, how to build it, and what must not be built.

This document is not marketing.  
This document is not user documentation.  
This document is a technical contract.

If something is not defined here, it does not exist.  
If a suggestion contradicts this file, it is wrong unless this file is explicitly updated.

---------------------------------------------------------------------

PRODUCT DEFINITION (LOCKED)

Objective:
Build a web-based, asynchronous video processing SaaS that accepts long-form video and outputs post-ready short-form clips.

Inputs:
- A YouTube video link
- OR a direct uploaded video file (can be multiple hours long)

Outputs:
- Multiple short-form clips
- Vertical aspect ratio (9:16)
- Burned-in subtitles
- Smart framing using face-aware cropping
- Final MP4 files ready for upload to Shorts / Reels / TikTok
- No external editor required

If the output is not immediately uploadable without further editing, the system has failed.

---------------------------------------------------------------------

EXPLICIT NON-GOALS

This system is NOT:
- A general-purpose video editor
- A CapCut or Premiere competitor
- A mobile-first application
- A real-time editor
- A livestreaming platform
- A social network
- A viral prediction engine
- A machine learning research project

Any feature that moves the product toward these directions is out of scope.

---------------------------------------------------------------------

SYSTEM ARCHITECTURE OVERVIEW

The system is composed of three strictly separated layers:

Frontend Layer (UI only)
API / Control Layer (business logic)
Media Processing Layer (AI + video rendering)

High-level flow:

Browser (Next.js)
→ FastAPI Backend
→ Redis Job Queue
→ Background Workers
→ Object Storage (S3-compatible)

Rules:
- The frontend never processes video
- The API server never processes video
- All AI and FFmpeg work happens in background workers
- Workers are stateless
- All artifacts are stored in object storage

---------------------------------------------------------------------

TECH STACK (FINAL AND LOCKED)

Frontend:
- Next.js (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- Auth: Clerk or Auth.js
- Job status via polling (no websockets initially)

Frontend responsibilities:
- Accept video input (link or upload)
- Display job status
- Display generated clips
- Allow minimal finalization controls
- Allow clip download

No client-side video processing.
No timeline editor.
No creative canvas.

Backend (API Layer):
- Python 3.11+
- FastAPI
- SQLAlchemy or SQLModel
- PostgreSQL
- JWT verification for auth
- Stripe for billing

Backend responsibilities:
- User management
- Plan and usage enforcement
- Job creation and orchestration
- Issuing signed upload/download URLs
- Persisting metadata and job state

No FFmpeg usage.
No AI inference.

Job Orchestration:
- Redis as message broker
- Celery as worker system
- Tasks are idempotent and asynchronous

Storage:
- Cloudflare R2 or equivalent S3-compatible storage
- Bucket structure:
  - raw/
  - intermediate/
  - final/
  - previews/

Media and AI Stack:
- yt-dlp for video ingestion
- Whisper or faster-whisper for speech-to-text
- PyDub for audio analysis
- MediaPipe or YOLOv8 for face detection
- FFmpeg for all video rendering
- Optional LLM for ranking and text generation only

No custom ML training in MVP.

---------------------------------------------------------------------

DATA MODEL (MINIMAL REQUIRED SCHEMA)

users table:
- id
- email
- plan
- created_at

videos table:
- id
- user_id
- source_type (YOUTUBE | UPLOAD)
- duration_seconds
- raw_storage_url
- status
- created_at

jobs table:
- id
- video_id
- type
- status
- progress
- error_message
- created_at

clips table:
- id
- video_id
- start_time
- end_time
- score
- final_storage_url
- preview_url
- created_at

---------------------------------------------------------------------

INGESTION SYSTEM

Supported at MVP:
- YouTube links
- Direct file uploads

Not supported at MVP:
- Twitch API integration
- Kick or Rumble APIs
- Live streams

YouTube ingestion flow:
1. Validate URL
2. Fetch metadata
3. Download video using yt-dlp
4. Store raw video in object storage
5. Create ingestion job

File upload flow:
1. Frontend requests signed upload URL
2. Client uploads directly to storage using multipart upload
3. Backend validates duration and format
4. Create ingestion job

Internal rule:
After ingestion, all videos are treated identically.  
The processing pipeline must not care about the original source.

---------------------------------------------------------------------

PROCESSING PIPELINE (DETAILED AND ORDERED)

Stage 1: Transcription (FOUNDATIONAL)
- Run Whisper or faster-whisper
- Output full transcript with word-level timestamps
- Store as intermediate/{video_id}/transcript.json
- Failure here aborts the entire pipeline

Stage 2: Signal Extraction
- Extract RMS loudness over time
- Detect silence segments
- Measure speech density
- Compute keyword frequency
- Store as intermediate/{video_id}/signals.json
- Pure heuristic logic

Stage 3: Clip Candidate Generation
- Minimum clip length: 15 seconds
- Maximum clip length: 60 seconds
- High speech density
- Loudness spikes
- Keyword clustering
- Generate 30–60 candidates
- Store as intermediate/{video_id}/candidates.json
- These are not final clips

Stage 4: Ranking and Filtering
- Rank candidates using heuristic scores
- Remove low-context or boring segments
- Select top N (typically 5–10)
- Optional LLM usage only for ranking and hook text
- Store as intermediate/{video_id}/selected_clips.json
- LLMs are never used for raw video understanding

Stage 5: Media Processing (AUTOMATED EDITING)
Smart Crop:
- Detect faces per frame
- Track face bounding boxes
- Compute dynamic 9:16 crop
- Prefer face centering
- Fallback to center crop if detection fails

Subtitles:
- Burned-in captions
- Word-level emphasis
- Large readable font
- Limited style presets
- No SRT export in MVP

Optional Enhancements:
- Background blur
- Optional background music
- Creator brand presets (later phase)

Stage 6: Rendering
- Compose FFmpeg command programmatically
- Render final MP4
- Generate preview video or GIF
- Store outputs in:
  - final/{clip_id}.mp4
  - previews/{clip_id}.mp4

---------------------------------------------------------------------

FINALIZATION CONTROLS (STRICTLY LIMITED)

Allowed user adjustments:
- Caption text edit
- Caption style toggle (very limited presets)
- Hook text edit
- Background music ON/OFF
- Crop nudge (left / center / right)

Disallowed:
- Timelines
- Layers
- Effects
- Transitions
- Keyframes
- Freeform editing

This is not an editor. This is final polish only.

---------------------------------------------------------------------

JOB STATE MACHINE

Job states:
CREATED → QUEUED → RUNNING → COMPLETED
                         ↓
                       FAILED

Frontend polls job status via API endpoints.
No real-time streaming updates in MVP.

---------------------------------------------------------------------

COST CONTROL AND LIMITS

- Enforce duration limits per pricing plan
- Enforce concurrent job limits per user
- Restrict GPU usage to necessary stages
- Delete raw videos after processing for lower tiers
- Unlimited processing is forbidden

Billing is usage-based (hours processed).

---------------------------------------------------------------------

DEVELOPMENT ORDER (MANDATORY)

Phase 0: Local Prototype
- Single Python script
- Hardcoded YouTube URL
- Generate exactly one vertical clip
- No web UI

Phase 1: Backend and Workers
- FastAPI backend
- Redis + Celery workers
- End-to-end automated pipeline

Phase 2: Frontend MVP
- Upload or link submission
- Job status page
- Clip list and download

Phase 3: Billing and Polish
- Stripe integration
- Usage enforcement
- Presets and UX improvements

---------------------------------------------------------------------

FAILURE CONDITIONS

This project is considered a failure if:
- Clips are not post-ready
- Users must open external editors
- Scope creep delays shipping
- Complexity exceeds solo-founder maintainability

---------------------------------------------------------------------

NORTH STAR

Long-form video → post-ready short → posted

Anything that does not move directly toward this outcome is noise.
