Commandes pour effacer l'ancien firmware et flasher le nouveau:
python -m esptool --chip esp32 --port COM4 erase-flash
python -m esptool --chip esp32 --port COM4 --baud 460800 write-flash --flash-mode dio --flash-size 4MB --flash-freq 40m 0x1000 CHEMIN_VERS_bootloader.bin 0x8000 CHEMIN_VERS_partition-table.bin 0x10000 CHEMIN_VERS_micropython.bin