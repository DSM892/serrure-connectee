import socket, struct, network, time, wpa2e


class ESP32Server:

    PORT = 5000
    MAX_PACKET_SIZE = 4096

    def __init__(self, port=5000, command_handler=None):
        self.port = port
        self.command_handler = command_handler
        self.door_status = "OPEN"
        self.server = None

    def start_server(self):
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server.bind(
            ("0.0.0.0", self.port)
        )

        self.server.listen(1)

        print(
            "Serveur ESP32 démarré"
        )

        print(
            "Port TCP :",
            self.port,
            "\n"
        )

        while True:
            client, address = self.server.accept()
            print(
                "Connexion depuis :",
                address
            )

            try:
                self._handle_client(client)

            except Exception as error:
                print(
                    "Erreur :",
                    error
                )

            finally:
                client.close()
                print(
                    "Connexion fermée\n"
                )

    def server_stop(self):
        if self.server is not None:
            self.server.close()
            self.server = None
            print(
                "Serveur arrêté"
            )

    def _handle_client(self, client):

        # Réception de la commande
        command = self._receive_packet(
            client
        )

        print(
            "Paquet reçu :",
            command
        )

        if self.command_handler is not None:
            self.command_handler(command)

        # =========================
        # OPEN
        # =========================

        if command == b"OPEN":
            self._send_packet(
                client,
                b"OK"
            )
            
            return "OPEN"

        # =========================
        # CLOSE
        # =========================

        elif command == b"CLOSE":
            self._send_packet(
                client,
                b"OK"
            )
    
            return "CLOSED"

        # =========================
        # STATUS
        # =========================

        elif command == b"STATUS":

            self._send_packet(
                client,
                self.door_status.encode()
            )

        # =========================
        # PING
        # =========================

        elif command == b"PING":

            self._send_packet(
                client,
                b"PONG"
            )

        # =========================
        # Commande inconnue
        # =========================

        else:

            self._send_packet(
                client,
                b"ERROR"
            )

    def _receive_packet(self, client):

        # Les 4 premiers octets
        # indiquent la taille du message.

        header = self._receive_exactly(
            client,
            4
        )

        length = struct.unpack(
            "!I",
            header
        )[0]

        if length > self.MAX_PACKET_SIZE:

            raise ValueError(
                "Paquet trop grand"
            )

        return self._receive_exactly(
            client,
            length
        )

    def _send_packet(self, client, data):

        packet = (
            struct.pack(
                "!I",
                len(data)
            )
            + data
        )

        client.send(
            packet
        )
        
        print("Paquet envoyé :", data)

    @staticmethod
    def _receive_exactly(
        client,
        size
    ):

        data = b""

        while len(data) < size:

            chunk = client.recv(
                size - len(data)
            )

            if not chunk:

                raise ConnectionError(
                    "Connexion fermée"
                )

            data += chunk

        return data
    
    def wifi_connect(self, ssid, username, password):
        wifi = network.WLAN(network.WLAN.IF_STA)
        wifi.active(False)
        time.sleep(1)
        wifi.active(True)
        time.sleep(1)
        print("Configuration WPA2-Enterprise...")
        wpa2e.configure(
            ssid,
            username,
            password
        )
        time.sleep(1)
        print("Connexion au Wi-Fi...")
        wifi.connect(ssid)
        while not wifi.isconnected():
            time.sleep(1)
            print("Connexion en cours...")
        print("Connecté !")
        print("Adresse IP :", wifi.ifconfig()[0], "\n")

    def wifi_disconnect(self):
        wifi = network.WLAN(network.STA_IF)
        wifi.disconnect()
        wifi.active(False)
        print("Wi-Fi déconnecté.")