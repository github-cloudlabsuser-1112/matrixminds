from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from apis.route_page import general_pages_router


def include_router(app):
	app.include_router(general_pages_router)


def start_application():
	app = FastAPI()
	include_router(app)
    
	return app 

app = start_application()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == '__main__':
    uvicorn.run('main:app', port=9002, host='127.0.0.1')