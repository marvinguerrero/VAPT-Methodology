import re
import subprocess
from openpyxl import Workbook

def run_nmap_command(targets, output_file):
    nmap_command = f"nmap -sC -sV -T4 -v5 -oN {output_file} {' '.join(targets)}"
    subprocess.run(nmap_command, shell=True)

def parse_nmap_output(nmap_output_file):
    with open(nmap_output_file, 'r') as f:
        lines = f.readlines()

    results = []
    current_host = None

    for line in lines:
        line = line.strip()

        # Match host lines
        host_match = re.match(r'^Nmap scan report for (.+)', line)
        if host_match:
            current_host = host_match.group(1)
            continue

        # Match service lines
        service_match = re.match(r'^(\d+)/(tcp|udp)\s+(open|filtered|closed)\s+(.+)\s+([\w/.]+)?', line)
        if service_match and current_host:
            port = service_match.group(1)
            protocol = service_match.group(2)
            state = service_match.group(3)
            service = service_match.group(4)
            product = service_match.group(5)
            results.append((current_host, port, protocol, state, service, product))

    return results

def write_to_excel(results, output_excel):
    wb = Workbook()
    ws = wb.active
    ws.title = "Nmap Results"
    headers = ["URL", "IP Address", "Port", "Protocol", "State", "Service", "Product"]
    ws.append(headers)

    for result in results:
        host = result[0]
        # Extract URL and IP address
        url_match = re.match(r'(.+) \((.+)\)', host)
        if url_match:
            url, ip_address = url_match.groups()
        else:
            url, ip_address = host, ""
        # Write to Excel
        row = [url, ip_address] + list(result[1:])
        ws.append(row)

    wb.save(output_excel)
    print(f"Nmap results extracted and saved to {output_excel}")

if __name__ == "__main__":
    targets_file = input("Enter the path to the file containing target URLs: ").strip()  # Remove leading/trailing whitespace
    with open(targets_file, 'r') as f:
        targets = [line.strip() for line in f.readlines()]
    nmap_output_file = "nmap_scan.txt"  # Output file name for Nmap scan
    output_excel = input("Enter output Excel file name (e.g., results.xlsx): ")

    # Run Nmap command
    run_nmap_command(targets, nmap_output_file)

    # Parse Nmap output
    results = parse_nmap_output(nmap_output_file)

    # Write results to Excel
    write_to_excel(results, output_excel)
