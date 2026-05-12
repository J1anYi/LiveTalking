#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify DashScope Embedding API model name and dimensions"""
import os
import sys

def verify_embedding():
    """Test DashScope Embedding API"""
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key:
        print("DASHSCOPE_API_KEY environment variable not set")
        print("Please set environment variable:")
        print("  Windows: set DASHSCOPE_API_KEY=your-key")
        print("  Linux/Mac: export DASHSCOPE_API_KEY=your-key")
        return None

    try:
        from openai import OpenAI
    except ImportError:
        print("openai library not installed, please run: pip install openai")
        return None

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # Test different model names
    models_to_test = ["text-embedding-v3", "text-embedding-v2", "text-embedding-v1"]

    for model in models_to_test:
        try:
            print(f"\nTesting model: {model}")
            response = client.embeddings.create(
                model=model,
                input=["This is a test text"]
            )

            embedding = response.data[0].embedding
            dimensions = len(embedding)

            print(f"  [OK] Success!")
            print(f"  Model: {model}")
            print(f"  Dimensions: {dimensions}")
            print(f"  First 5 values: {embedding[:5]}")

            return {
                "model": model,
                "dimensions": dimensions,
                "status": "success"
            }

        except Exception as e:
            print(f"  [FAIL] Error: {e}")

    return {"status": "failed", "error": "All model names failed"}

if __name__ == "__main__":
    result = verify_embedding()
    if result:
        print(f"\nFinal result: {result}")
    else:
        print("\nVerification failed: Please check API key configuration")
