import socket
import threading
from packet import Packet

class NetworkLayer:
    def __init__(self, node_id,host,port,on_packet_received_callback):
        """
        sadece fiziksel veri iletisimi ile ilgilenen ag katmani
        on_packet_received_callback: agdan bir sey geldiginde kime haber verecegini bilir
        """

        self.node_id = node_id
        self.host = host
        self.port = port

        #ajanimiz bir paket yakaladiginda bu fonksiyona paslayacak (tetikleyici)
        self.on_packet_received = on_packet_received_callback
        
        self.sock=None
        self.is_listenig = False

    def start_listening(self):
        """UDP Soketini acar ve arka planda dinlemeye baslar"""

        self.is_listening = True
        self.sock= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.bind((self.host,self.port))

        listen_thread = threading.Thread(target=self._listen_loop,daemon=True)
        listen_thread.start()
        print(f"[{self.node_id}] AG KATMANI AKTIF: {self.host}:{self.port} dinleniyor...")

    def _listen_loop(self):
        """Asenkron dinleme dongusu."""
        while self.is_listenig:
            try:
                data,addr = self.sock.recvfrom(65535)
                if data:
                    print(f"\n---> [AG] {addr} adresinden fiziksel baglanti yakaladi! Node'a iletiliyor...")
                    gelen_paket = Packet.from_bytes(data)

                    #yakalanan paketi Node'un Smart Buffer'ina gonder
                    self.on_packet_received(gelen_paket)

            except Exception as e:
                if self.is_listenig:
                    print(f"[{self.node_id}] AG hatasi:{e}")
    
    def send_packet(self,packet,target_ip,target_port):
        """Node'dan gelen paketi dis dunyaya (hedef IP/Port) firlatir"""
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = packet.to_bytes()
        send_sock.sendto(data, (target_ip,target_port))
        send_sock.close()