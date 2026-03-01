import os
from file_handler import FileHandler
from rlnc_engine import rlnc_encode, rlnc_decode

def test_file_coding():
    # 1. test icin gecici bir dosya olusturur 
    test_file = "test_input.txt"
    output_file = "test_output.txt"

    with open(test_file, "w", encoding="utf-8") as f:
        #dosya boyutunu buyutmek icin metin tekrarlanir
        f.write("Bu, RLNC motorunu ve dosya isleyicisini test etmek icin olusturulmus bir metin belgesidir. " * 50)

    print("--- 1. DOSYA BOLUMLEME ---")
    print(f"Orijinal dosya boyutu: {os.path.getsize(test_file)} byte")

    # chunk_size=16 byte, gen_size=4 parca (Her nesil 64 byte isleyecek)
    fh = FileHandler(chunk_size=16, gen_size=4)
    generations, original_size = fh.file_to_generations(test_file)
    print(f"Toplam {len(generations)} nesil olusturuldu.")

    decoded_generations = []

    print("\n--- 2. KODLAMA VE ÇOZME SIMULASYONU ---")
    for i, gen_matrix in enumerate(generations):
        # kodlama: 4 orijinal parcadan 6 sifreli paket uret (Yedeklilik)
        coef_matrix, encoded_payloads = rlnc_encode(gen_matrix, num_encoded_packets=6)

        # ag kaybı (Churn) simulasyonu: 2 paket yolda kaybolsun, sadece 4 paket ulassin
        received_coefs = coef_matrix[:4]
        received_payloads = encoded_payloads[:4]

        # cozumleme: Ulaşan 4 bağımsız paket ile matrisi geri elde et
        decoded_gen = rlnc_decode(received_coefs, received_payloads)
        decoded_generations.append(decoded_gen)

    print("Tum nesiller başariyla kodlandi ve ag kayiplarina ragmen cozuldu.")

    print("\n--- 3. DOSYAYI YENİDEN OLUSTURMA ---")
    fh.generations_to_file(decoded_generations, output_file, original_size)
    print(f"cözülen dosya boyutu: {os.path.getsize(output_file)} byte")

    # 4. Sonuç Doğrulama
    with open(test_file, "rb") as f1, open(output_file, "rb") as f2:
        if f1.read() == f2.read():
            print("\nBASARILI: Orijinal dosya ile kodlanip cozulen dosya byte byte birebir ayni!")
        else:
            print("\nHATA: Dosya butunlugu bozuldu, icerikler eslesmiyor.")

if __name__ == "__main__":
    test_file_coding()