#---- Image processing client ----
#--------- Written 2019 ----------
import socket
from struct import *
import threading

PORT = 8080
IPADDR = '10.19.18.85'

#Function connects up to server and sets sock
def connect_to_server(ipaddr):
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#print(sock)
	except socket.error as err:
		print("Socket creation error")
		return -1

	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		sock.connect((ipaddr, PORT))
	except socket.error as err:
		print("Error connecting to server")
		return -1

	return sock

#Function creates an message (one of the predefined ones at the top of this 
#file) and sends it
def send_message(sock, typ, receiver, lon, lat, alt):
	#Init message
	if typ == 0:
		sock.send(pack('icc', typ, b'I', b'N'))

	#Coord message
	elif typ == 1:
		sock.send(pack('iccddd', typ, b'I', receiver.encode('ascii'), lon, lat, alt))

	else:
		print("message type not recognized")

#Function constantly reads from socket
def read_message(sock):
	while True:
		buff = sock.recv(1024)
		if buff:
			#The message is an init message
			if int(buff[0]) == 0:
				msg = unpack('icc', buff[0:calcsize('icc')])
				print("Init message")

			#The message is a coord message
			elif int(buff[0]) == 1:
				msg = unpack('iccddd', buff[0:calcsize('iccddd')])
				lon = msg[3] #Is a float
				lat = msg[4] #Is a float
				alt = msg[5] #Is a float
				print("Coord message, lon: " + str(lon))

			#The message is a start message
			elif int(buff[0]) == 2:
				msg = unpack('icc', buff[0:calcsize('icc')])
				print("Start message")

			#The message is an abort message
			elif int(buff[0]) == 3:
				msg = unpack('icc', buff[0:calcsize('icc')])
				print("Abort message")

			#The message is a status message
			elif int(buff[0]) == 4:
				msg = unpack('iccdddi', buff[0:calcsize('iccdddi')])
				print("Status message")

			#The message is not recognized
			else:
				print("Message not recognized")

#How to connect to the server (do once)
#sock = connect_to_server(IPADDR)
#How to tell server that you are the image processing client (do once)
#send_message(sock, 0, 'N', 0, 0, 0)
#How to start the listening thread (do once)
#listening_thread = threading.Thread(target=read_message, args=(sock,), daemon=True)
#listening_thread.start()
#How to send a message, this is a coordinate message to main with lon 10, lat 11 and alt 12. This should not be used more than about once per second
#send_message(sock, 1, 'M', 10, 11, 12)
#How to close the listening thread, do this at the end of the code once (outside of the while loop)
#listening_thread.join()
