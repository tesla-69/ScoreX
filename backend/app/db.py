from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from datetime import datetime

# MongoDB connection string - you should move this to environment variables
MONGO_URI = "mongodb+srv://kartikshah:rOgvMAYXxoVCoW5k@cluster0.9jzg205.mongodb.net/"
DB_NAME = "resume_parser"

# Async client for FastAPI endpoints
async_client = AsyncIOMotorClient(MONGO_URI)
db = async_client[DB_NAME]

# Sync client for model processing
sync_client = MongoClient(MONGO_URI)
sync_db = sync_client[DB_NAME]

async def save_resume(file_data: bytes, filename: str, content_type: str):
    """Save resume to MongoDB"""
    collection = db.resumes
    document = {
        "filename": filename,
        "content_type": content_type,
        "data": file_data,
        "uploaded_at": datetime.utcnow(),
        "processed": False
    }
    result = await collection.insert_one(document)
    return result.inserted_id

async def save_job_description(file_data: bytes, filename: str, content_type: str):
    """Save job description to MongoDB"""
    collection = db.job_descriptions
    document = {
        "filename": filename,
        "content_type": content_type,
        "data": file_data,
        "uploaded_at": datetime.utcnow(),
        "processed": False
    }
    result = await collection.insert_one(document)
    return result.inserted_id

def get_unprocessed_resumes():
    """Get all unprocessed resumes for model processing"""
    collection = sync_db.resumes
    return list(collection.find({"processed": False}))

def get_latest_job_description():
    """Get the latest job description for model processing"""
    collection = sync_db.job_descriptions
    return collection.find_one(sort=[("uploaded_at", -1)])

def mark_resume_processed(resume_id):
    """Mark a resume as processed"""
    collection = sync_db.resumes
    collection.update_one({"_id": resume_id}, {"$set": {"processed": True}})

def mark_job_description_processed(jd_id):
    """Mark a job description as processed"""
    collection = sync_db.job_descriptions
    collection.update_one({"_id": jd_id}, {"$set": {"processed": True}}) 