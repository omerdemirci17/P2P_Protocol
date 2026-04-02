import hashlib

class MerkleTree:
    def merkle_tree(self, data_blocks=None):
        """
        data_blocks: Byte dizinlerinden olusan bir liste
        Eger alici (Leecher) isek agaci bastan kurmayiz, sadece dogrulama yapariz
        """

        self.leaves= []
        self.tree = []
        self.root_hash = None

        if data_blocks:
            self.build_tree_from_blocks(data_blocks)

    def _hash(self, data):
        "sha256 kullanarak verinin ozetini alir."
        return hashlib.sha256(data).hexdigest()

    def build_tree_from_blocks(self,data_blocks):
        "orijinal dosyadan nesiller olusturuldugunda agaci insa eder"

        #1. her bir neslin kendi hash degerini (yapraklari) olusturur
        self.leaves = [self._hash(block) for block in data_blocks]

        #2. agaci asagidan yukari dogru (yapraklardan koke) kur
        current_level = self.leaves
        self.tree = [current_level]

        while len(current_level) > 1:
            next_level= []

            #ikiserli guruplar halinde hash'leri birlestir
            for i in range(0,len(current_level),2):
                left = current_level[i]
                #eger tek sayida dugum kaldiysa, sonuncuyu kendisiyle eslestir
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                #iki hash'i birlestirip yeni bir hash olusturur (parent node)
                combined_hash = self._hash((left + right).encode('utf-8'))
                next_level.append(combined_hash)
            self.tree.append(next_level)
            current_level = next_level
        
        # en tepedeki hash, dosyanin parmak izidir (root hash)
        self.root_hash = self.tree[-1][0] if self.tree else None
    def verify_generation(self, decoded_data, expected_leaf_hash):
        """
        alici (leecher) dugum, cozdugu verinin beklenen hash ile uyumlu olup olmadigini kontrol eder
        """
        computed_hash =  self._hash(decoded_data)

        if computed_hash == expected_leaf_hash:
            return True
        else:
            return False
        
if __name__ == "__main__":
    print("merkle tree ve butunluk dogrulama testi")

    #ornek nesiller (dosyanin parcalara ayrilmis hali)
    # gercek sistemde bu byte dizileri 'file_handler' da uretilir

    orijinal_bloklar = [
        b"1.nesil: P2P sistemine hos geldin.",
        b"2.nesil: Bu veri cok onemli",
        b"3.nesil: Ag kodlamasi harika calisiyor",
        b"4.nesil: Chrun etkisine karsi dayanikliyiz"
    ]

    #kaynak dugum (SEEDER) islemleri
    print("\n[KAYNAK DUGUM] Merkle Tree insa ediliyor.")
    mt = MerkleTree(orijinal_bloklar)
    print(f"Tepe ozeti (root hash): {mt.root_hash}")
    print(f"Toplam Yaprak (nesil) sayisi: {len(mt.leaves)}")

    #alici dugum (LEECHER) islemleri
    print("\n[ALICI DUGUM] gelen nesiller dogrulaniyor.")

    #senaryo 1: veri agdan hatasiz ve kayipsiz gelir (RLNC basariyla cozuldu)
    gelen_dogru_veri = b"1.nesil: P2P sistemine hos geldin."
    beklenen_hash_0 = mt.leaves[0] #trackerdan gelen orijinal hash

    sonuc_dogru = mt.verify_generation(gelen_dogru_veri, beklenen_hash_0)
    print(f"\nSenaryo 1 (kayipsiz veri):")
    print(f"Beklenen : {beklenen_hash_0}")
    print(f"Hesaplanan: {mt._hash(gelen_dogru_veri)}")
    print(f"Sonuc   : {'ONAYLANDI - diske yaziliyor' if sonuc_dogru else 'REDDEDILDI'}")

    #senaryo 2: kotu niyetli bir es (peer) verinin arasina sizdi ve veriyi degistirdi
    gelen_bozuk_veri = b"2.nesil: Bu veri cok onemli - HACKER BURADAYDI"
    beklenen_hash_1 = mt.leaves[1]

    sonuc_bozuk = mt.verify_generation(gelen_bozuk_veri, beklenen_hash_1)
    print(f"\nSenaryo 2 (Bozuk/Zehirli veri - Pollution attack): ")
    print(f"Beklenen : {beklenen_hash_1}")
    print(f"Hesaplanan : {mt._hash(gelen_bozuk_veri)}")
    print(f"Sonuc   : {'ONAYLANDI' if sonuc_bozuk else 'HATA TESPIT EDILDI! Paket cope atildi, nesil yeniden islenecek'}")
