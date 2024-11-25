from fastapi import FastAPI
from routes import auth_routes, account_routes

app = FastAPI()

# Include routes for authentication and account management
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(account_routes.router, prefix="/bank", tags=["bank"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
