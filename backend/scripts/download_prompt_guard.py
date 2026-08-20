import os
from pathlib import Path

from huggingface_hub import snapshot_download

REPO_ID = "ProtectAI/deberta-v3-base-prompt-injection-v2"


def main() -> None:
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    target = Path(__file__).resolve().parent.parent / "guard_model"
    target.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=REPO_ID, local_dir=str(target))
    print(f"模型已下载到: {target}")


if __name__ == "__main__":
    main()
