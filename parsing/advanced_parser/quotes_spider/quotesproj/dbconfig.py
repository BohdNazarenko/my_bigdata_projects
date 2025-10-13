from environs import Env
from pathlib import Path

def _env():
    env = Env()
    env.read_env(Path(__file__).resolve().parent.parent / ".env")
    return env

def get_connection_string():
    env = _env()
    return "postgresql://{u}:{p}@{h}:{pt}/{d}".format(
        u=env.str("POSTGRES_USER"),
        p=env.str("POSTGRES_PASSWORD"),
        h=env.str("POSTGRES_HOST"),
        pt=env.str("POSTGRES_PORT"),
        d=env.str("POSTGRES_DB"),
    )