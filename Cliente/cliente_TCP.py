#!/usr/bin/env python3
"""
Cliente TCP/HTTP simples para interagir com servidor Vapor
- Mantém conexão TCP aberta
- Mostra etapas (conexão, requisições, resposta, fechamento)
- Menu:
    1 - Enviar mensagem (POST /messages)
    2 - Ver mensagens (GET /messages)  
    3 - Sair (fechar conexão TCP)
    4 - Editar mensagem (PATCH /messages/message) 
"""

import socket
import json
import sys
import time
from typing import Tuple

BUFFER_SIZE = 4096

def local_ip_for_remote(remote_ip: str) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((remote_ip, 80))
        return s.getsockname()[0]
    except Exception:
        return "0.0.0.0"
    finally:
        s.close()

def recv_http_response(sock: socket.socket, timeout: float = 2.0) -> Tuple[int, dict, bytes]:
    sock.settimeout(timeout)
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
    header_part, sep, rest = data.partition(b"\r\n\r\n")
    header_lines = header_part.decode(errors="replace").split("\r\n")
    status_line = header_lines[0] if header_lines else ""
    parts = status_line.split(" ", 2)
    status_code = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0
    headers = {}
    for line in header_lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    body = rest
    if "content-length" in headers:
        try:
            length = int(headers["content-length"])
            need = length - len(body)
            while need > 0:
                chunk = sock.recv(BUFFER_SIZE)
                if not chunk:
                    break
                body += chunk
                need -= len(chunk)
        except Exception:
            pass
    else:
        try:
            time.sleep(0.05)
            while True:
                sock.settimeout(0.2)
                chunk = sock.recv(BUFFER_SIZE)
                if not chunk:
                    break
                body += chunk
        except Exception:
            pass
    return status_code, headers, body

def build_http_post(host: str, path: str, json_obj: dict, keep_alive: bool = True) -> bytes:
    body = json.dumps(json_obj).encode("utf-8")
    headers = [
        f"POST {path} HTTP/1.1",
        f"Host: {host}",
        "User-Agent: tcp-client/1.0",
        "Content-Type: application/json",
        f"Content-Length: {len(body)}",
        f"Connection: {'keep-alive' if keep_alive else 'close'}",
        "",
        ""
    ]
    head = "\r\n".join(headers).encode("utf-8")
    return head + body

def build_http_get(host: str, path: str, keep_alive: bool = True) -> bytes:
    headers = [
        f"GET {path} HTTP/1.1",
        f"Host: {host}",
        "User-Agent: tcp-client/1.0",
        f"Connection: {'keep-alive' if keep_alive else 'close'}",
        "",
        ""
    ]
    return "\r\n".join(headers).encode("utf-8")

def build_http_patch(host: str, path: str, json_obj: dict, keep_alive: bool = True) -> bytes:
    """Constrói uma requisição HTTP PATCH com JSON no body."""
    body = json.dumps(json_obj).encode("utf-8")
    headers = [
        f"PATCH {path} HTTP/1.1",
        f"Host: {host}",
        "User-Agent: tcp-client/1.0",
        "Content-Type: application/json",
        f"Content-Length: {len(body)}",
        f"Connection: {'keep-alive' if keep_alive else 'close'}",
        "",
        ""
    ]
    head = "\r\n".join(headers).encode("utf-8")
    return head + body

def pretty_print_response(status:int, headers:dict, body:bytes):
    print(f"\n--- Resposta HTTP: {status} ---")
    for k,v in headers.items():
        print(f"{k}: {v}")
    print("--- Body (raw) ---")
    try:
        txt = body.decode("utf-8")
        print(txt)
    except Exception:
        print(body)
    print("---------------\n")

def format_messages_from_body(body: bytes):
    """
    Tenta interpretar o body como JSON. Se for um array de objetos, imprime formatado:
    1) ID: <uuid>
       Client IP: <ip>
       Message: "<texto>"
       --------------------
    """
    try:
        txt = body.decode("utf-8").strip()
    except Exception:
        print("[erro] Não foi possível decodificar o body como UTF-8.")
        print(body)
        return

    if txt == "":
        print("[info] Body vazio.")
        return

    try:
        parsed = json.loads(txt)
    except json.JSONDecodeError:
        print("\n[raw body não-JSON]")
        print(txt)
        return

    if isinstance(parsed, list):
        if len(parsed) == 0:
            print("\n[vazio] Nenhuma mensagem encontrada.")
            return
        print("\n===== Mensagens recebidas =====")
        for i, item in enumerate(parsed, start=1):
            if not isinstance(item, dict):
                print(f"{i}) (tipo inesperado) {item}")
                print("--------------------")
                continue
            mid = item.get("id") or item.get("messageId") or "—"
            cip = item.get("client_ip") or item.get("clientIp") or "—"
            msg = item.get("message") or item.get("messageText") or ""
            msg_one_line = " ".join(str(msg).splitlines()).strip()
            print(f"{i}) ID: {mid}")
            print(f"   Client IP: {cip}")
            print(f'   Message: "{msg_one_line}"')
            print("--------------------")
    elif isinstance(parsed, dict):
        print("\n===== Objeto JSON =====")
        for k, v in parsed.items():
            if isinstance(v, list):
                print(f"{k}: (lista de {len(v)} itens)")
                for j, it in enumerate(v, start=1):
                    print(f"  {j}) {it}")
            else:
                print(f"{k}: {v}")
        print("--------------------")
    else:
        print("\n[JSON]")
        print(parsed)

