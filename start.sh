#!/bin/bash

# HARMS Startup Script
# This script starts both the backend and frontend servers

echo "🏥 Starting Healthcare Appointment & Resource Management System (HARMS)"
echo "=================================================================="

# Check if MySQL is running
echo "📊 Checking MySQL connection..."
if ! mysqladmin ping -h localhost -u root -p111111 --silent; then
    echo "❌ MySQL is not running. Please start MySQL first."
    echo "   On macOS: brew services start mysql"
    echo "   On Ubuntu: sudo systemctl start mysql"
    exit 1
fi
echo "✅ MySQL is running"

# Check if database exists
echo "🗄️  Checking database..."
if ! mysql -h localhost -u root -p111111 -e "USE harms_db;" 2>/dev/null; then
    echo "📝 Creating database..."
    mysql -h localhost -u root -p111111 -e "CREATE DATABASE IF NOT EXISTS harms_db;"
    echo "✅ Database created"
else
    echo "✅ Database exists"
fi

# Start backend
echo "🚀 Starting Flask backend..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database with sample data
echo "🗃️  Initializing database with sample data..."
python init_db.py

# Start Flask server in background
echo "🌐 Starting Flask server on http://localhost:5000"
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting React frontend..."
cd ../frontend

# Install dependencies
echo "📥 Installing Node.js dependencies..."
npm install

# Start React development server
echo "🌐 Starting React server on http://localhost:3000"
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 HARMS is now running!"
echo "=================================================================="
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "📊 Database: MySQL (localhost:3306/harms_db)"
echo ""
echo "🔐 Demo Accounts:"
echo "   Admin: admin@harms.com / admin123"
echo "   Doctor: dr.smith@harms.com / doctor123"
echo "   Patient: patient1@harms.com / patient123"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
