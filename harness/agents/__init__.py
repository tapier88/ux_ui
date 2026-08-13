"""
Agent provider abstractions.

The harness runs on local infrastructure by default. Provider classes expose a
stable interface for tests and future adapters, but no external Qwen connection
is required or planned for normal operation.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class ProviderStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    MOCK = "mock"


@dataclass
class LLMRequest:
    """LLM request structure"""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """LLM response structure"""
    content: str
    usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "usage": self.usage,
            "metadata": self.metadata
        }


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the LLM service"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the LLM service"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the LLM service"""
        pass
    
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def get_status(self) -> ProviderStatus:
        """Get the current provider status"""
        pass


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing without real credentials"""
    
    def __init__(self):
        self._status = ProviderStatus.MOCK
        self._call_count = 0
    
    def connect(self) -> bool:
        """Mock connection - always succeeds"""
        self._status = ProviderStatus.MOCK
        return True
    
    def disconnect(self):
        """Mock disconnection"""
        self._status = ProviderStatus.DISCONNECTED
    
    def is_connected(self) -> bool:
        """Check mock connection status"""
        return self._status in [ProviderStatus.CONNECTED, ProviderStatus.MOCK]
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate mock response"""
        self._call_count += 1
        
        # Generate a mock response based on the prompt
        mock_content = f"[MOCK RESPONSE] I received your prompt: '{request.prompt[:50]}...'"
        
        return LLMResponse(
            content=mock_content,
            usage={
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": len(mock_content.split()),
                "total_tokens": len(request.prompt.split()) + len(mock_content.split())
            },
            metadata={
                "model": "mock-model",
                "provider": "mock",
                "call_number": self._call_count
            }
        )
    
    def call(self, prompt: str, **kwargs) -> LLMResponse:
        """Alternative method signature for compatibility"""
        request = LLMRequest(prompt=prompt, **kwargs)
        return self.generate(request)
    
    def get_status(self) -> ProviderStatus:
        """Get mock provider status"""
        return self._status
    
    def get_call_count(self) -> int:
        """Get number of calls made"""
        return self._call_count


class LocalInfrastructureProvider(MockLLMProvider):
    """
    Local provider used by this harness.

    It deliberately does not require credentials, endpoints, or remote Qwen
    infrastructure. The implementation remains deterministic so tests and agent
    workflows are reproducible inside this workspace.
    """

    def __init__(self, model: str = "local-codex-infra"):
        super().__init__()
        self.model = model

    def generate(self, request: LLMRequest) -> LLMResponse:
        self._call_count += 1
        content = (
            "[LOCAL INFRA RESPONSE] "
            f"Processed prompt locally: '{request.prompt[:50]}...'"
        )
        return LLMResponse(
            content=content,
            usage={
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": len(content.split()),
                "total_tokens": len(request.prompt.split()) + len(content.split()),
            },
            metadata={
                "model": self.model,
                "provider": "local-infrastructure",
                "call_number": self._call_count,
            },
        )


class QwenAgentProvider(LocalInfrastructureProvider):
    """
    Backward-compatible alias for older code paths.

    The project no longer connects to Qwen. Instantiating this class runs on the
    local infrastructure provider so legacy references do not break while the
    public direction remains local-first.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(model=kwargs.get("model", "local-codex-infra"))


class LLMAdapterFactory:
    """Factory for creating LLM providers"""
    
    _providers: Dict[str, LLMProvider] = {}
    
    @classmethod
    def create_provider(cls, provider_type: str, **kwargs) -> LLMProvider:
        """Create an LLM provider instance"""
        if provider_type == "mock":
            return MockLLMProvider()
        elif provider_type in ("local", "local-infrastructure"):
            return LocalInfrastructureProvider(
                model=kwargs.get("model", "local-codex-infra")
            )
        elif provider_type == "qwen":
            return QwenAgentProvider(model=kwargs.get("model", "local-codex-infra"))
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @classmethod
    def get_or_create(cls, name: str, provider_type: str, **kwargs) -> LLMProvider:
        """Get existing provider or create new one"""
        if name not in cls._providers:
            cls._providers[name] = cls.create_provider(provider_type, **kwargs)
        return cls._providers[name]
    
    @classmethod
    def get_provider(cls, name: str) -> Optional[LLMProvider]:
        """Get a registered provider by name"""
        return cls._providers.get(name)
    
    @classmethod
    def remove_provider(cls, name: str) -> bool:
        """Remove a registered provider"""
        if name in cls._providers:
            del cls._providers[name]
            return True
        return False


# Global default provider (mock by default)
_default_provider: Optional[LLMProvider] = None


def get_default_provider() -> LLMProvider:
    """Get or create the default provider (mock)"""
    global _default_provider
    if _default_provider is None:
        _default_provider = MockLLMProvider()
        _default_provider.connect()
    return _default_provider


def set_default_provider(provider: LLMProvider):
    """Set the default provider"""
    global _default_provider
    _default_provider = provider


def generate(prompt: str, **kwargs) -> LLMResponse:
    """Convenience function to generate using default provider"""
    provider = get_default_provider()
    request = LLMRequest(prompt=prompt, **kwargs)
    return provider.generate(request)


from harness.agents.judgment import (  # noqa: E402
    BaseDesignJudgmentEngine,
    DesignJudgmentRequest,
    DesignJudgmentResult,
)

from harness.agents.design_cycle import (  # noqa: E402
    AgentCycleResult,
    AgentCycleStep,
    AgentDecision,
    DeterministicDesignAgent,
)
