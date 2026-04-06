from file_handler import FileHandler
from rlnc_engine import RlncEngine
from integrity_check import MerkleTree
from packet import Packet
import galois
import numpy as np

GF = galois.GF(2**8)

class Node:

    """"
    P2P agindaki her bir cihazi temsil eden ana dugum sinifi.
    Kendi icinde dosya islemlerini ve matematik motorunu barindirir.
    """
    def __init__(self, node_id):
        #seeder
        self.node_id = node_id
        self.file_handler = FileHandler()
        self.rlnc_engine = RlncEngine()
        self.merkle_tree = None

        #leecher
        self.receive_buffer = {}
        self.expected_rank = 4

    def share_file(self, file_path):
        """
        Bir dosyayi P2P agina sunmak (Seeding) icin gereken tum sureci yonetir. 
        Parcala -> Imzala -> Kodla -> Paketle
        """
        print(f"\n [{self.node_id}] OTO-SUREC BASLATILDI: {file_path}")

        #--- 1. ADIM: PARCALA ---
        print("-> 1/4: Dosya okunuyor ve nesillere (generations) ayriliyor...")
        generations, original_size = self.file_handler.file_to_generations(file_path)

        #Simulasyonu basitlestirmek icin simdilik sadece ilk nesili (Gen 0) isle
        gen_0_data = generations[0]
        print(f"    * Nesil 0 yuklendi. (Parca sayisi: {len(gen_0_data)})")

        #--- 2. ADIM: IMZALA ---
        print("-> 2/4: Merkle Tree olusturuluyor ve Root Hash hesaplaniyor...")
        merkle = MerkleTree(gen_0_data)
        root_hash = merkle.root_hash
        print(f"    * Guvenlik Muhru (Root Hash):{root_hash}")

        #--- 3. ADIM: KODLA ---
        print("-> 3/4 RLNC Motoru ile veri isleniyor (Encode)...")
        #RLNC motoruna gondermeden once veriyi Galois matrisine cevir
        gen_matrix = GF(gen_0_data)

        #4 orijinal parcadan, aga salmak uzere 6 yedekli paket uret
        coef_matix, encoded_payloads = self.rlnc_engine.rlnc_encode(gen_matrix, num_encoded_packets=6)

        #--- 4. ADIM: PAKETLE ---
        print("-> 4/4: Agda ucacak P2P Paketleri (DTO) hazirlaniyor...")
        ready_packets = []
        for i in range(len(coef_matix)):
            pkt = Packet(
                file_id= root_hash,
                generation_id=0,
                coefficients=coef_matix[i],
                payload=encoded_payloads[i]
            )
            ready_packets.append(pkt)

        print(f"[{self.node_id}] ISLEM TAMAM! {len(ready_packets)} adet paket aga (soketlere) salinmaya hazir.\n")
        return ready_packets

    def receive_pack(self, packet):
        """
        Agdan gelen paketi havuza alir, rank kontrolu yapar ve gerekirse motoru tetikler.
        """
        gen_id = packet.gen_id

        #bu nesil icin daha once havuz acilmadiysa, yeni bir tane ac
        if gen_id not in self.receive_buffer:
            self.receive_buffer[gen_id] = {'coefs': [], 'payloads': [], 'current_rank':0}
        
        buffer = self.receive_buffer[gen_id]

        #eger bu nesli zaten cozduysek, paketi direkt cope at
        if buffer['current_rank'] == self.expected_rank:
            print(f"[{self.node_id}] Paket Iptal: {gen_id} zaten tamamlandi")
            return
        
        #yeni paketi gecici olarak listeye ekle ve rank'i olc 
        temp_coefs = buffer['coefs'] + [packet.coefficients]
        yeni_rank = np.linalg.matrix_rank(GF(temp_coefs))

        if yeni_rank > buffer['current_rank']:
            #Rank artti! Bu paket lineer bagimsizdir, kabul et.
            buffer['coefs'].append(packet.coefficients)
            buffer['payloads'].append(packet.payload)
            buffer['current_rank'] = yeni_rank
            print(f"[{self.node_id}] Paket Kabul | Guncel Rank: {yeni_rank}/{self.expected_rank}")

            #hedef rank'a (4'e) ulastiysak, paket beklemeyi birak ve coz
            if yeni_rank == self.expected_rank:
                print(f"[{self.node_id}] Nesil {gen_id} TAMAMLANDI! Cozumleme basliyor...")
                self._decode_and_verify(gen_id, packet.file_id)
        else:
            #Rank artmadi! Bu paket kopya (lineer bagimli) veri tasiyor
            print(f"[{self.node_id}] Paket REDDEDILDI! (Lineer bagimli/ Cop Veri)")
        
    def _decode_and_verify(self, gen_id, expected_node_hash):
        """
        Tam rank'a ulasan havuzu cozer ve Merkle ile dogrular.
        """
        buffer = self.receive_buffer[gen_id]
        received_coefs = GF(buffer['coefs'])
        received_payloads = GF(buffer['payloads'])

        #1. Coz (Decode)
        decoded_gen = self.rlnc_engine.rlnc_decode(received_coefs, received_payloads)

        #2. Merkle ile Dogrula (Guvenlik Kontrolu)
        merkle = MerkleTree(decoded_gen)
        if merkle.root_hash == expected_node_hash:
            print(" GUVENLIK ONAYI: Dosya yolda bozulmamis! (Hash: {merkle.root_hash[:10]}...)")
            print(f"[{self.node_id}] ISLEM BASARILI! Nesil {gen_id} diske yazilmaya hazir.\n")
        else:
            print(f"    GUVENLIK IHLALI: Dosya bozuk veya kirlilik saldirisi (Pollution) tespit edildi!")

#test
if __name__ == "__main__":
    #test icin sahte dosya olustur
    test = "ornek.txt"
    with open(test,"w") as f:
        f.write("Bu node sinifi tarafindan orkestre edilecek cok onemli bir veridir.")
    
    #dugumu ayaklandir ve dosyayi paylasmasini iste
    dugum = Node(node_id="Seeder_Node_1")
    uretilen_paketler = dugum.share_file(test)

    #cikan paketlerden birinin ici
    ornek_paket = uretilen_paketler[0]
    print(f"ORNEK PAKET INCELEMESI")
    print(f" - Dosya ID (Root Hash):{ornek_paket.file_id}")
    print(f" - Nesil: {ornek_paket.generation_id}")
    print(f" - Katsayilar: {ornek_paket.coefficients}")
