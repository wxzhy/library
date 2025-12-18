from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import lifespan
from .routers import auth, users, books, borrows

app = FastAPI(
    title="图书管理系统API",
    description="图书馆管理系统的后端API接口",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="", tags=["认证"])
app.include_router(users.router, prefix="", tags=["用户管理"])
app.include_router(books.router, prefix="", tags=["图书管理"])
app.include_router(borrows.router, prefix="", tags=["借阅管理"])


@app.get("/")
async def root():
    return {
        "message": "图书管理系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "library-management-system"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
