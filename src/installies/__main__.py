from installies.app import app
from installies.config import debug_mode, host, port

if __name__ == "__main__":
    app.run(host=host, port=port, debug=debug_mode)
