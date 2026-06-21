import subprocess
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('executor')

class ExecutionError(Exception):
    def __init__(self, command, exit_code, stderr, stdout):
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr
        self.stdout = stdout
        super().__init__(f"Command '{command}' failed with exit code {exit_code}\nStderr:\n{stderr}")

def run_command(command, cwd=None, env=None):
    """
    Executes a shell command, streams its output, and checks for errors.
    """
    logger.info(f"Executing: {command}")
    
    # We use shell=True to allow simple string commands and piping
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        env=env
    )
    
    # We will accumulate output in case we need it for error analysis
    stdout_lines = []
    stderr_lines = []

    # Read output and error streams line by line
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            line = output.strip()
            stdout_lines.append(line)
            # You can uncomment the next line to stream stdout to the console in real-time
            # print(f"[STDOUT] {line}")

    # Read the rest of stderr
    for err_line in process.stderr:
        line = err_line.strip()
        stderr_lines.append(line)
        print(f"[STDERR] {line}", file=sys.stderr)
        
    return_code = process.poll()
    
    # Ensure all output is grabbed if the process ended very fast
    stdout_rest, stderr_rest = process.communicate()
    if stdout_rest:
        stdout_lines.extend(stdout_rest.strip().split('\n'))
    if stderr_rest:
        stderr_lines.extend(stderr_rest.strip().split('\n'))

    if return_code != 0:
        logger.error(f"Execution failed with return code {return_code}")
        raise ExecutionError(
            command=command,
            exit_code=return_code,
            stderr='\n'.join(stderr_lines),
            stdout='\n'.join(stdout_lines)
        )
        
    logger.info("Execution completed successfully.")
    return '\n'.join(stdout_lines), '\n'.join(stderr_lines)
