import pickle

class Packet:
    def __init__(self, file_id, generation_id, coefficients, payload, merkle_proof = None):
        """
        agda tasinacak standart p2p veri paketi

        :param file_id: Dosyanin benzersiz kimligi
        :param generation_id: Bu paketin hangi nesle ait oldugu bilgisi
        :param coefficients: RLNC kodlama katsayilari matrisi
        :param payload: Sifrelenmis veri blogu
        :param merkle_proof: Istege bagli Merkle dogrulama kaniti
        """

        self.file_id = file_id
        self.generation_id = generation_id
        self.coefficients = coefficients
        self.payload = payload
        self.merkle_proof = merkle_proof 
    
    def to_bytes(self):
        """
        Paketi agda gonderebilecek byte formatina cevirir (Serialization)
        """
        return pickle.dumps(self)
    
    @staticmethod
    def from_bytes(byte_data):
        """
        agdan gelen byte verisini tekrar Packet objesine donustutur (Deserialization)
        """

        return pickle.loads(byte_data)
    
    def __repr__(self):
        return f"<Packet | File: {self.file_id[:8]}... | Gen: {self.generation_id}| Payload Size: {len(self.payload)} bytes"
