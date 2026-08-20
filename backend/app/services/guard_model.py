import logging
import os

logger = logging.getLogger("app.guard_model")


def model_guard(text: str) -> bool:
    """开源模型检测入口：ONNX + transformers，模型目录由配置指定。"""
    from app.core.config import get_settings

    model_dir = get_settings().prompt_guard_model_dir
    if not model_dir or not os.path.isdir(model_dir):
        raise FileNotFoundError("prompt_guard model not configured")

    import onnxruntime as ort
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    session = ort.InferenceSession(
        os.path.join(model_dir, "model.onnx"),
        providers=["CPUExecutionProvider"],
    )
    inputs = tokenizer(text, return_tensors="np", truncation=True, max_length=512)
    outputs = session.run(None, dict(inputs))[0]
    score = float(outputs[0][1]) if outputs.shape[-1] > 1 else float(outputs[0][0])
    return score >= 0.5
