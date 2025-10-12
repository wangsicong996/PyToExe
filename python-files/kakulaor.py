def hitung_tp_sl_xauusd_final():
    """
    Menghitung TP dan SL untuk XAU/USD berdasarkan pergerakan poin ($)
    dan menampilkannya dalam format ratusan pips.
    """
    # Profil trade dalam satuan POIN (pergerakan dolar)
    RISIKO_POIN = 45.0
    PROFIT_POIN = 48.0
    RR_RASIO = PROFIT_POIN / RISIKO_POIN

    # Perulangan utama agar program tidak langsung keluar
    while True:
        try:
            # 1. Menerima input dari pengguna
            print("--- Kalkulator TP/SL XAUUSD ---")
            harga_masuk_str = input("➡️ Masukkan Harga Masuk (atau ketik 'keluar' untuk berhenti): ")
            
            # Opsi untuk keluar di awal
            if harga_masuk_str.lower() == 'keluar':
                break

            harga_masuk = float(harga_masuk_str)
            arah_trade = input("➡️ Pilih Arah Trade (ketik 'buy' atau 'sell'): ").lower()

            # 2. Menghitung harga TP dan SL
            if arah_trade == 'buy':
                harga_sl = harga_masuk - RISIKO_POIN
                harga_tp = harga_masuk + PROFIT_POIN
            elif arah_trade == 'sell':
                harga_sl = harga_masuk + RISIKO_POIN
                harga_tp = harga_masuk - PROFIT_POIN
            else:
                print("\n❌ Arah trade tidak valid. Harap masukkan 'buy' atau 'sell'.\n")
                continue # Kembali ke awal loop

            # 3. Menampilkan hasil
            print("\n" + "="*40)
            print("✅ HASIL PERHITUNGAN (XAU/USD)")
            print("="*40)
            print(f"Arah Trade: {arah_trade.upper()}")
            print(f"Harga Masuk: {harga_masuk:.2f}")
            print("-" * 40)
            print(f"🔴 Stop Loss (SL): {harga_sl:.2f}")
            print(f"   (Risiko: {RISIKO_POIN * 10:.1f} Pips)")
            print(f"🟢 Take Profit (TP): {harga_tp:.2f}")
            print(f"   (Reward: {PROFIT_POIN * 10:.1f} Pips)")
            print("-" * 40)
            print(f"Risk/Reward Ratio (RR) Tetap: 1:{RR_RASIO:.2f}")
            print("="*40)

        except ValueError:
            print("\n❌ Input tidak valid. Pastikan Anda memasukkan angka yang benar untuk harga.\n")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

        # --- BAGIAN BARU: Aksi setelah hasil ---
        print("\n" + "="*25)
        aksi = input("Tekan ENTER untuk hitung ulang, atau ketik 'keluar' untuk menutup: ").lower()
        if aksi == 'keluar':
            break # Keluar dari loop dan menutup program
        print("\n") # Memberi spasi sebelum perhitungan baru

# Menjalankan fungsi kalkulator
if __name__ == "__main__":
    hitung_tp_sl_xauusd_final()