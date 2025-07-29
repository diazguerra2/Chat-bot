#!/usr/bin/env python3
"""
ISTQB Chatbot Application Launcher
=================================
This script starts both the FastAPI backend and React frontend,
handling port conflicts and process management automatically.
"""

import os
import sys
import time
import signal
import subprocess
import threading
import webbrowser
from typing import Optional, List

class AppLauncher:
    def __init__(self):
        self.backend_port = 8001
        self.frontend_port = 3000
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.running = True
        
        # Set OpenAI API key if available
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your-openai-api-key-here':
            print("⚠️  OpenAI API key not set. Chatbot will use rule-based responses.")
            print("   Set OPENAI_API_KEY environment variable for AI-powered responses.")
        else:
            print(f"✅ OpenAI API key configured: {api_key[:10]}...")
        
    def find_process_on_port(self, port: int) -> List[int]:
        """Find process IDs using a specific port"""
        try:
            if os.name == 'nt':  # Windows
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
                return pids
            else:  # Unix/Linux/Mac
                result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
                if result.stdout:
                    return [int(pid.strip()) for pid in result.stdout.split() if pid.strip().isdigit()]
                return []
        except Exception as e:
            print(f"Error finding processes on port {port}: {e}")
            return []

    def kill_process_on_port(self, port: int) -> bool:
        """Kill any process using the specified port"""
        pids = self.find_process_on_port(port)
        if not pids:
            return True
            
        print(f"🔄 Found processes on port {port}: {pids}")
        
        for pid in pids:
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                 capture_output=True, check=False)
                else:  # Unix/Linux/Mac
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)
                    # Force kill if still running
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # Process already dead
                print(f"✅ Killed process {pid} on port {port}")
            except Exception as e:
                print(f"❌ Failed to kill process {pid}: {e}")
                return False
        
        # Wait a moment for ports to be released
        time.sleep(2)
        return True

    def start_backend(self) -> bool:
        """Start the FastAPI backend"""
        print("\n🚀 Starting FastAPI Backend...")
        
        # Kill any existing processes on backend port
        if not self.kill_process_on_port(self.backend_port):
            print(f"❌ Failed to free port {self.backend_port}")
            return False
        
        try:
            # Start backend with environment variables
            env = os.environ.copy()
            # Ensure .env file is loaded by the backend
            env['PYTHONPATH'] = os.getcwd()
                
            self.backend_process = subprocess.Popen([
                sys.executable, 'main.py'
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Wait for backend to start and check output
            print("⏳ Waiting for backend to start...")
            
            # Monitor process output for startup completion
            for _ in range(30):  # Wait up to 30 seconds
                if self.backend_process.poll() is not None:
                    # Process died, check why
                    stdout, stderr = self.backend_process.communicate()
                    print(f"❌ Backend failed to start. Output: {stdout}")
                    return False
                
                time.sleep(1)
                
                # Test if the server is responding
                try:
                    import requests
                    response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Backend started successfully on http://localhost:{self.backend_port}")
                        return True
                except:
                    continue
            
            print("❌ Backend failed to start within timeout")
            return False
                
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False

    def start_frontend(self) -> bool:
        """Start the React frontend"""
        print("\n🌐 Starting React Frontend...")
        
        # Kill any existing processes on frontend port
        if not self.kill_process_on_port(self.frontend_port):
            print(f"⚠️  Port {self.frontend_port} busy, React will use next available port")
        
        try:
            # Change to frontend directory
            frontend_dir = os.path.join(os.getcwd(), 'frontend')
            if not os.path.exists(frontend_dir):
                print("❌ Frontend directory not found")
                return False
            
            # Start frontend
            env = os.environ.copy()
            env['BROWSER'] = 'none'  # Prevent auto-opening browser
            
            # Use correct npm command for Windows
            npm_cmd = 'npm.cmd' if os.name == 'nt' else 'npm'
            
            self.frontend_process = subprocess.Popen([
                npm_cmd, 'start'
            ], cwd=frontend_dir, env=env, stdout=subprocess.PIPE, 
               stderr=subprocess.STDOUT, text=True, shell=True)
            
            # Wait for frontend to start and capture the actual port
            print("⏳ Waiting for frontend to compile...")
            actual_port = self.frontend_port
            
            for _ in range(60):  # Wait up to 60 seconds
                if self.frontend_process.poll() is not None:
                    print("❌ Frontend failed to start")
                    return False
                
                # Try to read output to detect successful compilation
                try:
                    # Check if we can read from stdout
                    output = self.frontend_process.stdout.readline()
                    if 'webpack compiled successfully' in output or 'Compiled successfully' in output:
                        print(f"✅ Frontend compiled successfully!")
                        break
                    if 'Something is already running on port' in output:
                        # React will automatically choose next port
                        actual_port = self.frontend_port + 1
                except:
                    pass
                
                time.sleep(1)
            
            self.frontend_port = actual_port
            print(f"✅ Frontend available at http://localhost:{self.frontend_port}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return False

    def open_browser(self):
        """Open the application in the default browser"""
        try:
            time.sleep(2)  # Give the app a moment to fully start
            url = f"http://localhost:{self.frontend_port}"
            print(f"\n🌐 Opening browser: {url}")
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")

    def monitor_processes(self):
        """Monitor both processes and restart if needed"""
        while self.running:
            try:
                # Check backend
                if self.backend_process and self.backend_process.poll() is not None:
                    print("⚠️  Backend process died, restarting...")
                    self.start_backend()
                
                # Check frontend
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("⚠️  Frontend process died, restarting...")
                    self.start_frontend()
                
                time.sleep(5)  # Check every 5 seconds
            except KeyboardInterrupt:
                break

    def cleanup(self):
        """Clean up processes on exit"""
        print("\n🛑 Shutting down...")
        self.running = False
        
        if self.backend_process:
            print("⏹️  Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("⏹️  Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        # Final cleanup of ports
        self.kill_process_on_port(self.backend_port)
        self.kill_process_on_port(self.frontend_port)
        
        print("✅ Cleanup complete")

    def run(self):
        """Main application runner"""
        print("🎯 ISTQB Chatbot Application Launcher")
        print("=" * 50)
        
        try:
            # Start backend
            if not self.start_backend():
                print("❌ Failed to start backend. Exiting.")
                return False
            
            # Start frontend
            if not self.start_frontend():
                print("❌ Failed to start frontend. Exiting.")
                self.cleanup()
                return False
            
            # Open browser
            browser_thread = threading.Thread(target=self.open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Show status
            print("\n" + "=" * 60)
            print("🎉 ISTQB Chatbot Application is Running!")
            print("=" * 60)
            print(f"📊 Backend API:  http://localhost:{self.backend_port}")
            print(f"🌐 Frontend UI:  http://localhost:{self.frontend_port}")
            print("=" * 60)
            print("\n📝 Login Credentials:")
            print("   Email: demo@example.com")
            print("   Password: demo")
            print("\n💬 Test the Chatbot with:")
            print("   • 'Which certification should I start with?'")
            print("   • 'I have 3 years of testing experience'")
            print("   • 'Find training courses'")
            print("\n⏹️  Press Ctrl+C to stop both services")
            print("=" * 60)
            
            # Monitor and keep running
            monitor_thread = threading.Thread(target=self.monitor_processes)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Received shutdown signal...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            self.cleanup()
        
        return True

def main():
    launcher = AppLauncher()
    return launcher.run()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
