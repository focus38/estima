import warnings


warnings.filterwarnings('ignore', category=UserWarning)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, log_config=None)