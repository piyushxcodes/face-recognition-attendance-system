# Face Recognition Attendance System

A complete AI-powered smart attendance management system built using **Django**, **OpenCV**, and **LBPH (Local Binary Patterns Histogram)** face recognition technology. This project automates student attendance by detecting and recognizing faces in real time through a webcam, reducing manual attendance efforts while improving speed, efficiency, and accuracy.

---

# Project Overview

Traditional attendance systems are time-consuming, prone to proxy attendance, and inefficient for large classrooms or organizations. This project solves that problem by using computer vision and machine learning to automatically identify registered individuals and mark their attendance instantly.

The system captures face samples, trains a recognition model, and then performs real-time face detection and recognition to maintain attendance records digitally.

---

# Key Objectives

- Automate attendance using facial recognition
- Eliminate proxy attendance
- Reduce manual work for teachers/admins
- Maintain digital attendance records
- Improve classroom/office efficiency
- Build a practical AI + Web development minor project

---

# Core Features

## Student Registration
- Register new students/users into the system
- Assign unique ID and name
- Capture multiple face samples through webcam
- Store images for training

## Dataset Collection
- Collects facial images from live webcam feed
- Saves multiple face angles for better accuracy
- Organizes data for model training

## Model Training (LBPH)
- Uses LBPH Face Recognizer from OpenCV
- Trains on collected datasets
- Generates trained model for recognition
- Lightweight and effective for academic projects

## Real-Time Attendance System
- Detects face using Haar Cascade Classifier
- Recognizes registered users in live camera feed
- Marks attendance automatically
- Prevents duplicate attendance entries

## Attendance Record Management
- Saves attendance with:
  - Name
  - ID
  - Date
  - Time
- CSV export support
- Database management with SQLite

## Django Admin Panel
- Manage students
- View attendance records
- Database control
- Project scalability

---

# Technologies Used

## Backend
- Python
- Django Framework

## Computer Vision / AI
- OpenCV
- LBPH Face Recognizer
- Haar Cascade Classifier

## Database
- SQLite3

## Frontend
- HTML
- CSS
- Bootstrap

## Tools
- Git & GitHub
- VS Code

---

# System Workflow

## Step 1: Face Registration
User enters details → Webcam captures face images → Images stored in dataset folder

## Step 2: Model Training
Dataset images processed → LBPH algorithm trains model → Trained model saved

## Step 3: Real-Time Recognition
Webcam detects face → Model predicts identity → Attendance marked

## Step 4: Attendance Storage
Attendance saved in CSV / Database → Accessible through admin panel

---

# Folder Structure

```bash
face_attendance/
│── manage.py
│── requirements.txt
│── db.sqlite3
│
├── face_attendance/        # Main Django project settings
├── recognition/            # Face recognition app
├── Attendance/             # Attendance records
├── media/                  # Dataset and training files (excluded from GitHub)
└── templates/              # Frontend HTML templates
