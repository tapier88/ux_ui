"""
Qwen Adapter - Abstraction layer for Qwen-Agent LLM provider
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


class QwenAgentProvider(LLMProvider):
    """Qwen-Agent LLM provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None, 
                 endpoint: Optional[str] = None,
                 model: str = "qwen-max"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model
        self._status = ProviderStatus.DISCONNECTED
        self._client = None
        
        # Check if we have credentials
        if not api_key or not endpoint:
            self._status = ProviderStatus.ERROR
    
    def connect(self) -> bool:
        """Connect to Qwen-Agent service"""
        if not self.api_key or not self.endpoint:
            self._status = ProviderStatus.ERROR
            return False
        
        try:
            # NOTE: In a real implementation, this would initialize the Qwen-Agent client
            # Example:
            # from qwen_agent import Client
            # self._client = Client(api_key=self.api_key, endpoint=self.endpoint)
            
            # For now, we'll fall back to mock if no real client is available
            self._status = ProviderStatus.ERROR
            return False
            
        except Exception as e:
            self._status = ProviderStatus.ERROR
            return False
    
    def disconnect(self):
        """Disconnect from Qwen-Agent service"""
        self._client = None
        self._status = ProviderStatus.DISCONNECTED
    
    def is_connected(self) -> bool:
        """Check if connected to Qwen-Agent service"""
        return self._status == ProviderStatus.CONNECTED
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response from Qwen-Agent"""
        if not self.is_connected():
            raise RuntimeError("Not connected to Qwen-Agent service")
        
        try:
            # NOTE: Real implementation would call Qwen-Agent here
            # response = self._client.generate(
            #     prompt=request.prompt,
            #     system_prompt=request.system_prompt,
            #     temperature=request.temperature,
            #     max_tokens=request.max_tokens
            # )
            
            # Placeholder - should not reach here in mock mode
            return LLMResponse(
                content="[QWEN RESPONSE] This would be a real Qwen response",
                metadata={"model": self.model, "provider": "qwen-agent"}
            )
            
        except Exception as e:
            raise RuntimeError(f"Qwen-Agent generation failed: {str(e)}")
    
    def get_status(self) -> ProviderStatus:
        """Get Qwen-Agent provider status"""
        return self._status


class LLMAdapterFactory:
    """Factory for creating LLM providers"""
    
    _providers: Dict[str, LLMProvider] = {}
    
    @classmethod
    def create_provider(cls, provider_type: str, **kwargs) -> LLMProvider:
        """Create an LLM provider instance"""
        if provider_type == "mock":
            return MockLLMProvider()
        elif provider_type == "qwen":
            return QwenAgentProvider(
                api_key=kwargs.get("api_key"),
                endpoint=kwargs.get("endpoint"),
                model=kwargs.get("model", "qwen-max")
            )
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
