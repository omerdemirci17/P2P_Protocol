import galois
import numpy as np
from packet import Packet

GF = galois.GF(2**8)

def test_packet():
    print("---1. paket olusturma ---")
    #RLNC motorundan cikmis gibi sahte veri hazirlama
    sahte_file_id = "A8B9C10D..."
    sahte_gen_id = 0
    sahte_katsayilar = GF([[1,5,25], [10,20,30]])
    sahte_veri = GF([[100,200], [50,60]])

    #paket olusturma
    orijinal_paket = Packet(
        file_id=sahte_file_id,
        generation_id= sahte_gen_id,
        coefficients= sahte_katsayilar,
        payload= sahte_veri
        )
    print("Orijinal paket:", orijinal_paket)

    print("\n---2. AGA GONDERME (SERIALIZATION)---")
    #paketi byte a cevir
    giden_bytelar = orijinal_paket.to_bytes()
    print(f"Paket basariyla byte dizisine cevrildi. Boyut {len(giden_bytelar)} byte")

    print("\n---3. AGDAN ALMA (DESERIALIZATION)---")
    #karsi tarafin (Leecher) paketi alip geri acmasini simulasyonu
    gelen_paket = Packet.from_bytes(giden_bytelar)

    #4. dogrulama: giden veri ile gelen veri matematiksel olarak ayni mi
    if  np.array_equal(orijinal_paket.coefficients, gelen_paket.coefficients):
        print("\n BASARILI: Katsayi matrisleri bozunmadan tasindi!")
    else:
        print("\n HATA: Katsayilar yolda bozuldu!")

if __name__ =="__main__":
    test_packet()