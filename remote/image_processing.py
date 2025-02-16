import socketserver

class ImageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        print(data)

        #TODO process the data and like, AI/ML ASL that shtuff

        #TODO actually send the corct character
        socket = self.request[1]
        socket.sendto(bytes("X", "UTF-8"), self.client_address)

if __name__ == "__main__":
    HOST, PORT = "localhost", 5000

    with socketserver.UDPServer((HOST, PORT), ImageHandler) as server:
        server.serve_forever()