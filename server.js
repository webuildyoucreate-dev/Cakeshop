const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;

// 1. Create the server listener
const server = http.createServer((req, res) => {
    console.log(`Received request for: ${req.url}`);

    // 2. Route handling: check if user is at the homepage
    if (req.url === '/' || req.url === '/index.html') {
        const filePath = path.join(__dirname, 'index.html');

        // 3. Read the HTML file from disk
        fs.readFile(filePath, (err, content) => {
            if (err) {
                // Handle internal server error if file missing
                res.writeHead(500, { 'Content-Type': 'text/plain' });
                res.end('500 Internal Server Error');
                return;
            }
            
            // 4. Send successful headers and HTML content
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(content); 
        });
    } else {
        // 5. Handle 404 Not Found for any other URL path
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 Page Not Found</h1>');
    }
});

// 6. Start listening for network traffic
server.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
});
