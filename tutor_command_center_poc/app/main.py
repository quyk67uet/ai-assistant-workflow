from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime

from agent import run_agent_flow

app = FastAPI(title="Tutor Command Center API", version="1.0.0")

# Add CORS middleware to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TutorCommandRequest(BaseModel):
    prompt: str


class LogEntry(BaseModel):
    timestamp: str
    step: str
    status: str
    message: str
    details: Dict[str, Any] = {}


class TutorCommandResponse(BaseModel):
    response: str
    logs: List[LogEntry] = []
    processing_time: float = 0.0
    turns_processed: int = 0
    status: str = "success"


@app.post("/tutor-command", response_model=TutorCommandResponse)
async def handle_tutor_command(request: TutorCommandRequest) -> TutorCommandResponse:
    """
    Handle tutor command requests and process them through the AI agent.
    
    Args:
        request: Request containing the tutor's natural language command
        
    Returns:
        Response containing the AI agent's processed result and detailed logs
    """
    try:
        # Process the command through the AI agent
        result = run_agent_flow(request.prompt)
        
        return TutorCommandResponse(
            response=result["response"],
            logs=result["logs"],
            processing_time=result["processing_time"],
            turns_processed=result["turns_processed"],
            status=result["status"]
        )
        
    except Exception as e:
        error_log = LogEntry(
            timestamp=str(datetime.now().isoformat()),
            step="error_handling",
            status="error",
            message=f"Lỗi API: {str(e)}",
            details={}
        )
        
        return TutorCommandResponse(
            response=f"Đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}",
            logs=[error_log],
            processing_time=0.0,
            turns_processed=0,
            status="error"
        )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Tutor Command Center API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "tutor-command-center"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)