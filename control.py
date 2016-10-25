ip = 'localhost'
import socket
port = 10000
# Connect to the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, port))

# Send the data
message = 'Hello, world'
print 'Sending : "%s"' % message
len_sent = s.send(message)

# Receive a response
response = s.recv(1024)
print 'Received: "%s"' % response

# Clean up
s.close()

