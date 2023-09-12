#!/usr/local/bin/python
from app.db.init_db import reset_app_db
from app.db.session import engine

reset_app_db(engine)
