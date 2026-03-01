import os
import numpy as np
import galois

GF = galois.GF(2**8)

class FileHandler:
    def __init__(self, chunk_size=1024, gen_size = 4):
        self.chunk_size = chunk_size #her bir parcanin byte boyutu
        self.gen_size = gen_size     #bir nesildeki parca (blok) sayisi

    def file_to_generations(self, file_path):
        """
        dosya okunur, bytelarina ayrilir ve nesil matrislerine donusturulur
        """
        
        file_size = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            data = f.read()

        required_size = self.chunk_size * self.gen_size
        generations = []

        for i in range(0, len(data), required_size):
            gen_data = data[i:i + required_size]

            #padding: eger son nesil tam dolu olmadiysa, sonunu sifir (0x00) ile tamamlar
            if len(gen_data)<required_size:
                gen_data = gen_data.ljust(required_size, b'\x00')

            #veriyi (gen_size , chunk_size) boyutunda 8-bitlik matrise donusturur
            matrix = np.frombuffer(gen_data, dtype=np.uint8).reshape(self.gen_size, self.chunk_size)
            generations.append(GF(matrix))
        return generations, file_size
    def generations_to_file(self, generations, output_path, original_file_size): 
        """
        cozulen nesil matrisini birlestirip orijinal dosyayi diske yazar
        """
        with open(output_path, "wb") as f:
            written_bytes = 0
            for gen in generations:
                #GF matrisini byte dizisine geri cevirir
                gen_bytes = np.array(gen, dtype=np.uint8).tobytes()

                #orijinal dosya boyutunu asmamak icin padding'leri kirp
                if written_bytes + len(gen_bytes) > original_file_size:
                    gen_bytes = gen_bytes[:original_file_size - written_bytes]

                f.write(gen_bytes)
                written_bytes += len(gen_bytes)