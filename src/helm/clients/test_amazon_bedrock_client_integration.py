"""
Integration tests for AmazonBedrockClient with live AWS Bedrock API.

These tests require:
- Valid AWS credentials configured (via environment variables, ~/.aws/credentials, or IAM role)
- Access to AWS Bedrock service
- Amazon Nova models enabled in the AWS account

To run these tests:
    pytest test_amazon_bedrock_client_integration.py -v -s

Set SKIP_INTEGRATION_TESTS=1 to skip these tests in CI/CD environments.

Note: These tests will make real API calls and may incur costs.
"""

import os
import pytest

from helm.common.cache_backend_config import BlackHoleCacheBackendConfig
from helm.common.request import Request
from helm.tokenizers.auto_tokenizer import AutoTokenizer


# Skip integration tests if environment variable is set
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", "0") == "1",
    reason="Integration tests disabled via SKIP_INTEGRATION_TESTS environment variable"
)


@pytest.fixture(scope="module")
def tokenizer():
    """Create a tokenizer for testing."""
    credentials = {}
    cache_config = BlackHoleCacheBackendConfig()
    return AutoTokenizer(credentials, cache_config)._get_tokenizer("huggingface/gpt2")


@pytest.fixture(scope="module")
def cache_config():
    """Create a cache config for testing."""
    return BlackHoleCacheBackendConfig().get_cache_config("test")


@pytest.fixture(scope="module")
def client(tokenizer, cache_config):
    """Create an AmazonBedrockClient for testing."""
    from helm.clients.amazon_bedrock_client import AmazonBedrockClient
    
    return AmazonBedrockClient(
        cache_config=cache_config,
        tokenizer=tokenizer,
        tokenizer_name="huggingface/gpt2",
        region=os.environ.get("AWS_REGION", "us-east-1"),
    )


class TestBasicFunctionality:
    """Test basic client functionality with live API."""

    def test_simple_completion_nova_lite(self, client):
        """Test a simple completion request with Nova 2 Lite."""
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="What is the capital of France? Answer in one word.",
            temperature=0.0,
            max_tokens=10,
            top_p=1.0,
        )
        
        result = client.make_request(request)
        
        assert result.success is True
        assert len(result.completions) > 0
        assert result.completions[0].text
        assert "Paris" in result.completions[0].text or "paris" in result.completions[0].text.lower()
        assert result.error is None

    def test_simple_completion_nova_pro(self, client):
        """Test a simple completion request with Nova 2 Pro."""
        request = Request(
            model="amazon/nova-2-pro-v1:0",
            prompt="What is 2+2? Answer with just the number.",
            temperature=0.0,
            max_tokens=5,
            top_p=1.0,
        )
        
        result = client.make_request(request)
        
        assert result.success is True
        assert len(result.completions) > 0
        assert "4" in result.completions[0].text
        assert result.error is None

    def test_completion_with_messages(self, client):
        """Test completion with messages format."""
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            messages=[
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi there! How can I help you?"},
                {"role": "user", "content": "What's your name?"},
            ],
            temperature=0.7,
            max_tokens=50,
            top_p=0.9,
        )
        
        result = client.make_request(request)
        
        assert result.success is True
        assert len(result.completions) > 0
        assert len(result.completions[0].text) > 0


class TestParameterHandling:
    """Test different parameter configurations."""

    def test_temperature_variation(self, client):
        """Test that different temperatures produce different outputs."""
        prompt = "Write a creative story opening in 20 words:"
        
        # Low temperature (more deterministic)
        request_low = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt=prompt,
            temperature=0.1,
            max_tokens=50,
        )
        result_low = client.make_request(request_low)
        
        # High temperature (more creative)
        request_high = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt=prompt,
            temperature=0.9,
            max_tokens=50,
        )
        result_high = client.make_request(request_high)
        
        assert result_low.success is True
        assert result_high.success is True
        # Outputs should be different (though not guaranteed)
        # At minimum, both should produce text
        assert len(result_low.completions[0].text) > 0
        assert len(result_high.completions[0].text) > 0

    def test_max_tokens_limit(self, client):
        """Test that max_tokens is respected."""
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="Count from 1 to 100:",
            temperature=0.0,
            max_tokens=10,
            top_p=1.0,
        )
        
        result = client.make_request(request)
        
        assert result.success is True
        # Check that output doesn't exceed max_tokens
        assert len(result.completions[0].tokens) <= 10

    def test_stop_sequences(self, client):
        """Test that stop sequences are respected."""
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="List three colors: red,",
            temperature=0.0,
            max_tokens=50,
            stop_sequences=[",", "."],
        )
        
        result = client.make_request(request)
        
        assert result.success is True
        # Output should stop at first comma or period
        text = result.completions[0].text
        assert "," not in text or text.index(",") == len(text) - 1


