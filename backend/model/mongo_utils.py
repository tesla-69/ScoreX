from pymongo import MongoClient
from gridfs import GridFS
import io
import os
import tempfile
<<<<<<< HEAD
from datetime import datetime
from bson.objectid import ObjectId # Import ObjectId


# MongoDB connection string - using the same as in app/db.py for consistency
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://kartikshah:rOgvMAYXxoVCoW5k@cluster0.9jzg205.mongodb.net/")
DB_NAME = "resume_parser"

def get_mongo_client():
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    return client

def get_db():
    client = get_mongo_client()
    return client[DB_NAME]

def get_gridfs():
    # GridFS is typically associated with a specific database
    return GridFS(get_db())
=======

def get_mongo_client():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    return client

def get_gridfs():
    client = get_mongo_client()
    db = client['resume_db']  # Use your database name
    return GridFS(db)
>>>>>>> 597ccf41dd54ec10daf12d0a71636f27cedcd518

def get_resumes_from_mongodb():
    """
    Retrieves all resumes from MongoDB GridFS and saves them temporarily
    Returns a list of dictionaries containing resume data and temporary file paths
    """
<<<<<<< HEAD
    db = get_db()
    resumes_collection = db.resumes
    resumes_data = []
=======
    gfs = get_gridfs()
    resumes = []
>>>>>>> 597ccf41dd54ec10daf12d0a71636f27cedcd518
    
    # Create a temporary directory to store the files
    temp_dir = tempfile.mkdtemp()
    
<<<<<<< HEAD
    # Find all resume documents in the resumes collection
    for resume_doc in resumes_collection.find({"processed": False}):
        # Assuming 'data' field stores the binary content and 'filename' stores the name
        temp_file_path = os.path.join(temp_dir, resume_doc["filename"])
        
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(resume_doc["data"])
        
        resumes_data.append({
            '_id': resume_doc['_id'],
            'file_path': temp_file_path,
            'filename': resume_doc["filename"],
            'content_type': resume_doc["content_type"]
        })
    
    return resumes_data

def get_unprocessed_resumes():
    """Get all unprocessed resumes from the resumes collection"""
    db = get_db()
    return list(db.resumes.find({"processed": False}))

def get_latest_job_description():
    """Get the latest job description from the job_descriptions collection"""
    db = get_db()
    return db.job_descriptions.find_one(sort=[("uploaded_at", -1)])

def mark_resume_processed(resume_id):
    """Mark a resume as processed by its ID"""
    db = get_db()
    db.resumes.update_one({"_id": ObjectId(resume_id) if isinstance(resume_id, str) else resume_id}, {"$set": {"processed": True}})

def mark_job_description_processed(jd_id):
    """Mark a job description as processed by its ID"""
    db = get_db()
    db.job_descriptions.update_one({"_id": ObjectId(jd_id) if isinstance(jd_id, str) else jd_id}, {"$set": {"processed": True}})
=======
    # Find all resume files in GridFS
    for grid_out in gfs.find({"metadata.type": "resume"}):
        # Create a temporary file
        temp_file_path = os.path.join(temp_dir, grid_out.filename)
        
        # Download the file from GridFS
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(grid_out.read())
        
        resumes.append({
            'file_path': temp_file_path,
            'filename': grid_out.filename,
            'metadata': grid_out.metadata
        })
    
    return resumes
>>>>>>> 597ccf41dd54ec10daf12d0a71636f27cedcd518

def cleanup_temp_files(resumes):
    """
    Cleans up temporary files after processing
    """
    for resume in resumes:
        try:
<<<<<<< HEAD
            if 'file_path' in resume and os.path.exists(resume['file_path']):
                os.remove(resume['file_path'])
        except Exception as e:
            print(f"Error cleaning up file {resume.get('file_path', 'N/A')}: {e}") 
=======
            os.remove(resume['file_path'])
        except:
            pass 
>>>>>>> 597ccf41dd54ec10daf12d0a71636f27cedcd518
