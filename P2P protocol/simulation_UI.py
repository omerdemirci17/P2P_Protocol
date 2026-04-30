import tkinter as tk
from tkinter import scrolledtext
import sys
from node import Node

class TextRedirector:
    """ Konsol Ciktilarini tkinter metin kutusuna gonderecek yardimci sinif"""
    def __init__(self, test_widget):
        self.text_widget = test_widget
    
    def write(self, string):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END,string)
        self.text_widget.see(tk.END) #otomatik  olarak asagi kaydirma
        self.text_widget.update()
        self.text_widget.config(state=tk.DISABLED)

    def flush(self):
        pass

class P2PSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P RLNC AG SIMULASYONU")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")

        #baslik
        title = tk.Label(root, text = "RLNC P2P Dugum Simulasyonu", font=("Arial,16,bold"), bg="#1e1e1e", fg ="white")
        title.pack(pady=10)

        #Butonlar cercevesi
        btn_frame = tk.Frame(root,bg="#1e1e1e")
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text= "Dosyayi parcala ve aga sal", font="Arial,12",bg="#4caf50",fg= "white", command=self.start_simulation )
        self.start_btn.pack(side=tk.LEFT,padx=10)
        
        #konsol ciktisi ekrani
        self.console = scrolledtext.ScrolledText(root,wrap = tk.WORD, width = 90, height = 25, bg = "#2d2d2d",fg ="#00ff00")
        self.console.pack(padx = 20,pady = 10)

        #print komutlarini bu ekrana yonlendir
        sys.stdout = TextRedirector(self.console)
        sys.stderr = TextRedirector(self.console) #hatalari yazdir
        
        #dugumleri olustur
        self.seeder = Node("SEEDER_1")
        self.leecher = Node("LEECHER_2")
        self.packets_in_network = []
    
    def start_simulation(self):
        #buton calisiyor mu test
        sys.__stdout__.write("\n[!!!] BUTON ALGILANDI: SİMÜLASYON TETİKLENDİ!\n")
        self.start_btn.config(state=tk.DISABLED)
        print("="*60)
        print("[SISTEM] Simulasyon Baslatiliyor")

        #test icin gecici dosya olusturma
        test_file = "gui_test_file.txt"
        with open(test_file,"w") as f:
            f.write("bu metin P2P aginda paketlere ayrilip ucan bir veridir")

        #seeder dosyayi parcalar, kodlar ve paketleri uretir
        self.packets_in_network = self.seeder.share_file(test_file)

        print("\n[AG] Paketler yola cikti. Leecher'a ulasti")

        #agi simule etmek icin paketleri yarim saniye arayla Leecher'a gonderiyoruz
        self.send_packet_with_delay(0)

    def send_packet_with_delay(self,index):
        """Agdaki gecikmeyi (ping/latency) gorsellestirmek icin pakeytleri sirayla yollar"""
        if index <len(self.packets_in_network):
            pkt = self.packets_in_network[index]
            print(f"---> [AG] Paket {index+1} Leecher'e ulasti.")

            #Leecher paketi karsilar
            self.leecher.receive_pack(pkt)
            
            #tkinter'i dondurmak icin 'after' kullanarak 600ms sonra diger paketi yolla
            self.root.after(600,self.send_packet_with_delay,index+1)
        else:
            print("[SISTEM] Simulasyon Tamamlandi.")
            self.start_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = P2PSimulatorGUI(root)

    #kapanirken printi eski haline getir (guvenlik icin)
    def on_closing():
        sys.stdout = sys.__stdout__
        root.destroy()

    root.protocol("WM_DELETE_WINDOW",on_closing)
    root.mainloop()