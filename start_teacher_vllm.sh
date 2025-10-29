#!/bin/bash

# 🏴‍☠️ MAROONED - Start vLLM Teacher Server
# Run this in a separate terminal before training

echo "=================================="
echo "🧑‍🏫 Starting vLLM Teacher Server"
echo "=================================="
echo ""
echo "Model: Meta-Llama-3.1-8B-Instruct"
echo "Port: 8000"
echo "API: http://localhost:8000/v1/chat/completions"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

# Check if vLLM is installed
if ! python -c "import vllm" 2>/dev/null; then
    echo "⚠️  vLLM not found. Installing..."
    pip install vllm
fi

# Start vLLM server
vllm serve unsloth/Meta-Llama-3.1-8B-Instruct \
    --dtype bfloat16 \
    --max-model-len 8192 \
    --port 8000
