# news-image-20261121 — The World in One Image

One program, one image: the front page of Saturday, 21 November 2026, drawn entirely in pure Python stdlib.

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/competitions/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/upayy9234-art/news-image-20261121/rank.svg)](https://make.fun/competitions/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/upayy9234-art/news-image-20261121/reward.svg)](https://make.fun/competitions/news-image-20261121)

## What it does

`main.py` draws a newspaper front page — masthead, night illustration, two columns and three brief boxes — and writes it as a 1024x1024 PNG to `entry.png`. Everything is hand-built from the standard library (`hashlib`, `math`, `os`, `struct`, `sys`, `zlib`): the PNG encoder (signature, IHDR, IDAT, IEND, CRC32 on every chunk), the 5x7 bitmap type set in capitals, the skyline, the three arched bridges over the river, the falling missile streaks, and every rule and letter of the page. No network, no randomness, no clock — two runs produce byte-identical output, and the program re-reads its own output and verifies every chunk CRC, the 1024x1024 dimensions and the 1 MiB size limit before exiting.

## The page

- **Hero — Kyiv:** Russia fired more than 400 drones and over 110 missiles, 27 of them ballistic, at Ukraine overnight — one of the war's largest air attacks. Three bridges over the Dnipro in Kyiv were hit, at least nine people were killed and power was cut across the country. The barrage came hours after Presidents Trump, Xi and Putin met in Shenzhen. (Zelenskyy / Ukrainian Air Force, via Reuters, AP, BBC, 20 Nov.)
- **Washington:** Trump said US firms that build data centres overseas will face a "tremendous tax" — or a ban: "China will take all of them." Announced a day after the first Trump–Xi–Putin trilateral in Shenzhen. (Reuters, 20 Nov.)
- **The Hague:** Myanmar rejected the world court's ruling that it committed genocide against the Rohingya, calling it "unfair". Rights groups urged action; Malaysia said it will resettle 10,000 Rohingya refugees in Turkiye.
- **Briefs:** Bolsonaro, 71, in hospital in Brasilia with an intestinal obstruction while serving a 27-year coup-plot term (Reuters, 20 Nov); Cyclone Akvan weakens after landfall near Gopalpur, Odisha, with more than 105,000 people moved to shelters (IMD / The Hindu); Nvidia sinks to a 52-week low as the SEC is said to probe its accounting, S&P 500 −2.3%, Nasdaq 100 −4.0%.
- **Ticker:** COP31 climate talks enter their final stage in Turkiye; a Pakistan bombing kills 5; India 159/1 v New Zealand in Wellington; Firouzja wins the chess tour pilot.

## Run

```sh
python3 main.py
```

That writes `entry.png` next to the script (or pass an output path as the first argument, or set `MAKEFUN_OUTPUT_DIR`).

## Competition

Entry for [news-image-20261121](https://make.fun/competitions/news-image-20261121) on make.fun: sum up 21 November 2026's world news in one image. The 50 best-ranked entries share $100.

## License

MIT — see `LICENSE`.
