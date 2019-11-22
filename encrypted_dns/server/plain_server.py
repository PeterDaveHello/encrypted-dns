from encrypted_dns import parse
from encrypted_dns.server import BaseServer


class PlainServer(BaseServer):
    def __init__(self, server_config, controller_address):
        super().__init__(server_config, controller_address)
        print('Plain DNS Server listening on:',
              self.server_config['address'] + ':' + str(self.server_config['port']))

    def start(self):
        while True:
            recv_data, recv_address = self.server.recvfrom(512)
            recv_header = parse.ParseHeader.parse_header(recv_data)
            transaction_id = recv_header['transaction_id']

            if recv_header['flags']['QR'] == '0':
                if recv_address[0] not in self.server_config['client_blacklist']:
                    self.dns_map[transaction_id] = recv_address
                    self.query(recv_data)

            if recv_header['flags']['QR'] == '1' and transaction_id in self.dns_map:
                self.response(recv_data, self.dns_map[transaction_id])

    def query(self, query_data):
        self.server.sendto(query_data, self.controller_address)

    def response(self, response_data, address):
        self.server.sendto(response_data, address)