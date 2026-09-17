import socket
import struct

from .exceptions import (
    ConnectionError,
    PacketError,
    TimeoutError,
    CommandError,
)


class Client:

    MAX_PACKET_SIZE = 4096

    ALLOWED_COMMANDS = {
        b"OPEN",
        b"CLOSE",
        b"STATUS",
        b"PING",
    }

    def __init__(
        self,
        ip,
        port=5000,
        timeout=3
    ):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def open(self):
        response = self._send_command(
            b"OPEN"
        )

        if response != b"OK":
            raise CommandError(
                f"Réponse inattendue pour OPEN : "
                f"{response!r}"
            )

        return True

    def close(self):
        response = self._send_command(
            b"CLOSE"
        )

        if response != b"OK":
            raise CommandError(
                f"Réponse inattendue pour CLOSE : "
                f"{response!r}"
            )

        return True

    def status(self):
        response = self._send_command(
            b"STATUS"
        )

        if response == b"OPEN":
            return "OPEN"

        if response == b"CLOSED":
            return "CLOSED"

        raise CommandError(
            f"Réponse STATUS invalide : "
            f"{response!r}"
        )

    def ping(self):
        response = self._send_command(
            b"PING"
        )

        if response != b"PONG":
            raise CommandError(
                f"Réponse inattendue pour PING : "
                f"{response!r}"
            )

        return True

    def _send_command(self, command):

        # Vérification de la commande
        if command not in self.ALLOWED_COMMANDS:
            raise CommandError(
                f"Commande interdite : {command!r}"
            )

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:
            sock.settimeout(
                self.timeout
            )

            # =========================
            # Connexion
            # =========================

            try:
                print(
                    "Connexion vers :",
                    self.ip,
                    self.port
                )
                sock.connect(
                    (self.ip, self.port)
                )

                print(
                    "Connexion établie"
                )

            except socket.timeout as error:
                raise TimeoutError(
                    f"Connexion vers "
                    f"{self.ip}:{self.port} "
                    f"trop longue"
                ) from error

            except OSError as error:
                raise ConnectionError(
                    f"Impossible de se connecter à "
                    f"{self.ip}:{self.port}"
                ) from error

            # =========================
            # Envoi
            # =========================

            packet = (
                struct.pack(
                    "!I",
                    len(command)
                )
                + command
            )

            try:
                sock.sendall(
                    packet
                )

                print(
                    "Paquet envoyé :",
                    command
                )

            except socket.timeout as error:
                raise TimeoutError(
                    "Délai d'envoi dépassé"
                ) from error

            except OSError as error:
                raise ConnectionError(
                    "Erreur lors de l'envoi"
                ) from error

            # =========================
            # Réception
            # =========================

            try:
                # Les 4 premiers octets indiquent
                # la taille de la réponse
                header = self._receive_exactly(
                    sock,
                    4
                )

                length = struct.unpack(
                    "!I",
                    header
                )[0]

                # Protection contre un paquet
                # anormalement grand
                if length > self.MAX_PACKET_SIZE:
                    raise PacketError(
                        f"Paquet trop grand : "
                        f"{length} octets"
                    )

                # Réception de la réponse complète
                response = self._receive_exactly(
                    sock,
                    length
                )

                print(
                    "Paquet reçu :",
                    response
                )

                return response

            except socket.timeout as error:
                raise TimeoutError(
                    "Délai de réception dépassé"
                ) from error

        except (
            TimeoutError,
            ConnectionError,
            PacketError
        ):
            raise

        except OSError as error:
            raise ConnectionError(
                "Erreur réseau"
            ) from error

        finally:
            # La connexion est toujours fermée
            # après une communication.
            sock.close()
            print(
                "Connexion fermée\n"
            )

    @staticmethod
    def _receive_exactly(
        sock,
        size
    ):
        data = b""

        while len(data) < size:

            chunk = sock.recv(
                size - len(data)
            )

            if not chunk:
                raise ConnectionError(
                    "La connexion a été fermée "
                    "avant la fin du paquet"
                )

            data += chunk

        return data