from fastapi import FastAPI, UploadFile

app = FastAPI(title="Capture Service")


@app.post("/upload/{session_id}")
async def upload_chunk(session_id: str, file: UploadFile):
    return {"session_id": session_id, "filename": file.filename, "status": "received"}
