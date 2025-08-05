#!/bin/bash

echo "=== Docker Build Script for Han-Viet Translator ==="

# Build Docker image
echo "Building Docker image..."
docker build -t han-viet-translator .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    
    # Run with docker-compose
    echo "Starting application with docker-compose..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Application started successfully!"
        echo "🌐 Access the application at: http://localhost:5008"
        echo "📊 Health check: http://localhost:5008/api/health"
        
        # Wait a bit for the app to start
        echo "⏳ Waiting for application to start..."
        sleep 10
        
        # Test the API
        echo "🧪 Testing API..."
        curl -X POST http://localhost:5008/api/search \
            -H "Content-Type: application/json" \
            -d '{"query": "你好"}' \
            --max-time 30
        
        echo -e "\n🎉 Setup completed! Use 'docker-compose logs -f' to view logs"
    else
        echo "❌ Failed to start application with docker-compose"
        exit 1
    fi
else
    echo "❌ Failed to build Docker image"
    exit 1
fi 