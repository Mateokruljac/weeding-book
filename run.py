import os

from factory import create_app

app = create_app()

if __name__ == "__main__":
    in_docker = os.getenv("DOCKER_ENV") == "1"
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=not in_docker,
        reloader_type="stat",
    )
