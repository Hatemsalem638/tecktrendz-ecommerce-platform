from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from tryon_model import generate_tryon_image  
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/tryon")
async def tryon(userImage: UploadFile = File(...), productId: str = Form(...)):
    with open(f"temp/{userImage.filename}", "wb") as buffer:
        shutil.copyfileobj(userImage.file, buffer)
    
    output_path = generate_tryon_image(user_img_path=f"temp/{userImage.filename}", product_id=productId)

    return {"success": True, "output_path": output_path}
