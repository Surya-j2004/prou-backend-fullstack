SkillNexus - API & Matching Engine (Backend)

 Overview

This is the backend API for SkillNexus, the Internal Talent Marketplace for "any company(for ex)". It provides the core logic for managing projects, employees, and executing the Weighted Skill Matching Algorithm.

It is built with FastAPI for high performance and uses SQLAlchemy for database ORM.

https://prou-backend-fullstack.onrender.com 
(Render)
Swagger Documentation

 Tech Stack

Language: Python 3.10+

Framework: FastAPI

Server: Uvicorn

Database: SQLite (Production-ready simulation for Render Free Tier)

ORM: SQLAlchemy

Validation: Pydantic

Deployment: Render

 The Matching Algorithm

The core of this project is the calculate_match_score function. It calculates a compatibility percentage (0-100%) based on:

Weighted Requirements: Harder skills contribute more to the final score.

Skill Capping: Over-qualification does not artificially inflate the score (a Senior Dev doing a Junior task is a 100% match, not 150%).

Gap Analysis: Penalizes missing critical skills.

 API Endpoints

Method

Endpoint

Description

GET

/projects/

Fetch all active projects.

POST

/projects/

Create a new project requirement.

GET

/projects/{id}/matches

Run the matching algorithm for a specific project.

 Setup Instructions

Clone the repository:

git clone [https://github.com/Surya-j2004/prou-backend-fullstack.git](https://github.com/Surya-j2004/prou-backend-fullstack.git)
cd prou-backend-fullstack


Create Virtual Environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Requirements:

pip install -r requirements.txt


Run Locally:

uvicorn main:app --reload


The API will be available at http://127.0.0.1:8000.

 Deployment Note (Render Free Tier)

This project is deployed on Render's Free Tier.

Cold Start: The server may sleep after inactivity. The first request might take ~60 seconds to wake it up.

Persistence: It uses a file-based SQLite database. On the free tier, the database resets to the initial seed data (Sarah Chen & Marcus Johnson) whenever the server restarts or deploys. For a permanent production environment, I would configure a managed PostgreSQL instance.
