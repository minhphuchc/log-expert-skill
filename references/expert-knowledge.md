# Log Analysis Expert Knowledge

This document contains expert knowledge for analyzing system and application logs on GCE (Google Compute Engine) instances.

## Common Log Locations
- `/var/log/syslog`
- `/var/log/auth.log`
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`

## Analysis Techniques
1. Identifying error patterns (ERROR, CRITICAL, FATAL).
2. Correlating timestamps across different log files.
3. Summarizing frequency of occurrences.
4. **Pattern & Anomaly Detection**:
    - **Retry Storm**: Look for a spike in 5xx errors accompanied by high CPU. Pattern: `[5xx errors count] > 10x normal`.
    - **Cascading Failure**: Database timeouts leading to API hang. Pattern: `DB timeout -> API 504 -> App Unresponsive`.
    - **Memory Leak**: Check `free -h` over time. Pattern: `available memory decreasing` + `swap usage increasing`.

## Log Pattern Library

### Linux System
- **OOM Kill**: `kernel: out of memory: Kill process [PID] (node) score 950 or sacrifice child`.
- **Disk Full**: `No space left on device`, `ext4_add_entry: [inode] No space left in directory`.
- **Auth Fail**: `sshd[PID]: Failed password for invalid user [NAME] from [IP] port [PORT] ssh2`.

### Nginx
- **Rate Limit**: `[error] ... limiting requests, excess: 0.500 by zone "mylimit"`.
- **Upstream Timeout**: `[error] ... upstream timed out (110: Connection timed out) while connecting to upstream`.
- **404 Surge**: `[info] ... GET /wp-login.php HTTP/1.1" 404` (Potential scanning/attack).

### Database (PostgreSQL/MySQL)
- **Lock Wait**: `PostgreSQL: ERROR: deadlock detected`, `MySQL: Error: 1205 SQLSTATE: HY000 (ER_LOCK_WAIT_TIMEOUT)`.
- **Max Connections**: `FATAL: remaining connection slots are reserved for non-replication superuser connections`.
- **Slow Query**: `[Note] ... query_time: 10.500000 lock_time: 0.000000 rows_sent: 50000 rows_examined: 1000000`.

## Common Error Library

### JSON Syntax
- **Description**: The system fails to parse a JSON string, often due to unexpected characters or incorrect formatting.
- **Log pattern**: `SyntaxError: Unexpected token '`'`, `JSON.parse: unexpected character`, `Expecting value: line 1 column 1 (char 0)`.
- **Root cause**: The source of the JSON string (like an LLM response or a file) included extra formatting characters (e.g., Markdown code blocks like ` ```json `) or the data was corrupted.
- **Resolution**: Clean the JSON string by removing Markdown wrappers or ensuring the source only returns valid JSON. Implement robust parsing with validation.

### OpenAI API Timeout
- **Description**: Requests to the OpenAI API exceed the allowed time limit without receiving a response.
- **Log pattern**: `openai.error.Timeout`, `Request timed out`, `Status Code: 408`, `Gateway Timeout`.
- **Root cause**: High network latency, API rate limits, or heavy load on OpenAI servers.
- **Resolution**: Implement retry logic with exponential backoff. Increase the request timeout in the client configuration. Optimize prompts to reduce response size.

### DB Connection
- **Description**: The application is unable to establish or maintain a connection to the database.
- **Log pattern**: `ConnectionRefusedError`, `OperationalError: (psycopg2.OperationalError) FATAL: remaining connection slots are reserved`, `Can't connect to MySQL server on 'localhost'`.
- **Root cause**: Database server is down, connection pool is exhausted, incorrect credentials, or firewall issues.
- **Resolution**: Check database server status. Increase connection pool size. Verify credentials and network access rules.

### OOM (Out of Memory)
- **Description**: The system or a process runs out of available memory, leading to crashes or poor performance.
- **Log pattern**: `out of memory: Kill process`, `java.lang.OutOfMemoryError`, `Fatal error: Allowed memory size of ... bytes exhausted`.
- **Root cause**: Memory leaks, processing excessively large data sets, or insufficient RAM allocated to the instance.
- **Resolution**: Identify and fix memory leaks. Increase memory allocation. Optimize data processing to use streaming instead of loading everything into memory.

### CPU High
- **Description**: CPU usage consistently stays at or near 100%, causing the system to become unresponsive.
- **Log pattern**: `High CPU usage detected`, `top` output showing 100% CPU for a process, `Load average: 10.0, 8.0, 5.0`.
- **Root cause**: Infinite loops, unoptimized algorithms, heavy computations, or high traffic.
- **Resolution**: Profile the application to find CPU-intensive code. Optimize algorithms. Scale horizontally by adding more instances or vertically by increasing CPU cores.
