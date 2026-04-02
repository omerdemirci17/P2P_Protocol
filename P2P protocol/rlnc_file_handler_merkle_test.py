from integrity_check import MerkleTree
from rlnc_engine import RlncEngine
from file_handler import FileHandler

def p2p_master_test():
    print("===P2P MIMARISI UCTAN UCA TEST===")

    #classlari baslatma
    fh = FileHandler()
    re = RlncEngine()

    #temsili orijinal dosya (byte bizisi)
    orijinal_dosya_verisi = b"P2P_Network_Coding_Architecture_Test_Data_12345"

    print("\n[1.Asama - Kaynak dugum (seeder)]")
    #dosyayi parcalara bol

    nesiller = re.rlnc_encode(orijinal_dosya_verisi, num_encoded_packets=5)
    print("[-] File Handler: Dosya {len(nesiller)} parcaya bolundu")

    #Merkle agaci butunluk ozeti olusturma
    mt = MerkleTree(nesiller)
    beklenen_yapraklar = mt.leaves
    print(f"[-] Merkle Tree: Root Hash olusturuldu -> {mt.root_hash}")

    #RLNC ile parcalari kodla (matris islemleri)
    kodlanmis_paketler = re.rlnc_encode(nesiller)
    print(f"[-] RLNC Engine: Veriler ag uzerinden gonderilmek uzerde kodlandi")


    print("\n[2. ASAMA - ALICI  DUGUM (leecher)]")
    #Kodlanmis paketler ag uzerinden aliciya ulasti (simulasyon)
    alinan_paketler = kodlanmis_paketler

    #alici, gelen sifreli RLNC paketlerini orijinal verilere cozer
    cozulmus_nesiller = re.rlnc_decode(alinan_paketler)
    print("[-]RLNC ENGINE: Gelen paketler cozuldu")

    #Cozule nesillerin butunlugu Merkle Tree ile dogrula
    dogrulanmis_nesiller = []
    hatali_nesil_var = False

    for i in range(len(cozulmus_nesiller)):
        #mt.verify_generation metodunu kullanarak eldeki veriyi tracker'dan gelen hash ile kiyasla
        if mt.verify_generation(cozulmus_nesiller):
            dogrulanmis_nesiller.append(cozulmus_nesiller[i])
        else:
            print(f"HATA!: {i+1}. Nesilde kirlilik (Pollution) tespit edildi")
            hatali_nesil_var = True
    
    print("\n[3. ASAMA - SONUC]")
    #eger merkle kontrolunduen hepsi basariyla gectiyse, dosyayi diskte birlestir
    if not hatali_nesil_var:
        final_dosya = fh.generations_to_file(dogrulanmis_nesiller)
        print("DURUM: KUSURSUZ! Butunluk Onaylandi")
        print(f"-> Gonderilen: {orijinal_dosya_verisi}")
        print(f"-> Birlestirilen {final_dosya}")
    else:
        print("DURUM: BASARISIZ! Guvenlik sistemine  takilan veriler oldugu icin dosya diske yazilmadi")

if __name__ == "__main__":
    p2p_master_test()