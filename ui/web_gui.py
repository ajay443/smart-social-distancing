import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse
import uvicorn
import os


class WebGUI:
    """
    The Webgui object implements a fastapi application and acts as an interface for users.
    Once it is created it will act as a central application for viewing outputs.

    :param config: Is a ConfigEngine instance which provides necessary parameters.
    :param engine_instance:  A ConfigEngine object which store all of the config parameters. Access to any parameter
        is possible by calling get_section_dict method.
    """

    def __init__(self, config):
        self.config = config
        self._host = self.config.get_section_dict("App")["Host"]
        self._port = int(self.config.get_section_dict("App")["Port"])
        self.app = self.create_fastapi_app()

    def create_fastapi_app(self):
        # Create and return a fastapi instance
        app = FastAPI()

        if os.environ.get('DEV_ALLOW_ALL_ORIGINS', False):
            # This option allows React development server (which is served on another port, like 3000) to proxy requests
            # to this server.
            # WARNING: read this before enabling it in your environment:
            # https://medium.com/@stestagg/stealing-secrets-from-developers-using-websockets-254f98d577a0
            from fastapi.middleware.cors import CORSMiddleware
            app.add_middleware(CORSMiddleware, allow_origins='*', allow_credentials=True, allow_methods=['*'],
                               allow_headers=['*'])

        app.mount("/panel/static", StaticFiles(directory="/srv/frontend/static"), name="panel")
        app.mount("/static", StaticFiles(directory="/repo/data/web_gui/static"), name="static")

        @app.get("/panel/")
        async def panel():
            return FileResponse("/srv/frontend/index.html")

        @app.get("/favicon.ico")
        async def panel():
            return FileResponse("/srv/frontend/favicon.ico")

        @app.get("/")
        async def index():
            return RedirectResponse("/panel/")

        @app.get("/api/cameras/")
        async def api_cameras():
            return [{
                'id': 'default',
                'streams': [
                    {'src': '/static/gstreamer/default/playlist.m3u8', 'type': 'application/x-mpegURL',
                     'birdseye': False},
                    {'src': '/static/gstreamer/default-birdseye/playlist.m3u8', 'type': 'application/x-mpegURL',
                     'birdseye': True},
                ],
            }]

        return app

    def start(self):
        uvicorn.run(self.app, host=self._host, port=self._port, log_level='info', access_log=False)
