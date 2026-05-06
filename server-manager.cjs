#!/usr/bin/env node

/**
 * Platter Compiler Webapp - Server Manager
 * Single script to manage both Python backend and Svelte frontend
 * Handles virtual environment creation and management
 */

const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuration
const CONFIG = {
  BACKEND_PORT: 8000,
  FRONTEND_PORT: 5173,
  BACKEND_DIR: path.join(__dirname, 'backend'),
  FRONTEND_DIR: path.join(__dirname, 'platter-compiler-sveltejs'),
  VENV_DIR: path.join(__dirname, 'backend', '.venv'),
  REQUIREMENTS_FILE: path.join(__dirname, 'backend', 'requirements.txt'),
  VENV_CHECK_FILE: path.join(__dirname, 'backend', '.venv', '.venv_complete')
};

// Global process references
let backendProcess = null;
let frontendProcess = null;
let isWindows = os.platform() === 'win32';

// Logging utilities
const log = {
  info: (msg) => console.log(`\x1b[36mINFO ${msg}\x1b[0m`),
  success: (msg) => console.log(`\x1b[32mOK   ${msg}\x1b[0m`),
  warning: (msg) => console.log(`\x1b[33mWARN ${msg}\x1b[0m`),
  error: (msg) => console.log(`\x1b[31mERR  ${msg}\x1b[0m`),
  step: (msg) => console.log(`\x1b[35mSTEP ${msg}\x1b[0m`)
};

