import numpy as np
import galois

GF = galois.GF(2**8)
class RlncEngine:
    def rlnc_encode(self, data, num_encoded_packets):
        """
        rastgele dogrusal kombinasyonlarla sifreler
        """
        if not isinstance(data, galois.FieldArray):
            #byte dizilerini integer listesine cevirip GF matirsine donustur
            matris_verisi = [list(blok) for blok in data]
            data_matris = GF(matris_verisi)
        else:
            data_matris = data

        num_chunks = data_matris.shape[0]

        #rastgele katsayi matrisi olusturur
        #boyut : (uretilecek_paket_sayisi, orijinal_parca sayisi)
        encoding_matris = GF.Random((num_encoded_packets, num_chunks))

        #kodlanmis paketleri uretir: sifreli paket = katsayilsar * veri
        encoded_payloads = encoding_matris @ data_matris

        return encoding_matris, encoded_payloads

    def rlnc_decode(self, received_coefficients, recived_payloads):
        """ 
        alinan katsayilar ve sifreli veriler uzerinden gauss eleme ile orijinal veriyi cozer
        """
        #matris rankini kontrol et
        mevcut_rank = np.linalg.matrix_rank(received_coefficients)
        beklenen_rank = received_coefficients.shape[1] #orijinal parca sayisi (sutun sayisi)

        #eger rank yetersizde hata firlat (alici yeni paket beklemeli)
        if mevcut_rank < beklenen_rank:
            raise ValueError(f"Yetersiz bagimsiz paket! Beklenen rank: {beklenen_rank}")
        
        #matrisin tersini al
        inverse_matris = np.linalg.inv(received_coefficients)
        
        #orijinal veriyi hesapla: veri = katsayilarin_tersi * sifreli_paket
        decoded_data = inverse_matris @ recived_payloads
    
        return decoded_data

# --- TEST SENARYOSU ---
if __name__ == "__main__":
    re = RlncEngine()
    # Orijinal Veri (Ornegin 4 parcaya bolunmuş 3'er bytelik bloklar)
    # Gercek sistemde bu matris, diske yazilan bir dosyanin bytelarindan beslenir.
    print("--- 1. ORİJİNAL VERİ (KAYNAK DÜĞÜM) ---")
    original_data = GF([[72, 101, 108],  # 'Hel'
                        [108, 111, 32],  # 'lo '
                        [80, 50, 80],    # 'P2P'
                        [33, 33, 33]])   # '!!!'
    print(original_data)
    
    # --- SIFRELEME ---
    print("\n--- 2. KODLAMA (ENCODING) ---")
    # Dosyamiz 4 parca. Churn (kopma) etkisine karsi aga 6 paket saliyoruz (Redundancy).
    coef_matrix, encoded_packets = re.rlnc_encode(original_data, num_encoded_packets=6)
    print("Üretilen Şifreli Paket Sayısı: 6")
    
    # --- AG TRANSFERİ SIMULASYONU (KAYiPLi AG) ---
    # Agdaki kopmalar yuzunden 2 paket yolda kayboldu diyelim.
    # Aliciya sadece 4 paket ulasti. (Herhangi 4 bagimsiz paket veriyi cozmek için yeterlidir).
    received_coefs = coef_matrix[:4]
    received_data = encoded_packets[:4]
    
    # --- COZUMLEME ---
    print("\n--- 3. ÇOZUMLEME (DECODING - HEDEF DUGUM) ---")
    try:
        decoded_result = re.rlnc_decode(received_coefs, received_data)
        print("cozülen veri:")
        print(decoded_result)
        
        if np.array_equal(original_data, decoded_result):
            print("\n BAŞARILI: Agdaki paket kayiplarina ragmen orijinal veri kayipsiz geri kazanildi!")
    except Exception as e:
        print("\nHATA: Yeterli bagimsiz paket toplanamadi veya matris tersinir değil.", e)