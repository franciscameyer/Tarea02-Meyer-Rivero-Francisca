import getopt
import sys
import subprocess
import argparse
import os
import re

# Función para obtener los datos de fabricación de una tarjeta de red por IP
def obtener_datos_por_ip(ip):
    try:
        # Utiliza el comando 'arp' para obtener información de la tarjeta de red por IP
        resultado = subprocess.check_output(["arp", "-a", ip])
        # Decodifica la salida utilizando el conjunto de caracteres 'latin-1'
        resultado_decodificado = resultado.decode("latin-1")
        # Procesa el resultado para obtener la información relevante
        fabricante = obtener_fabricante_desde_arp(resultado_decodificado)
        if fabricante:
            print(f"IP address: {ip} Fabricante: {fabricante}")
        else:
            print(f"IP address: {ip} No se encontró información del fabricante.")
    except Exception as e:
        print(f"Error: {e}")

# Función para obtener los datos de fabricación de una tarjeta de red por MAC
def obtener_datos_por_mac(mac):
    # Lee el archivo 'manuf.txt' para buscar el fabricante
    try:
        with open("manuf.txt", "r", encoding="utf-8") as manuf_file:
            for line in manuf_file:
                if line.startswith(mac):
                    fabricante = line.split("\t")[1].strip()
                    return fabricante
            return ""
    except FileNotFoundError:
        print("El archivo 'manuf.txt' no se encontró en la ubicación actual. Asegúrate de que esté en la misma carpeta que este script y se llame 'manuf.txt'.")

# Función para procesar la tabla ARP
def obtener_fabricante_desde_arp(arp_output):
    lines = arp_output.split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            ip = parts[0]
            mac = parts[1]
            if ip.startswith("192.168.1.") and len(mac) == 17:
                return mac

#Parsear los argumentos de línea de comandos
parser = argparse.ArgumentParser(description="Herramienta para consultar el fabricante de una tarjeta de red dada su dirección MAC o su IP.")
parser.add_argument("--ip", help="IP del host a consultar.")
parser.add_argument("--mac", help="MAC a consultar. P.e. aa:bb:cc:00:00:00.")
parser.add_argument("--arp", help="Muestra los fabricantes de los host disponibles en la tabla arp.", action="store_true")
args = parser.parse_args()

if args.mac:
    mac_address = args.mac
    vendor = obtener_datos_por_mac(mac_address)
    if vendor:
        print(f"IP address: {mac_address} Fabricante: {vendor}")
    else:
        print(f"No se encontró información del fabricante para la dirección MAC {mac_address}.")
elif args.ip:
    ip_address = args.ip
    obtener_datos_por_ip(ip_address)
elif args.arp:
    response = os.popen("arp -a").read()
    arp_table = re.findall(r"((\d{1,3}\.){3}\d{1,3})\s+([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\s+(\w+)", response)
    print("IP/MAC/Vendor:")
    for arp_entry in arp_table:
        ip_address, _, mac_address, _, _ = arp_entry
        vendor = obtener_datos_por_mac(mac_address)
        if vendor:
            print(ip_address + " / " + mac_address + " / " + vendor)
        else:
            print(ip_address + " / " + mac_address + " / No se encontró información del fabricante.")
else:
    parser.print_help()