def run_client(server_ip: str, server_port: int):
    print(f"Cliente vai conectar em {server_ip}:{server_port}")
    print("Observação: o kernel TCP realiza o three-way handshake automaticamente ao connect().")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.settimeout(5.0)

        print("-> Chamando connect() (envia SYN, aguarda SYN-ACK, envia ACK) ...")
        t0 = time.time()
        sock.connect((server_ip, server_port))
        t1 = time.time()
        print(f"Conectado! (tempo aproximado: {(t1-t0):.3f}s)")

        local_ip = local_ip_for_remote(server_ip)
        host_header = f"{server_ip}:{server_port}"

        while True:
            print("\n===== MENU =====")
            print("1 - Enviar mensagem (POST /messages)")
            print("2 - Ver mensagens (GET /messages)")
            print("3 - Sair (fechar conexão TCP)")
            print("4 - Editar mensagem (PATCH /messages/message)")
            choice = input("Escolha: ").strip()

            if choice == "1":
                texto = input("Digite a mensagem a enviar: ").strip()
                payload = {
                    "client_ip": local_ip,
                    "message": texto
                }
                req = build_http_post(host_header, "/messages", payload, keep_alive=True)
                print("\n[etapa] Enviando requisição POST ...")
                sock.sendall(req)
                print("[etapa] Requisição enviada. Aguardando resposta HTTP...")
                status, headers, body = recv_http_response(sock)
                pretty_print_response(status, headers, body)
                if headers.get("connection", "").lower() == "close":
                    print("[info] servidor indicou Connection: close — reconectando automaticamente.")
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((server_ip, server_port))
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            elif choice == "2":
                req = build_http_get(host_header, "/messages", keep_alive=True)
                print("\n[etapa] Enviando GET /messages ...")
                sock.sendall(req)
                status, headers, body = recv_http_response(sock)
                if status == 200:
                    format_messages_from_body(body)
                else:
                    print(f"[aviso] Status {status} — exibindo resposta crua:")
                    pretty_print_response(status, headers, body)
                if headers.get("connection", "").lower() == "close":
                    print("[info] servidor indicou Connection: close — reconectando automaticamente.")
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((server_ip, server_port))
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            elif choice == "4":
                # Nova opção: editar (PATCH)
                message_id = input("Digite o ID (UUID) da mensagem a editar: ").strip()
                if message_id == "":
                    print("ID vazio — operação cancelada.")
                    continue
                new_text = input("Digite o novo texto da mensagem: ").strip()
                payload = {
                    "messageId": message_id,
                    "updatedMessage": new_text
                }
                req = build_http_patch(host_header, "/messages/message", payload, keep_alive=True)
                print("\n[etapa] Enviando PATCH /messages/message ...")
                sock.sendall(req)
                status, headers, body = recv_http_response(sock)
                # se sucesso, servidor retorna o DTO atualizado (provavelmente). Tentar formatar.
                if status == 200:
                    # tentar decodificar body e mostrar resultado formatado simples
                    try:
                        parsed = json.loads(body.decode("utf-8"))
                        print("\n[sucesso] Mensagem atualizada:")
                        # parsed deve ser um objeto com id, client_ip, message
                        mid = parsed.get("id") if isinstance(parsed, dict) else "—"
                        cip = parsed.get("client_ip") if isinstance(parsed, dict) else "—"
                        msg_txt = parsed.get("message") if isinstance(parsed, dict) else str(parsed)
                        print(f"ID: {mid}")
                        print(f"Client IP: {cip}")
                        print(f'Message: "{msg_txt}"')
                        print("--------------------")
                    except Exception:
                        print("[info] Response 200, mas não foi possível decodificar JSON. Mostrando bruto:")
                        pretty_print_response(status, headers, body)
                else:
                    print(f"[aviso] Status {status} — exibindo resposta crua:")
                    pretty_print_response(status, headers, body)

                if headers.get("connection", "").lower() == "close":
                    print("[info] servidor indicou Connection: close — reconectando automaticamente.")
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((server_ip, server_port))
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            elif choice == "3":
                print("\n[etapa] Encerrando conexão TCP com FIN (fechamento gentil)...")
                try:
                    sock.shutdown(socket.SHUT_WR)
                    print("-> shutdown(SHUT_WR) chamado: FIN enviado, aguardando resposta final...")
                except Exception as e:
                    print("-> shutdown falhou:", e)
                try:
                    sock.settimeout(1.0)
                    while True:
                        chunk = sock.recv(BUFFER_SIZE)
                        if not chunk:
                            break
                except Exception:
                    pass
                try:
                    sock.close()
                except Exception:
                    pass
                print("Conexão fechada. Programa finalizando.")
                break

            else:
                print("Opção inválida. Tente 1, 2, 3 ou 4.")

    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário. Fechando socket...")
        try:
            sock.close()
        except Exception:
            pass
    except Exception as e:
        print("Erro durante a execução:", e)
        try:
            sock.close()
        except Exception:
            pass

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        SERVER_IP = sys.argv[1]
        SERVER_PORT = int(sys.argv[2]) if len(sys.argv) >= 3 else 8080
    else:
        SERVER_IP = input("IP do servidor (ex: 192.168.0.5): ").strip()
        if SERVER_IP == "":
            print("IP inválido. Saindo.")
            sys.exit(1)
        SERVER_PORT = int(input("Porta do servidor (padrão 8080): ") or 8080)

    run_client(SERVER_IP, SERVER_PORT)