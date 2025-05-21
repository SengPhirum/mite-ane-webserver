import os
import socket


def create_server_socket(port):
    """Attempts to create and bind a server socket on the given port.
    If the port is in use, it tries the next port number.
    """
    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('', port))
            server_socket.listen(1) # Listen for only one connection at a time
            print(f"Server listening on port: {port}")
            return server_socket, port
        except OSError as e:
            if e.errno == socket.errno.EADDRINUSE: # Address already in use
                print(f"Port {port} is already in use. Trying next port.")
                port = 8080
                port += 1
            else:
                raise # Reraise other OSError exceptions

def handle_request(connection_socket, addr):
    """Handles an incoming HTTP request."""
    try:
        message = connection_socket.recv(1024).decode()
        if not message: # Handle empty request
            return

        print(f"\nReceived request:\n{message.splitlines()[0]}") # Log only the first line of request

        # Parse the request to get the filename
        filename = message.split()[1]
        # Ensure filename starts with '/' and remove it for local file access
        if filename == '/':
            filename = '/index.html' # Default file
        
        filepath = filename[1:] # Remove leading '/'

        # Get the requested file
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                outputdata = f.read()
            
            # Determine content type based on file extension
            content_type = "text/html" # Default
            if filepath.endswith(".jpg") or filepath.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif filepath.endswith(".png"):
                content_type = "image/png"
            elif filepath.endswith(".css"):
                content_type = "text/css"
            elif filepath.endswith(".js"):
                content_type = "application/javascript"

            # Create HTTP response message
            header = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(outputdata)}\r\n\r\n"
            response = header.encode() + outputdata
            print(f"Sending file: {filepath}")
        else:
            # File not found, return 404 error
            error_message = "<html><head></head><body><h1>404 Not Found</h1></body></html>"
            header = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: {len(error_message)}\r\n\r\n"
            response = header.encode() + error_message.encode()
            print(f"File not found: {filepath}. Sending 404 error.")

        # Send the response
        connection_socket.sendall(response)

    except IndexError:
        print("Error: Malformed HTTP request.")
        # Optionally send a bad request error to the client
        error_response = "HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n<html><body><h1>400 Bad Request</h1></body></html>"
        connection_socket.sendall(error_response.encode())
    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally send a server error to the client
        error_response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n<html><body><h1>500 Internal Server Error</h1></body></html>"
        connection_socket.sendall(error_response.encode())
    finally:
        # Close client connection socket
        connection_socket.close()
        print(f"Connection from: {addr} closed")

def start_server():
    """Starts the web server."""
    default_port = 80
    server_socket, actual_port = create_server_socket(default_port)
    print(f"\nReady to serve on port {actual_port}...")

    try:
        while True:
            # Wait for an incoming connection
            connection_socket, addr = server_socket.accept()
            print(f"Accepted connection from: {addr}")
            
            # Handle the client request
            handle_request(connection_socket, addr)
            
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()

if __name__ == '__main__':
    start_server()