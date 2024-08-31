bind = "0.0.0.0:1337"
workers = 1
threads = 4
timeout = 120
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"