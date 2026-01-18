"""
Bedrock client utilities for LLM and image generation.
"""

import base64
import json
from typing import Any

from config.aws import get_bedrock_client
from config.settings import settings


class BedrockClient:
    """Client for Amazon Bedrock model invocations."""

    def __init__(self) -> None:
        self.client = get_bedrock_client()
        self.model_id = settings.bedrock_model_id
        self.image_model_id = settings.bedrock_image_model_id

    def invoke_claude(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stop_sequences: list[str] | None = None,
    ) -> str:
        """
        Invoke Claude model with a prompt.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            stop_sequences: Optional stop sequences

        Returns:
            The model's response text
        """
        messages = [{"role": "user", "content": prompt}]

        body: dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
        }

        if system_prompt:
            body["system"] = system_prompt

        if stop_sequences:
            body["stop_sequences"] = stop_sequences

        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )

        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]

    def invoke_claude_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """
        Invoke Claude model with tool use capability.

        Args:
            prompt: The user prompt
            tools: List of tool definitions
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation

        Returns:
            The full response including tool calls
        """
        messages = [{"role": "user", "content": prompt}]

        body: dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
            "tools": tools,
        }

        if system_prompt:
            body["system"] = system_prompt

        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )

        return json.loads(response["body"].read())

    def converse(
        self,
        modelId: str,
        messages: list[dict[str, Any]],
        system: list[dict[str, str]] | None = None,
        toolConfig: dict[str, Any] | None = None,
        inferenceConfig: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Use Bedrock Converse API for agentic workflows.

        Args:
            modelId: Model identifier
            messages: Conversation messages
            system: System prompts
            toolConfig: Tool configuration
            inferenceConfig: Inference parameters

        Returns:
            Converse API response
        """
        params: dict[str, Any] = {
            "modelId": modelId,
            "messages": messages,
        }

        if system:
            params["system"] = system

        if toolConfig:
            params["toolConfig"] = toolConfig

        if inferenceConfig:
            params["inferenceConfig"] = inferenceConfig
        else:
            params["inferenceConfig"] = {
                "maxTokens": 4096,
                "temperature": 0.7,
            }

        return self.client.converse(**params)

    def generate_image(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        width: int = 1024,
        height: int = 1024,
        quality: str = "standard",
        cfg_scale: float = 8.0,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate an image using Amazon Nova Canvas.

        Args:
            prompt: Text description of the image to generate
            negative_prompt: What to avoid in the image
            width: Image width in pixels
            height: Image height in pixels
            quality: Image quality (standard/premium)
            cfg_scale: How closely to follow the prompt (1-20)
            seed: Random seed for reproducibility

        Returns:
            Dictionary with image data (base64) and metadata
        """
        body: dict[str, Any] = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
            },
            "imageGenerationConfig": {
                "width": width,
                "height": height,
                "quality": quality,
                "cfgScale": cfg_scale,
                "numberOfImages": 1,
            },
        }

        if negative_prompt:
            body["textToImageParams"]["negativeText"] = negative_prompt

        if seed is not None:
            body["imageGenerationConfig"]["seed"] = seed

        response = self.client.invoke_model(
            modelId=self.image_model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )

        response_body = json.loads(response["body"].read())

        # Extract the base64 image
        images = response_body.get("images", [])
        if images:
            return {
                "success": True,
                "image_base64": images[0],
                "prompt": prompt,
                "width": width,
                "height": height,
            }

        return {
            "success": False,
            "error": "No image generated",
            "response": response_body,
        }

    def generate_campaign_image(
        self,
        product_name: str,
        campaign_type: str,
        promotion_text: str | None = None,
        occasion: str | None = None,
        style: str = "modern and professional",
    ) -> dict[str, Any]:
        """
        Generate a campaign image for SK Brands.

        Args:
            product_name: Name of the product to feature
            campaign_type: Type of campaign (banner/social/email)
            promotion_text: Promotion text to include (e.g., "20% OFF")
            occasion: Occasion if any (e.g., "Diwali", "Summer Sale")
            style: Visual style description

        Returns:
            Dictionary with generated image data
        """
        # Build the prompt
        prompt_parts = [
            f"Create a {style} promotional {campaign_type} for SK Brands clothing store",
            f"featuring {product_name}",
        ]

        if occasion:
            prompt_parts.append(f"for {occasion} celebration")

        prompt_parts.extend(
            [
                "Premium Indian retail aesthetic",
                "Clean, elegant design with brand colors (navy blue and gold)",
                "Professional photography style",
                "Space for text overlay",
            ]
        )

        if promotion_text:
            prompt_parts.append(f"Include visual elements suggesting '{promotion_text}'")

        prompt = ". ".join(prompt_parts) + "."

        negative_prompt = (
            "blurry, low quality, distorted text, unprofessional, "
            "cluttered, cheap looking, watermarks"
        )

        # Set dimensions based on campaign type
        dimensions = {
            "banner": (1456, 832),  # Wide banner
            "social": (1024, 1024),  # Square for Instagram
            "email": (1024, 512),  # Email header
            "whatsapp": (800, 800),  # WhatsApp share
        }

        width, height = dimensions.get(campaign_type, (1024, 1024))

        return self.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            quality="standard",
            cfg_scale=10.0,
        )


# Global client instance
bedrock_client = BedrockClient()
