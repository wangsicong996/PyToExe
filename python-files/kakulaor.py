def hitung_tp_sl_xauusd_final():
    """
    Menghitung TP dan SL untuk XAU/USD berdasarkan pergerakan poin ($)
    dan menampilkannya dalam format ratusan pips.
    - Risiko: 45 poin ($45) = 450 pips
    - Reward: 48 poin ($48) = 480 pips
    """
    # Profil trade dalam satuan POIN (pergerakan dolar)
    RISIKO_POIN = 45.0
    PROFIT_POIN = 48.0
    RR_RASIO = PROFIT_POIN / RISIKO_POIN

    try:
        # 1. Menerima input dari pengguna
        harga_masuk = float(input("➡️ Masukkan Harga Masuk XAU/USD: "))
        arah_trade = input("➡️ Pilih Arah Trade (ketik 'buy' atau 'sell'): ").lower()

        # 2. Menghitung harga TP dan SL secara langsung dari poin
        if arah_trade == 'buy':
            harga_sl = harga_masuk - RISIKO_POIN
            harga_tp = harga_masuk + PROFIT_POIN
        elif arah_trade == 'sell':
            harga_sl = harga_masuk + RISIKO_POIN
            harga_tp = harga_masuk - PROFIT_POIN
        else:
            print("❌ Arah trade tidak valid. Harap masukkan 'buy' atau 'sell'.")
            return

        # 3. Menampilkan hasil dengan format pips dikali 10
        print("\n" + "="*40)
        print("✅ HASIL PERHITUNGAN (XAU/USD)")
        print("="*40)
        print(f"Arah Trade: {arah_trade.upper()}")
        print(f"Harga Masuk: {harga_masuk:.2f}")
        print("-" * 40)
        print(f"🔴 Stop Loss (SL): {harga_sl:.2f}")
        # Tampilkan pips dengan dikali 10
        print(f"   (Risiko: {RISIKO_POIN * 10:.1f} Pips)")
        print(f"🟢 Take Profit (TP): {harga_tp:.2f}")
        # Tampilkan pips dengan dikali 10
        print(f"   (Reward: {PROFIT_POIN * 10:.1f} Pips)")
        print("-" * 40)
        print(f"Risk/Reward Ratio (RR) Tetap: 1:{RR_RASIO:.2f}")
        print("="*40)

    except ValueError:
        print("❌ Input tidak valid. Pastikan Anda memasukkan angka untuk harga.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

# Menjalankan fungsi kalkulator
if __name__ == "__main__":
    hitung_tp_sl_xauusd_final()