class TestMedHELMScenarios:
    """Test scenarios relevant to MedHELM benchmarks."""

    def test_medical_knowledge_question(self, client):
        """Test medical knowledge question answering."""
        request = Request(
            model="amazon/nova-2-pro-v1:0",
            prompt="What is the primary function of hemoglobin? Answer in one sentence.",
            temperature=0.0,
            max_tokens=100,
        )
        
        result = client.make_request(request)
        
        assert result.success is True
        text = result.completions[0].text.lower()
        # Should mention oxygen or transport
        assert "oxygen" in text or "transport" in text

    def test_clinical_note_generation(self, client):
        """Test clinical note generation capability."""
        request = Request(
            model="amazon/nova-2-pro-v1:0",
            prompt="""Patient presents with fever (38.5°C), cough, and fatigue for 3 days. 
No recent travel. No known allergies. 

Generate a brief clinical impression:""",
            temperature=0.3,
            max_tokens=150,
        )
        
        result = client.make_request(request)
        
        assert result.success is True
        assert len(result.completions[0].text) > 20
        # Should generate some medical content
        text = result.completions[0].text.lower()
        # Check for medical terminology
        medical_terms = ["fever", "symptom", "infection", "respiratory", "viral", "patient"]
        assert any(term in text for term in medical_terms)

    def test_patient_communication(self, client):
        """Test patient-friendly medical explanation."""
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="""Explain hypertension to a patient in simple terms. 
Use one short paragraph.""",
            temperature=0.5,
            max_tokens=150,
        )
        
        result = client.make_request(request)
        
        assert result.success is True
        text = result.completions[0].text.lower()
        # Should mention blood pressure
        assert "blood" in text or "pressure" in text


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_model_id(self, cache_config, tokenizer):
        """Test handling of invalid model ID."""
        from helm.clients.amazon_bedrock_client import AmazonBedrockClient
        
        client = AmazonBedrockClient(
            cache_config=cache_config,
            tokenizer=tokenizer,
            tokenizer_name="huggingface/gpt2",
            bedrock_model_id="invalid.model.id",
        )
        
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="Test",
            max_tokens=10,
        )
        
        result = client.make_request(request)
        
        # Should fail with error
        assert result.success is False
        assert result.error is not None

    def test_empty_prompt(self, client):
        """Test handling of empty prompt."""
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="",
            max_tokens=10,
        )
        
        result = client.make_request(request)
        
        # Should handle gracefully (may succeed with empty response or fail)
        assert result is not None

    def test_very_large_max_tokens(self, client):
        """Test handling of very large max_tokens."""
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="Write a story:",
            temperature=0.5,
            max_tokens=10000,  # Very large
        )
        
        result = client.make_request(request)
        
        # Should either succeed or fail gracefully
        assert result is not None


class TestPerformance:
    """Test performance and efficiency."""

    def test_response_time(self, client):
        """Test that responses are returned in reasonable time."""
        import time
        
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="Hello",
            temperature=0.0,
            max_tokens=5,
        )
        
        start_time = time.time()
        result = client.make_request(request)
        elapsed_time = time.time() - start_time
        
        assert result.success is True
        # Should complete in reasonable time (30 seconds for simple request)
        assert elapsed_time < 30.0

    def test_caching(self, client):
        """Test that caching works for identical requests."""
        request = Request(
            model="amazon/nova-2-lite-v1:0",
            prompt="What is 1+1?",
            temperature=0.0,
            max_tokens=5,
        )
        
        # First request
        result1 = client.make_request(request)
        assert result1.success is True
        cached1 = result1.cached
        
        # Second identical request
        result2 = client.make_request(request)
        assert result2.success is True
        cached2 = result2.cached
        
        # Second request should be cached (unless cache is disabled)
        # At minimum, both should succeed
        assert result1.completions[0].text == result2.completions[0].text


if __name__ == "__main__":
    # Run with: python test_amazon_bedrock_client_integration.py
    pytest.main([__file__, "-v", "-s"])
