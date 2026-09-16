class WifiPacketError(Exception):
    """Erreur générale de la bibliothèque."""


class ConnectionError(WifiPacketError):
    """Erreur de connexion réseau."""


class PacketError(WifiPacketError):
    """Erreur concernant un paquet."""


class TimeoutError(WifiPacketError):
    """Une opération réseau a dépassé le délai."""


class CommandError(WifiPacketError):
    """L'appareil a refusé ou mal exécuté une commande."""