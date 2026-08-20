"""OpenTelemetry 全链路观测初始化。

职责：
- 初始化 TracerProvider，通过 OTLP 上报到 Tempo（Grafana 观测栈）。
- FastAPI（HTTP 请求）/ SQLAlchemy（数据库）/ httpx（Qdrant 等外部调用）自动埋点。
- 提供 get_tracer() 供 LLM 调用、工具执行等处打手动 span。
- 所有初始化与导出失败一律静默降级：观测层故障绝不阻塞业务。

注意：本模块顶层不 import opentelemetry，全部惰性导入，
保证未安装 OTel 依赖时应用也能正常启动（观测只是加分项）。

配置（backend/.env）：
- OTEL_EXPORTER_OTLP_ENDPOINT：OTLP HTTP 接收地址，默认 http://tempo:4318
- OTEL_SERVICE_NAME：服务名，默认 aigc-backend
"""
import logging

logger = logging.getLogger("app.telemetry")

_initialized = False


def setup_telemetry() -> bool:
    """幂等初始化 OTel；失败返回 False，不影响应用启动。"""
    global _initialized
    if _initialized:
        return True
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import (
            SQLAlchemyInstrumentor,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        from app.core.config import get_settings
        from app.db.session import engine

        s = get_settings()
        if not s.otel_enabled:
            logger.info("telemetry disabled by config")
            _initialized = True
            return True

        resource = Resource.create({"service.name": s.otel_service_name})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=s.otel_exporter_otlp_endpoint)
            )
        )
        trace.set_tracer_provider(provider)

        # 自动埋点：HTTP 路由、数据库操作、外部 HTTP 调用
        FastAPIInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument(engine=engine)
        HTTPXClientInstrumentor().instrument()

        _initialized = True
        logger.info("telemetry initialized endpoint=%s", s.otel_exporter_otlp_endpoint)
        return True
    except Exception as exc:
        logger.warning("telemetry init failed (%s), run without tracing", exc)
        return False


def get_tracer():
    """获取应用命名空间的 Tracer；未初始化/未安装依赖时返回 None。

    调用方约定：`tr = get_tracer()`，为 None 时跳过埋点（无操作）。
    """
    if not _initialized:
        return None
    try:
        from opentelemetry import trace

        return trace.get_tracer("aigc.app")
    except Exception:
        return None

