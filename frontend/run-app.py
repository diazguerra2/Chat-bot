#!/usr/bin/env python3
"""
Simple ISTQB Chatbot Application Launcher
Starts both backend and frontend in separate windows
"""

import os
import sys
import time
import subprocess
import webbrowser

def kill_port_processes(port):
    """Kill processes on a specific port"""
    try:
        if os.name == 'nt':  # Windows
            # Find processes using the port
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            pids = []
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            pid = int(parts[-1])
                            pids.append(pid)
                        except ValueError:
                            continue
            
            # Kill the processes
            for pid in pids:
                try:
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                 capture_output=True, check=False)
                    print(f"✅ Killed process {pid} on port {port}")
                except:
                    pass
        else:  # Unix/Linux/Mac
            subprocess.run(['pkill', '-f', f':{port}'], capture_output=True)
    except:
        pass

def main():
    print("🎯 ISTQB Chatbot Application Launcher")
    print("=" * 50)
    
    # Clean up ports
    print("🔄 Cleaning up ports...")
    kill_port_processes(8000)
    kill_port_processes(3000)
    time.sleep(2)
    
    # Start backend
    print("🚀 Starting Backend...")
    if os.name == 'nt':  # Windows
        backend_cmd = f'start "ISTQB Backend" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"'
        os.system(backend_cmd)
    else:  # Unix/Linux/Mac
        subprocess.Popen(['gnome-terminal', '--', 'python3', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'])
    
    time.sleep(3)
    
    # Start frontend
    print("🌐 Starting Frontend...")
    frontend_dir = os.path.join(os.getcwd(), 'frontend')
    if os.name == 'nt':  # Windows
        frontend_cmd = f'start "ISTQB Frontend" cmd /k "cd /d {frontend_dir} && set PORT=3001 && npm start"'
        os.system(frontend_cmd)
    else:  # Unix/Linux/Mac
        subprocess.Popen(['gnome-terminal', '--working-directory', frontend_dir, '--', 'bash', '-c', 'PORT=3001 npm start; bash'])
    
    time.sleep(5)
    
    # Open browser
    print("🌐 Opening browser...")
    try:
        webbrowser.open('http://localhost:3001')
    except:
        print("⚠️  Could not open browser automatically")
    
    print("\n" + "=" * 60)
    print("🎉 ISTQB Chatbot Application Started!")
    print("=" * 60)
    print("📊 Backend API:  http://localhost:8000")
    print("🌐 Frontend UI:  http://localhost:3001")
    print("📖 API Docs:    http://localhost:8000/docs")
    print("=" * 60)
    print("\n📝 Login Credentials:")
    print("   Email: demo@example.com")
    print("   Password: password123")
    print("\n💬 Test Messages:")
    print("   • 'Which certification should I start with?'")
    print("   • 'I have 3 years of testing experience'")
    print("   • 'Find training courses'")
    print("\n⏹️  Close the command windows to stop the services")
    print("=" * 60)

if __name__ == "__main__":
    main()
