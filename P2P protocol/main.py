import time
from node import Node
from network import NetworkLayer

if __name__ == "__main__":
    print("="*60)
    print("P2P gercek ag (UDP) testi")
    print("="*60)

    #1. alici (leecher) kurulumu

    leecher_node = Node("LEECHER_NODE")
    
    #leecher ag kartini kur
    #5001 portunu dinle paket gelirse leeceher_node beynine at

    leecher_net = NetworkLayer(
        node_id="LEECHER_NET",
        host="127.0.0.1",
        port=5001,
        on_packet_received_callback=leecher_node.receive_pack
    )
    leecher_net.start_listening()

    #2. gonderici (seeder) kur
    seeder_node = Node("SEEDER_NODE")

    #seeder sadece paket yollama yapar dinleme yapmasina gerek yok, callback bos gecilebilir
    seeder_net = NetworkLayer("SEEDER_NET","127.0.0.1",5000,lambda pkt:None)

    #gonderilecek sahte test dosyasi
    test_file = "real_network_test.txt"
    with open(test_file,"w") as f:
        f.write("bu veri, node beyninden cikip NetworkLayer uzerinden UDP ile ucmustur")

    #3. islem basliyor (parcala sifrele firlat)

    created_packets= seeder_node.share_file(test_file)

    print("\n[SISTEM] Paketler gercek ag uzerinden firlatiliyor...")

    for pkt in created_packets:
        #node'un urettigi paketi, network katman araciligiyla 5001 portuna (Leecher'a) at
        seeder_net.send_packet(packet = pkt, target_ip='127.0.0.1',target_port=5001)
        time.sleep(0.5) #paketin agda gittigini gormek icin yarim saniye gecikme
    
    #arka plandaki ag dinleme islemlerinin tamamlanmasi icin ana programi biraz ayakta tut
    time.sleep(3)
    print("\n[SISTEM] Test basariyla tamamlandi")