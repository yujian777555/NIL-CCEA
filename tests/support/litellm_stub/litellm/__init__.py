"""Phase 0B 无 API 测试用 LiteLLM stub。"""


class _LiteLLMStub:
    def __init__(self):
        self.client_session = None
        self.aclient_session = None
        self.success_callback = []
        self.drop_params = True

    def disable_cache(self):
        pass

    def enable_cache(self):
        pass


litellm = _LiteLLMStub()
client_session = None
aclient_session = None
success_callback = []
drop_params = True


def completion(*args, **kwargs):
    raise RuntimeError("API calls disabled in Phase 0B no-API test")


def completion_cost(*args, **kwargs):
    return 0.0


def disable_cache():
    pass


def enable_cache():
    pass
