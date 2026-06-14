# HostingPlatform

Introduction:
What: An automated benchmarking platform designed to stress-test trading algorithms by simulating real-world market conditions like order books and matching engines.
Who: Built for competitive algorithmic traders and developers who need an objective, reliable environment to validate the performance and safety of their strategies.
Why: To solve the challenge of evaluating unverified code safely and fairly, providing immediate feedback on metrics like (Accuracy, Stability, Speed) without risking our host server's integrity or stability.


Tech Stack:
        Frontend:
                Html
                JavaScript
        Backend:
                Python
                FastAPI
        Execution:
                Docker Engine


Functions/Features of the Platform:
        Ingestion: It accepts source code files from contestants via a web portal.
       Isolation: It automatically spins up a clean, temporary Docker sandbox for every submission to ensure the code runs securely without touching your host machine.
                   Compilation: It handles the building of binaries for multiple languages (C++, Go, Rust, Java, Python) inside those isolated environments.
                   Execution: It runs the code against a performance test, enforcing a 5-second time limit to prevent system crashes.
                   Telemetry: It parses the script's output to extract specific performance metrics (Accuracy, Stability, and Speed).
                    Leaderboard Management: It instantly updates and sorts the live rankings based on the extracted metrics.
                   Sanitisation: It wipes the sandbox environment immediately after execution to keep the server clean and ready for the next entry.




Core Working Steps:
Ingestion: The user submits their source code file and team identity via the web portal.
Sandbox Isolation: The backend starts a fresh Docker container (the "sandbox") to ensure the code cannot access our server.
Injection: The code is copied directly into the isolated container's memory layer.  
Execution: The system runs the appropriate compiler or interpreter (like g++ or python3) within that sandbox, enforced by a 5-second hard time limit.
Telemetry Extraction: The engine monitors the output stream to break down performance markers (metrics_start and metrics_end).
Leaderboard Update: The extracted data is processed and used to update the live leaderboard.
Resource Reclamation: The system immediately deletes the container to free up server resources. 


System Data Flow:
1. Submission Request:

         1.1 Code Payload: 

           File Format Restrictions: To maintain compatibility with our execution engines, only authorised file extensions (e.g., .py, cpp, rs) are permitted. All other formats are programmatically rejected upon upload.
             Size Constraints: Each submission is limited to a maximum file size (e.g., 500KB) to prevent storage exhaustion.
             Sanitisation & Content Inspection: Before ingestion, files undergo basic header inspection to ensure the file content matches the declared extension. This prevents the execution of malicious scripts.
         1.2 Metadata: 
Identity: Each request must include a unique team name to attribute the submission to the correct participant.
Contextual Data: Include necessary environment variables, such as language version (e.g., Python 3.12, C++20) and submission timestamp for leaderboard tracking.
         1.3 Validation Pipeline:
Pre-Processing Checks: Before reaching the Docker orchestration layer, the request is validated for schema integrity (ensuring all required metadata fields are present).
Rate Limiting: To prevent API abuse, the system imposes a cooling-off period between submissions for each team.
2. Orchestration Details: The orchestration layer acts as the bridge between the API and the isolated runtime. It manages the lifecycle of the user's code from initialisation to termination:
      2.1 Environment Setup:
Container Initialisation: Upon validation, the backend triggers the Docker Engine to spawn a fresh container instance.
Resource Mounting: The validated code payload is securely mounted into a read-only directory within the container, preventing the user code from modifying its own source files during execution.
Environment Injection: Metadata (e.g., language version) is injected as environment variables to configure the runtime (e.g., selecting the appropriate compiler or interpreter version).
   2.2  Execution Lifecycle: 
Standardised Runtime: The container executes the code within a restricted user-space to limit privileges.
I/O Capture: The system monitors stdout and stderr streams in real-time, capturing program output and runtime errors for later analysis.
Termination Triggers: A strict execution timer is applied. If the process exceeds the allocated time limit, the container is forcibly terminated to prevent an "infinite loop".
    2.3 Resource Policing:
Namespace Isolation: Usage of Docker namespaces ensures the process cannot view or interact with host-level processes or other contestant containers.
Hardware Capping: Hard limits are applied to CPU shares and RAM usage via control groups (cgroups), ensuring no single submission can starve the host system of resources.
Network Restriction: The container is configured with no external network access (or strictly proxied access) to prevent unauthorised calls to external APIs.
3. Feedback Loop Details:.
         3.1 Result Capture:
Stream Aggregation: The system continuously monitors and collects stdout and stderr streams, storing them in a structured format (e.g., JSON) rather than raw text files.
Exit Status Mapping: The container's exit code is mapped to specific human-readable states (e.g.,0 for Success,1 for Runtime Error, 124 for Time Limit Exceeded) to inform the user why their code behaved a certain way.
        3.2 Data Normalisation:
Format Standardisation: Regardless of the language (Python, C++, Rust), all outputs are parsed into a uniform schema to ensure the leaderboard and dashboard can process them consistently.
Log Truncation: To prevent UI clutter and database strain, log files are truncated to a maximum character length, with a provided link to the full execution trace for deep debugging.
3.3   Communication Layer:
Event-Driven Notification: Upon process termination, the orchestration layer triggers an asynchronous event to notify the backend API.
Push Updates: The backend uses WebSockets to push the final status and performance metrics (e.g., execution time, memory usage) to the user's dashboard in real-time.