// Utility functions
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function execPromise(command, options = {}) {
  return new Promise((resolve, reject) => {
    exec(command, options, (error, stdout, stderr) => {
      if (error) {
        reject({ error, stdout, stderr });
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
}

function isPortInUse(port) {
  return new Promise((resolve) => {
    if (isWindows) {
      // On Windows, check specifically for LISTENING state, ignore TIME_WAIT
      const command = `netstat -ano | findstr :${port}`;
      exec(command, (error, stdout) => {
        if (stdout && stdout.trim()) {
          const lines = stdout.split('\n').filter(line => line.trim());
          const isListening = lines.some(line => {
            const parts = line.trim().split(/\s+/);
            return parts.length >= 4 && 
                   (parts[1].includes(`:${port} `) || parts[1].endsWith(`:${port}`)) && 
                   parts[parts.length - 2] === 'LISTENING';
          });
          resolve(isListening);
        } else {
          resolve(false);
        }
      });
    } else {
      // Unix/Linux: use lsof which only shows active connections
      exec(`lsof -i :${port}`, (error, stdout) => {
        resolve(stdout.trim() !== '');
      });
    }
  });
}

function killProcessOnPort(port) {
  return new Promise((resolve) => {
    if (isWindows) {
      // More reliable Windows port killing with better parsing
      const command = `netstat -ano | findstr :${port}`;
      exec(command, (error, stdout) => {
        if (stdout && stdout.trim()) {
          const lines = stdout.split('\n').filter(line => line.trim());
          const pids = new Set();
          
          lines.forEach(line => {
            const trimmed = line.trim();
            // Look for lines containing our port in LISTENING or ESTABLISHED state
            if (trimmed.includes(`:${port} `) || trimmed.includes(`:${port}\t`)) {
              const parts = trimmed.split(/\s+/);
              if (parts.length >= 5) {
                const pid = parts[parts.length - 1]; // PID is always the last column
                if (pid && !isNaN(pid) && pid !== '0') {
                  pids.add(pid);
                }
              }
            }
          });
          
          if (pids.size > 0) {
            log.step(`Found ${pids.size} process(es) on port ${port}, terminating...`);
            const pidArray = Array.from(pids);
            let completed = 0;
            
            pidArray.forEach(pid => {
              exec(`taskkill /PID ${pid} /F`, (killError) => {
                if (!killError) {
                  log.info(`Killed process ${pid}`);
                } else {
                  log.warning(`Could not kill process ${pid}: ${killError.message}`);
                }
                completed++;
                if (completed === pidArray.length) {
                  // Give a moment for ports to be released
                  setTimeout(resolve, 500);
                }
              });
            });
          } else {
            resolve();
          }
        } else {
          resolve();
        }
      });
    } else {
      exec(`lsof -ti :${port}`, (error, stdout) => {
        if (stdout && stdout.trim()) {
          const pids = stdout.trim().split('\n').filter(pid => pid.trim());
          if (pids.length > 0) {
            log.step(`Found ${pids.length} process(es) on port ${port}, terminating...`);
            exec(`kill -9 ${pids.join(' ')}`, () => {
              setTimeout(resolve, 500);
            });
          } else {
            resolve();
          }
        } else {
          resolve();
        }
      });
    }
  });
}

// Virtual environment management
class VenvManager {
  static getVenvPython() {
    const pythonExe = isWindows ? 'python.exe' : 'python';
    return path.join(CONFIG.VENV_DIR, isWindows ? 'Scripts' : 'bin', pythonExe);
  }

  static getVenvActivateScript() {
    return isWindows 
      ? path.join(CONFIG.VENV_DIR, 'Scripts', 'activate.bat')
      : path.join(CONFIG.VENV_DIR, 'bin', 'activate');
  }

  static async checkVenvExists() {
    return fs.existsSync(CONFIG.VENV_DIR) && fs.existsSync(this.getVenvPython());
  }

  static async checkVenvComplete() {
    if (!await this.checkVenvExists()) return false;
    
    // Check if our completion marker exists
    if (!fs.existsSync(CONFIG.VENV_CHECK_FILE)) return false;
    
    // Verify key packages are installed
    try {
      const pythonPath = this.getVenvPython();
      await execPromise(`"${pythonPath}" -c "import fastapi, uvicorn"`);
      return true;
    } catch {
      return false;
    }
  }

  static async createVenv() {
    log.step('Creating Python virtual environment...');
    
    try {
      // Create virtual environment
      await execPromise(`python -m venv "${CONFIG.VENV_DIR}"`);
      log.success('Virtual environment created');
      
      // Install requirements
      await this.installRequirements();
      
      // Mark as complete
      fs.writeFileSync(CONFIG.VENV_CHECK_FILE, new Date().toISOString());
      log.success('Virtual environment setup complete');
      
    } catch (error) {
      log.error(`Failed to create virtual environment: ${error.error?.message || error.stderr || error}`);
      throw error;
    }
  }

  static async installRequirements() {
    if (!fs.existsSync(CONFIG.REQUIREMENTS_FILE)) {
      log.warning('requirements.txt not found, skipping package installation');
      return;
    }

    log.step('Installing Python requirements...');
    
    try {
      const pythonPath = this.getVenvPython();
      const pipCommand = isWindows 
        ? `"${pythonPath}" -m pip install -r "${CONFIG.REQUIREMENTS_FILE}"`
        : `"${pythonPath}" -m pip install -r "${CONFIG.REQUIREMENTS_FILE}"`;
      
      const result = await execPromise(pipCommand, { cwd: CONFIG.BACKEND_DIR });
      log.success('Requirements installed successfully');
      
    } catch (error) {
      log.error(`Failed to install requirements: ${error.stderr || error.error?.message}`);
      throw error;
    }
  }

  static async ensureVenv() {
    log.info('Checking Python virtual environment...');
    
    if (await this.checkVenvComplete()) {
      log.success('Virtual environment is ready');
      return;
    }
    
    if (await this.checkVenvExists()) {
      log.warning('Virtual environment exists but is incomplete, reinstalling requirements...');
      await this.installRequirements();
      fs.writeFileSync(CONFIG.VENV_CHECK_FILE, new Date().toISOString());
    } else {
      await this.createVenv();
    }
  }
}

// Server management
class ServerManager {
  static async checkDependencies() {
    log.info('Checking dependencies...');
    
    // Check if backend directory exists
    if (!fs.existsSync(CONFIG.BACKEND_DIR)) {
      throw new Error(`Backend directory not found: ${CONFIG.BACKEND_DIR}`);
    }
    
    // Check if frontend directory exists
    if (!fs.existsSync(CONFIG.FRONTEND_DIR)) {
      throw new Error(`Frontend directory not found: ${CONFIG.FRONTEND_DIR}`);
    }
    
    log.success('Project directories found');
  }

  static async checkPorts() {
    log.info('Checking port availability...');
    
    const backendInUse = await isPortInUse(CONFIG.BACKEND_PORT);
    const frontendInUse = await isPortInUse(CONFIG.FRONTEND_PORT);
    
    if (backendInUse) {
      log.warning(`Port ${CONFIG.BACKEND_PORT} is already in use (backend)`);
    }
    
    if (frontendInUse) {
      log.warning(`Port ${CONFIG.FRONTEND_PORT} is already in use (frontend)`);
    }
    
    if (backendInUse || frontendInUse) {
      const answer = await this.askQuestion('Some ports are in use. Stop existing processes? (y/N): ');
      if (answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes') {
        await this.stopServers();
      }
    }
  }

  static askQuestion(question) {
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    return new Promise((resolve) => {
      rl.question(question, (answer) => {
        rl.close();
        resolve(answer);
      });
    });
  }

  static async openBrowser(url) {
    try {
      log.step('Opening browser...');
      
      let command, args;
      
      if (isWindows) {
        command = 'cmd';
        args = ['/c', 'start', '', url];
      } else if (process.platform === 'darwin') {
        command = 'open';
        args = [url];
      } else {
        command = 'xdg-open';
        args = [url];
      }
      
      const browserProcess = spawn(command, args, {
        detached: true,
        stdio: 'ignore'
      });
      
      browserProcess.unref();
      log.success(`Browser opened to ${url}`);
      
    } catch (error) {
      log.warning(`Could not open browser automatically: ${error.message}`);
      log.info(`Please manually open: ${url}`);
    }
  }

  static async startBackend() {
    log.step('Starting Python backend server...');
    
    return new Promise((resolve, reject) => {
      const pythonPath = VenvManager.getVenvPython();
      const args = ['-m', 'uvicorn', 'main:app', '--reload', '--host', '127.0.0.1', '--port', CONFIG.BACKEND_PORT.toString()];
      
      backendProcess = spawn(pythonPath, args, {
        cwd: CONFIG.BACKEND_DIR,
        stdio: 'inherit'
      });
      
      backendProcess.on('error', (error) => {
        log.error(`Backend process error: ${error.message}`);
        reject(error);
      });
      
      backendProcess.on('spawn', () => {
        log.success(`Backend server starting on http://127.0.0.1:${CONFIG.BACKEND_PORT}`);
        resolve();
      });
      
      backendProcess.on('exit', (code) => {
        if (code !== null && code !== 0) {
          log.error(`Backend process exited with code ${code}`);
        }
        backendProcess = null;
      });
      
      // Timeout fallback in case spawn event doesn't fire
      setTimeout(() => {
        if (backendProcess && !backendProcess.killed) {
          log.success(`Backend server starting on http://127.0.0.1:${CONFIG.BACKEND_PORT}`);
          resolve();
        }
      }, 1000);
    });
  }

  static async startFrontend() {
    log.step('Starting Svelte frontend server...');
    
    return new Promise((resolve, reject) => {
      let npmCommand, args;
      
      if (isWindows) {
        // Use cmd.exe to run npm on Windows to avoid shell security warning
        npmCommand = 'cmd';
        args = ['/c', 'npm', 'run', 'dev'];
      } else {
        npmCommand = 'npm';
        args = ['run', 'dev'];
      }
      
      frontendProcess = spawn(npmCommand, args, {
        cwd: CONFIG.FRONTEND_DIR,
        stdio: 'inherit'
      });
      
      frontendProcess.on('error', (error) => {
        log.error(`Frontend process error: ${error.message}`);
        reject(error);
      });
      
      frontendProcess.on('spawn', () => {
        log.success(`Frontend server starting on http://localhost:${CONFIG.FRONTEND_PORT}`);
        resolve();
      });
      
      frontendProcess.on('exit', (code) => {
        if (code !== null && code !== 0) {
          log.error(`Frontend process exited with code ${code}`);
        }
        frontendProcess = null;
      });
      
      // Timeout fallback in case spawn event doesn't fire
      setTimeout(() => {
        if (frontendProcess && !frontendProcess.killed) {
          log.success(`Frontend server starting on http://localhost:${CONFIG.FRONTEND_PORT}`);
          resolve();
        }
      }, 1000);
    });
  }

  static async startServers() {
    console.log('\nStarting Platter Compiler Webapp...');
    console.log('=======================================\n');
    
    try {
      await this.checkDependencies();
      await VenvManager.ensureVenv();
      await this.checkPorts();
      
      log.info('Starting servers...');
      
      // Start backend
      await this.startBackend();
      await sleep(3000); // Wait for backend to start
      
      // Start frontend
      await this.startFrontend();
      await sleep(2000); // Wait for frontend to start
      
      console.log('\nServers started successfully!');
      console.log('\nURLs:');
      console.log(`   Backend API:  http://127.0.0.1:${CONFIG.BACKEND_PORT}`);
      console.log(`   Frontend UI:  http://localhost:${CONFIG.FRONTEND_PORT}`);
      console.log('\nPress Ctrl+C to stop all servers');
      
      // Open browser automatically
      await this.openBrowser(`http://localhost:${CONFIG.FRONTEND_PORT}`);
      
      console.log('\x1b[32mHappy coding!\x1b[0m\n');
      
    } catch (error) {
      log.error(`Failed to start servers: ${error.message}`);
      process.exit(1);
    }
  }

  static async stopServers() {
    console.log('\nStopping servers...');
    
    // Kill spawned processes first
    if (backendProcess) {
      log.step('Stopping backend process...');
      try {
        // Remove listeners to prevent error logging on expected termination
        backendProcess.removeAllListeners('error');
        backendProcess.removeAllListeners('exit');
        
        if (isWindows) {
          // On Windows, use taskkill for more reliable termination
          exec(`taskkill /PID ${backendProcess.pid} /T /F`, () => {});
        } else {
          backendProcess.kill('SIGTERM');
        }
        
        // Give it time to gracefully shutdown
        await sleep(1500);
      } catch (error) {
        // Suppress expected termination errors
      }
      backendProcess = null;
    }
    
    if (frontendProcess) {
      log.step('Stopping frontend process...');
      try {
        // Remove listeners to prevent error logging on expected termination
        frontendProcess.removeAllListeners('error');
        frontendProcess.removeAllListeners('exit');
        
        if (isWindows) {
          // On Windows, use taskkill for more reliable termination
          exec(`taskkill /PID ${frontendProcess.pid} /T /F`, () => {});
        } else {
          frontendProcess.kill('SIGTERM');
        }
        
        // Give it time to gracefully shutdown
        await sleep(1500);
      } catch (error) {
        // Suppress expected termination errors
      }
      frontendProcess = null;
    }
    
    // Kill any remaining processes on ports
    log.step('Cleaning up ports...');
    await killProcessOnPort(CONFIG.BACKEND_PORT);
    await killProcessOnPort(CONFIG.FRONTEND_PORT);
    
    // Wait a bit more for ports to be fully released
    await sleep(1000);
    
    log.success('All servers stopped and ports cleaned up');
  }

  static async forceStopAll() {
    console.log('\nForce stopping all processes...');
    
    // Reset process references
    backendProcess = null;
    frontendProcess = null;
    
    // Aggressively kill all related processes
    if (isWindows) {
      log.step('Force killing Python and Node processes...');
      await new Promise(resolve => {
        exec('taskkill /F /IM python.exe /T', () => {
          exec('taskkill /F /IM node.exe /T', () => {
            exec('taskkill /F /IM uvicorn.exe /T', resolve);
          });
        });
      });
    } else {
      exec('pkill -f uvicorn', () => {});
      exec('pkill -f "npm.*dev"', () => {});
      exec('pkill -f "vite"', () => {});
    }
    
    // Clean up ports aggressively
    await killProcessOnPort(CONFIG.BACKEND_PORT);
    await killProcessOnPort(CONFIG.FRONTEND_PORT);
    
    // Wait for cleanup
    await sleep(2000);
    
    log.success('Force stop completed');
  }
}

// Main execution
async function main() {
  const command = process.argv[2] || 'start';
  
  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n\nStopping servers...');
    await ServerManager.stopServers();
    process.exit(0);
  });
  
  process.on('SIGTERM', async () => {
    await ServerManager.stopServers();
    process.exit(0);
  });
  
  try {
    switch (command) {
      case 'start':
        await ServerManager.startServers();
        // Keep the process alive
        await new Promise(() => {});
        break;
        
      case 'stop':
        await ServerManager.stopServers();
        break;
        
      case 'restart':
        await ServerManager.stopServers();
        await sleep(2000);
        await ServerManager.startServers();
        await new Promise(() => {});
        break;
        
      case 'venv':
        await VenvManager.ensureVenv();
        break;
        
      case 'force-stop':
        await ServerManager.forceStopAll();
        break;
        
      default:
        console.log('Usage: node server-manager.cjs [start|stop|restart|venv|force-stop]');
        console.log('  start      - Start both servers (default)');
        console.log('  stop       - Stop all servers gracefully');
        console.log('  restart    - Restart all servers');
        console.log('  venv       - Setup/check virtual environment only');
        console.log('  force-stop - Aggressively kill all related processes');
        break;
    }
  } catch (error) {
    log.error(`Command failed: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}
