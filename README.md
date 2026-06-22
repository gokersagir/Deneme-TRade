# Deneme Trade

BIST 100 hisseleri için günlük teknik tarama raporu üreten Python uygulaması.

> Not: Kıvanç Özbilgiç'in TradingView indikatörleri bire bir kopyalanmamıştır. Bu proje, lisanslı/izinli Pine Script kuralları sağlandığında genişletilebilecek özgün ve denetlenebilir OTT/Supertrend benzeri tarama mantığı içerir.

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Kullanım

İnternetten günlük veri indirerek rapor üretmek:

```bash
trade-scan --symbols-file data/bist100_symbols.txt --output reports/bist100_daily.md
```

CSV verisiyle internetsiz çalıştırmak:

```bash
trade-scan --csv-dir path/to/ohlc-csv --symbols-file data/bist100_symbols.txt
```

CSV dosyalarında `Date,Open,High,Low,Close` kolonları bulunmalıdır.

## Günlük çalıştırma

Linux cron örneği:

```cron
30 18 * * 1-5 cd /workspace/Deneme-TRade && . .venv/bin/activate && trade-scan --output reports/bist100_daily.md
```

## Çıktı

Rapor `Hisse`, `Sinyal`, `Kapanış`, `Alım yeri`, `Satım yeri`, `Stop` ve not kolonlarını içeren Markdown tablo üretir.
