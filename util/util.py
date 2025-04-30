from util.model import Env

def get_env_color(env: Env) -> str:
    match env:
        case Env.DEV:
            return "green"
        case Env.SIT:
            return "yellow1"
        case Env.SAT:
            return "dark_orange"
        case Env.PROD:
            return "red"
