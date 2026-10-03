"""Generate a persistent local JWT secret without printing it."""

from pathlib import Path
from secrets import token_urlsafe

BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BACKEND_DIR / ".env"
PLACEHOLDER = "replace-with-a-random-secret"


def configure_secret(env_path: Path = ENV_PATH) -> bool:
    if not env_path.exists():
        raise SystemExit("No existe backend/.env. Cree el archivo desde .env.example primero.")

    lines = env_path.read_text(encoding="utf-8").splitlines()
    changed = False
    found = False
    updated_lines: list[str] = []

    for line in lines:
        if line.startswith("SECRET_KEY="):
            found = True
            current_value = line.partition("=")[2].strip()
            if not current_value or current_value == PLACEHOLDER:
                updated_lines.append(f"SECRET_KEY={token_urlsafe(48)}")
                changed = True
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    if not found:
        updated_lines.append(f"SECRET_KEY={token_urlsafe(48)}")
        changed = True

    if changed:
        env_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    return changed


if __name__ == "__main__":
    was_changed = configure_secret()
    if was_changed:
        print("SECRET_KEY local generada y guardada sin mostrar su valor.")
    else:
        print("SECRET_KEY ya estaba configurada; no se modifico.")
