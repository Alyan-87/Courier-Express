# Courier Express

A full-stack courier and parcel delivery management system with role-based workflows for customers, staff, and riders.

For a concise portfolio/recruiter version, see [README.profile.md](README.profile.md).

The project provides a complete logistics flow from parcel booking to delivery status updates, with secure authentication and a modern frontend dashboard.

## Table of Contents
- Overview
- Key Features
- Workflow
- Tech Stack
- Project Structure
- Getting Started
- Environment Configuration
- Running the Project
- API Overview
- Roadmap

## Overview
Courier Express is built for courier operations where different users need dedicated responsibilities:
- Customers create and track parcels.
- Staff manages parcels and assigns riders.
- Riders view assigned parcels and update delivery status.

The backend is powered by FastAPI and MongoDB, while the frontend is built with React + Vite.

## Key Features
- Role-based authentication using JWT (Customer, Staff, Rider)
- Customer parcel booking and parcel tracking
- Staff parcel management and rider assignment
- Rider parcel board and status updates
- Status history logging for delivery lifecycle
- MongoDB health-check endpoint for runtime verification
- Responsive frontend dashboards by role

## Workflow
### 1. User Authentication
- User registers with a role.
- User logs in and receives a bearer token.
- Protected endpoints validate token and role before access.

### 2. Customer Flow
- Customer creates parcel with receiver details and weight.
- System auto-generates tracking number.
- Charges are calculated based on weight.
- Customer can view their parcels and track by tracking number.

### 3. Staff Flow
- Staff can view all parcels.
- Staff creates parcels on behalf of customers when needed.
- Staff assigns parcels to available riders.
- Staff can update parcel details.

### 4. Rider Flow
- Rider sees parcels assigned to them.
- Rider updates parcel status through delivery stages.
- Status changes are saved in status history.

## Tech Stack
### Frontend
- React 19
- Vite 7
- React Router
- Axios
- Tailwind CSS

### Backend
- FastAPI
- PyMongo
- python-jose (JWT)
- passlib (password hashing)
- python-dotenv

### Database
- MongoDB (local instance)

## Project Structure
```text
Courier-Express/
  backend/
    config/
    models/
    routers/
    schemas/
    utils/
    main.py
    requirements.txt
  frontend/
    src/
      pages/
      services/
      assets/
    package.json
```

## Getting Started
### Prerequisites
- Node.js 18+
- Python 3.10+
- MongoDB running locally on default port (27017)

## Environment Configuration
Create/update backend environment file at `backend/.env`:

```env
MONGO_URL=mongodb://localhost:27017/
MONGO_DB_NAME=courier_express
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Frontend API base URL is configured in `frontend/src/services/api.js` and should point to:

```js
http://127.0.0.1:8000
```

## Running the Project
### 1. Backend
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

Backend will run at:
- http://127.0.0.1:8000

### 2. Frontend
```powershell
cd frontend
npm install
npm run dev
```

Frontend will run at:
- http://127.0.0.1:5173

## API Overview
### Health
- `GET /health` - Service health
- `GET /health/db` - MongoDB connectivity health

### Auth
- `POST /auth/register`
- `POST /auth/login`

### Customer
- `POST /customer/parcel/create`
- `GET /customer/my-parcels`
- `GET /customer/parcel/track/{tracking_number}`

### Staff
- `GET /staff/parcels`
- `GET /staff/parcel/{parcel_id}`
- `GET /staff/riders`
- `POST /staff/parcel/create`
- `PUT /staff/parcel/{parcel_id}`
- `POST /staff/assign-rider`

### Rider
- `GET /rider/my-parcels`
- `PUT /rider/update-status/{parcel_id}`

## Roadmap
- Add advanced filtering and search for parcels
- Add notification system for status updates
- Add analytics dashboard for staff
- Add Docker setup for one-command deployment
- Add automated tests and CI pipeline

---

If you find this project useful, feel free to star the repository and contribute improvements.
