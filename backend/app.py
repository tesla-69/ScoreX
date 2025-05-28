from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
import pandas as pd
import os
from typing import List, Dict, Any
from pydantic import BaseModel

app = FastAPI(title="Resume Parser API")

# Configure CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchResult(BaseModel):
    Area: str
    Match: float
    Matching_Keywords: str
    Missing_Keywords: str

class MatchResponse(BaseModel):
    results: List[Dict[str, Any]]
    graphUrl: str
    wordcloudUrl: str

# Get the absolute path to the project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.get("/")
async def root():
    return {"status": "success", "message": "Resume Parser API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "success", "message": "API is healthy"}

@app.get("/api/results/{match_number}")
async def get_match_results(match_number: int):
    if not 1 <= match_number <= 3:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "Invalid match number"}
        )
    
    match_folder = os.path.join(ROOT_DIR, f"match{match_number}")
    results_file = os.path.join(match_folder, 'results.csv')
    
    try:
        print(f"Reading results from: {results_file}")
        if not os.path.exists(results_file):
            return JSONResponse(
                status_code=404,
                content={"status": "error", "detail": f"Results file not found at {results_file}"}
            )
            
        results_df = pd.read_csv(results_file)
        results = results_df.to_dict('records')
        
        response_data = {
            "status": "success",
            "results": results,
            "graphUrl": f"/api/graph/{match_number}",
            "wordcloudUrl": f"/api/wordcloud/{match_number}"
        }
        print(f"Sending response: {response_data}")
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except Exception as e:
        print(f"Error in get_match_results: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

@app.get("/api/graph/{match_number}")
async def get_graph(match_number: int):
    if not 1 <= match_number <= 3:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "Invalid match number"}
        )
    
    file_path = os.path.join(ROOT_DIR, f"match{match_number}", "graph.png")
    print(f"Serving graph from: {file_path}")
    
    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"status": "error", "detail": f"Graph not found at {file_path}"}
        )
    
    return FileResponse(file_path, media_type="image/png")

@app.get("/api/wordcloud/{match_number}")
async def get_wordcloud(match_number: int):
    if not 1 <= match_number <= 3:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "Invalid match number"}
        )
    
    file_path = os.path.join(ROOT_DIR, f"match{match_number}", "wordcloud.png")
    print(f"Serving wordcloud from: {file_path}")
    
    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"status": "error", "detail": f"Wordcloud not found at {file_path}"}
        )
    
    return FileResponse(file_path, media_type="image/png")

@app.get("/api/top-matches")
async def get_top_matches():
    try:
        output_file = os.path.join(ROOT_DIR, 'output.csv')
        print(f"Reading top matches from: {output_file}")
        
        if not os.path.exists(output_file):
            return JSONResponse(
                status_code=404,
                content={"status": "error", "detail": f"Output file not found at {output_file}"}
            )
            
        df = pd.read_csv(output_file)
        candidates = df['Candidate'].unique()
        
        response_data = {
            "status": "success",
            "candidates": candidates.tolist()
        }
        print(f"Sending response: {response_data}")
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except Exception as e:
        print(f"Error in get_top_matches: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    print(f"Project root directory: {ROOT_DIR}")
    print(f"Checking files:")
    print(f"output.csv exists: {os.path.exists(os.path.join(ROOT_DIR, 'output.csv'))}")
    for i in range(1, 4):
        match_dir = os.path.join(ROOT_DIR, f"match{i}")
        print(f"match{i} exists: {os.path.exists(match_dir)}")
        if os.path.exists(match_dir):
            print(f"  results.csv exists: {os.path.exists(os.path.join(match_dir, 'results.csv'))}")
            print(f"  graph.png exists: {os.path.exists(os.path.join(match_dir, 'graph.png'))}")
            print(f"  wordcloud.png exists: {os.path.exists(os.path.join(match_dir, 'wordcloud.png'))}")
    
    uvicorn.run(app, host="127.0.0.1", port=8000) 