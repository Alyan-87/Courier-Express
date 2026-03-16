# Courier Express

Role-based courier and parcel management platform built with React, FastAPI, and MongoDB.

## Project Snapshot
Courier Express digitizes parcel operations across three operational roles:
- Customer: Book and track parcels
- Staff: Manage parcels and assign riders
- Rider: View assigned deliveries and update status

The system is designed to reflect real-world delivery workflows from booking to final delivery updates.

## Highlights
- JWT-based role authentication (Customer, Staff, Rider)
- End-to-end parcel lifecycle management
- Tracking number generation and status history logging
- Rider assignment and delivery progress updates
- MongoDB-backed API with health monitoring
- Responsive frontend dashboard experience

## Tech Stack
- Frontend: React, Vite, Axios, React Router, Tailwind CSS
- Backend: FastAPI, PyMongo, python-jose, passlib, python-dotenv
- Database: MongoDB (local)

## Architecture
- Frontend consumes REST APIs from FastAPI backend
- Backend enforces role-based authorization via bearer tokens
- MongoDB stores users, parcels, assignments, and status history

## Core Workflow
1. User registers and logs in by role.
2. Customer creates parcel request.
3. Staff reviews parcels and assigns rider.
4. Rider updates delivery status through route milestones.
5. Customer tracks parcel progression.

## Quick Run
### Backend
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

## Key Endpoints
- `GET /health`
- `GET /health/db`
- `POST /auth/register`
- `POST /auth/login`
- `POST /customer/parcel/create`
- `POST /staff/assign-rider`
- `PUT /rider/update-status/{parcel_id}`

## Value Delivered
This project demonstrates:
- Full-stack architecture design
- Role-driven product workflow modeling
- API-first backend engineering
- Practical state and auth handling in modern React apps

---
Built as a production-style portfolio project for courier operations and logistics workflow automation.
