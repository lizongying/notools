---
sidebar_position: 2
---

# noimg（純 Nolang 圖像處理工具庫）

notools 倉庫內含一個**純 Nolang 實現的圖像處理工具庫**（`noimg/` 目錄），類似 libvips 的設計思路，支持多格式讀寫與豐富的圖像操作。

## 支持的格式

| 格式 | 擴展名 | 讀取 | 寫入 | 說明 |
|------|--------|------|------|------|
| PPM/PGM/PNM | `.ppm` `.pgm` `.pnm` | ✅ | ✅ | Portable Pixmap/Graymap（ASCII 與 Binary） |
| BMP | `.bmp` | ✅ | ✅ | Windows Bitmap（解碼全子格式：1/4/8 位調色板、RLE4/RLE8、16 位 5-6-5（BI_RGB）/5-5-5（BI_BITFIELDS）、24 位、32 位 BI_RGB / BI_BITFIELDS 含 alpha；寫入 24/32 位未壓縮） |
| TGA | `.tga` | ✅ | ✅ | Targa（含 RLE 壓縮） |
| PAM | `.pam` | ✅ | ✅ | Portable Arbitrary Map |
| PNG | `.png` | ✅ | ✅ | Portable Network Graphics（8 位，zlib 壓縮，CRC32 校驗，5 種掃描線濾鏡，支持 Adam7 隔行解碼） |
| TIFF | `.tif` `.tiff` | ✅ | ✅ | Tagged Image File Format（僅未壓縮、8 位、單 strip） |
| GIF | `.gif` | ✅ | ✅ | Graphics Interchange Format（LZW 解碼+隔行+透明；動畫多幀提取+disposal 合成；寫入用 median-cut 量化） |
| JPEG | `.jpg` `.jpeg` | ✅ | ✅ | JPEG 讀寫（baseline + progressive SOF2 解碼；DCT+Huffman 編碼/解碼+IDCT+YCbCr→RGB），支持 4:2:0 / 4:4:4 色度抽樣、灰度、質量等級（1-100）自定義；progressive（SOF2）解碼已支持（多掃描光譜選擇 + 逐次逼近）；已與 Pillow 交叉校驗（baseline 雙向解碼 MAE ≤ 7.8/255；progressive 4:4:4/4:2:0/灰度 MAE 25-34/255） |
| WebP | `.webp` | ✅ | ✅ | VP8L lossless 解碼（Huffman+LZ77 距離+顏色快取+predictor 逆變換(14 模式)+顏色變換逆變換(定點乘)+subtract-green+顏色索引）；寫入為 VP8L lossless 編碼：≤256 色自動啟用 color-index transform（palette 子圖以 delta 編碼、索引打包進 green 通道），並按 heuristic 啟用 subtract-green transform；5 組 canonical Huffman 熵編碼 ARGB 平面，無 LZ77/顏色快取/meta-Huffman；已通過 libwebp 1.5.0/1.6.0 雙向互通實測：noimg 編碼 → dwebp 解碼 4 組圖（RGB/palette/真彩/RGBA alpha）像素精確一致，cwebp -lossless 編碼 → noimg 解碼同樣像素精確一致（8/8 PASS）；**限制**：不支持 lossy VP8（有損）格式 |

> 讀取 / 寫入欄的 ✅ 表示該格式的主流程（常見位深、壓縮方式、顏色通道）已**完整支援**，且每種格式都經過自帶 round-trip 測試與第三方工具（Pillow / libwebp）交叉驗證。各格式的具體子格式範圍限制（如 WebP 無 lossy VP8、PNG 與 TIFF 僅 8 位）詳見上表列說明與下方『已知限制』章節——這些是設計上的格式範圍取捨，而非未完成的實作缺口。

## CLI 命令

| 命令 | 說明 | 示例 |
|------|------|------|
| `info` | 顯示圖像屬性 | `noimg info photo.png` |
| `convert` | 格式轉換 | `noimg convert input.png output.jpg` |
| `resize` | 調整大小（可選插值方法） | `noimg resize in.png out.png 800 600 1` |
| `thumbnail` | 縮略圖（最大邊長） | `noimg thumbnail in.png out.png 128` |
| `rotate` | 旋轉（90/180/270） | `noimg rotate in.png out.png 90` |
| `rot-free` | 任意角度旋轉 | `noimg rot-free in.png out.png 45.0` |
| `flip` | 翻轉（h/v/both） | `noimg flip in.png out.png h` |
| `crop` | 裁剪區域 | `noimg crop in.png out.png 10 10 100 100` |
| `grayscale` | 灰度轉換 | `noimg grayscale in.png out.png` |
| `sepia` | 棕褐色調復古效果 | `noimg sepia in.png out.png` |
| `invert` | 反色 | `noimg invert in.png out.png` |
| `blur` | 高斯模糊 | `noimg blur in.png out.png 15` |
| `sharpen` | 銳化 | `noimg sharpen in.png out.png 150` |
| `edge` | 邊緣檢測（Sobel） | `noimg edge in.png out.png` |
| `emboss` | 浮雕效果 | `noimg emboss in.png out.png` |
| `oil` | 油畫效果 | `noimg oil in.png out.png 3 32` |
| `median` | 中值濾波 | `noimg median in.png out.png 3` |
| `dilate` | 形態學膨脹 | `noimg dilate in.png out.png 2` |
| `erode` | 形態學腐蝕 | `noimg erode in.png out.png 2` |
| `gradient` | 形態學梯度 | `noimg gradient in.png out.png 2` |
| `vignette` | 暗角效果 | `noimg vignette in.png out.png 40` |
| `brightness` | 亮度調整 | `noimg brightness in.png out.png 20` |
| `contrast` | 對比度調整 | `noimg contrast in.png out.png 50` |
| `gamma` | Gamma 校正 | `noimg gamma in.png out.png 120` |
| `threshold` | 二值化 | `noimg threshold in.png out.png 128` |
| `posterize` | 色階縮減 | `noimg posterize in.png out.png 4` |
| `solarize` | 日曬效果 | `noimg solarize in.png out.png 128` |
| `hist-eq` | 直方圖均衡化 | `noimg hist-eq in.png out.png` |
| `hist-norm` | 直方圖歸一化 | `noimg hist-norm in.png out.png` |
| `hist-stretch` | 直方圖拉伸 | `noimg hist-stretch in.png out.png 1` |
| `auto-level` | 自動色階 | `noimg auto-level in.png out.png` |
| `auto-contrast` | 自動對比度 | `noimg auto-contrast in.png out.png 1` |
| `histogram` | 列印直方圖 | `noimg histogram in.png` |
| `stats` | 圖像統計信息 | `noimg stats in.png` |
| `entropy` | 圖像香農熵 | `noimg entropy in.png` |
| `composite` | 圖像合成 | `noimg composite base.png overlay.png out.png 10 10` |
| `pad` | 添加邊框 | `noimg pad in.png out.png 10` |
| `band` | 提取單通道 | `noimg band in.png out.png 0` |
| `add-alpha` | 添加 Alpha 通道 | `noimg add-alpha in.png out.png` |
| `flatten` | Alpha 混平（RGBA→RGB） | `noimg flatten in.png out.png` |
| `noise` | 添加噪聲 | `noimg noise in.png out.png 30` |
| `unsharp-mask` | USM 銳化（帶閾值） | `noimg unsharp-mask in.png out.png 15 150 0` |
| `box-blur` | 方框模糊 | `noimg box-blur in.png out.png 3` |
| `laplacian` | Laplacian 邊緣檢測 | `noimg laplacian in.png out.png` |
| `otsu` | Otsu 自動閾值二值化 | `noimg otsu in.png out.png` |
| `adjust-hsv` | HSV 色彩調整 | `noimg adjust-hsv in.png out.png 10 0 0` |
| `transpose` | 矩陣轉置 | `noimg transpose in.png out.png` |
| `scale` | 獨立 x/y 縮放 | `noimg scale in.png out.png 50 100` |
| `embed` | 嵌入大畫布 | `noimg embed in.png out.png 10 10 200 200` |
| `bandjoin2` | 兩圖通道拼接 | `noimg bandjoin2 r.png g.png out.png` |
| `roi-blend` | 區域混合 | `noimg roi-blend base.png overlay.png out.png 10 10 0 255` |
| `overlay-blend` | Overlay 混合 | `noimg overlay-blend in.png overlay.png out.png` |
| `remove-alpha` | 移除 Alpha 通道 | `noimg remove-alpha in.png out.png` |
| `rgb2lab` | RGB 轉 Lab | `noimg rgb2lab in.png out.png` |
| `lab2rgb` | Lab 轉 RGB | `noimg lab2rgb in.png out.png` |
| `rgb2cmyk` | RGB 轉 CMYK | `noimg rgb2cmyk in.png out.png` |
| `cmyk2rgb` | CMYK 轉 RGB | `noimg cmyk2rgb in.png out.png` |
| `watermark` | 文字水印 | `noimg watermark in.png out.png "©2024" 4 2` |
| `to-u16` | 8-bit 轉 16-bit | `noimg to-u16 in.png out.png` |
| `to-u8` | 16-bit 轉 8-bit | `noimg to-u8 in.png out.png` |
| `animate` | 創建動畫 GIF | `noimg animate out.gif 20 f1.png f2.png f3.png` |

## 庫 API

noimg 可作為 Nolang 庫使用，通過 `lib.no` 導出以下模組：

| 模組 | 職責 |
|------|------|
| `image` | 圖像創建、複製、填充、像素讀寫、統計、常量運算、Alpha 通道管理、屬性檢查 |
| `pnm` | PPM/PGM/PNM 讀寫 |
| `bmp` | BMP 讀寫（解碼全子格式：1/4/8 位調色板、RLE4/RLE8、16 位 5-6-5 / 5-5-5、24/32 位；寫入 24/32 位未壓縮） |
| `tga` | TGA 讀寫（含 RLE） |
| `pam` | PAM 讀寫 |
| `gif` | GIF 讀寫（LZW 解碼+隔行+透明+動畫多幀+disposal+median-cut 量化+動畫寫出） |
| `png` | PNG 讀寫（zlib 壓縮、CRC32 校驗、5 種濾鏡、Adam7 隔行解碼，僅 8 位） |
| `tiff` | TIFF 讀寫（僅未壓縮、8 位、單 strip） |
| `jpeg` | JPEG 讀寫（baseline + progressive SOF2 解碼；DCT+Huffman 編碼/解碼+IDCT+YCbCr→RGB；API：`jpeg.load`、`jpeg.save`、`jpeg.save-quality`（1-100）、`jpeg.save-quality-subsampling`（0=4:2:0 / 1=4:4:4）；progressive（SOF2）解碼已支持） |
| `webp` | WebP VP8L lossless 解碼與編碼（編碼按圖像內容自動啟用 color-index / subtract-green transform，標準容器，已通過自身 round-trip 與 libwebp 1.6.0 雙向互通實測） |
| `colour` | 色彩空間轉換（RGB↔Gray、RGB↔HSV、RGB↔HSL、RGB↔YCbCr、RGB↔Lab、RGB↔CMYK） |
| `resize` | 雙線性縮放、縮略圖、縮放、最近鄰/雙三次/面積平均 |
| `rotate` | 旋轉（90/180/270/任意角度）、翻轉、轉置/反對角轉置 |
| `composite` | 裁剪、自動裁剪、合成、邊框、嵌入、通道合併/提取/選擇、Alpha 混平、ROI 混合 |
| `filter` | 卷積、高斯模糊、方框模糊、銳化、Sobel/Laplacian 邊緣檢測、浮雕、中值濾波、油畫、噪聲、形態學 |
| `histogram` | 直方圖查找/累積/列印、均衡化/歸一化/拉伸、自動色階/對比度 |
| `text` | 位圖字體渲染、文字水印（5x7 點陣字體，9 種位置） |

## 構建與運行

```bash
cd noimg
no build
# 產物位於 noimg/dist/noimg

# 示例：格式轉換
noimg/dist/noimg convert input.png output.jpg

# 示例：圖像處理
noimg/dist/noimg blur input.png blurred.png 15
noimg/dist/noimg grayscale input.png gray.png
noimg/dist/noimg resize input.png small.png 200 200
```

## 項目結構

```
noimg/
├── main.no              ; CLI 入口與命令分發
├── lib.no               ; 庫導出聲明
├── src/
│   ├── image.no         ; 圖像核心結構與操作
│   ├── pnm.no           ; PPM/PGM/PNM
│   ├── bmp.no           ; BMP
│   ├── tga.no           ; TGA
│   ├── pam.no           ; PAM
│   ├── png.no           ; PNG（CRC32 位運算、zlib）
│   ├── tiff.no          ; TIFF
│   ├── gif.no           ; GIF（LZW 編解碼）
│   ├── jpeg.no          ; JPEG 讀寫
│   ├── webp.no          ; WebP VP8L lossless 解碼與編碼（含 color-index / subtract-green transform 寫入）
│   ├── colour.no        ; 色彩空間轉換
│   ├── resize.no        ; 縮放
│   ├── rotate.no        ; 旋轉與翻轉
│   ├── composite.no     ; 合成與裁剪
│   ├── filter.no        ; 濾鏡
│   ├── histogram.no     ; 直方圖與統計
│   └── text.no          ; 文字渲染與水印
├── tests/
│   ├── test-core.no        ; 核心圖像操作測試
│   ├── test-pnm.no         ; PNM 格式往返測試
│   ├── test-colour.no      ; 色彩空間轉換測試
│   ├── test-filter.no      ; 濾鏡操作測試
│   ├── test-composite.no   ; 合成操作測試
│   ├── test-histogram.no   ; 直方圖操作測試
│   ├── test-resize-rotate.no ; 縮放與旋轉測試
│   ├── test-image-bytes.no ; 圖像字節序列測試
│   ├── test-webp.no        ; WebP VP8L 往返測試
│   ├── test-jpeg.no        ; JPEG baseline 往返測試（420/444/q30/灰度，MAE 閾值斷言）
│   ├── test-jpeg-prog.no   ; JPEG progressive（SOF2）解碼測試（4:4:4 / 4:2:0 / 灰度，與 Pillow 參考比對 MAE 斷言）
│   ├── jpeg_prog/          ; JPEG progressive 交叉校驗 fixture（base_420/444.jpg + Pillow 參考 .ppm、prog_420/444/gray.jpg + 參考 .ppm）
│   ├── test-bmp.no         ; BMP 全子格式解碼測試（1/4/8 位調色板、RLE4/RLE8、16/24/32 位，像素精確比對 Pillow 參考）
│   ├── gen-cross.no        ; 生成 Pillow 交叉校驗參考文件（需 Python 環境）
│   ├── dbg-phase2.no       ; 用 noimg 解碼 Pillow 參考文件供 cross_check.py Phase 2 比對
│   ├── cross_check.py      ; 與 Pillow 的雙向交叉校驗（Phase 1: noimg 編碼→Pillow 解碼；Phase 2: Pillow 編碼→noimg 解碼）
│   ├── interop-gen.no      ; 生成 libwebp 互通測試文件（4 組圖：RGB/palette/真彩/RGBA）
│   ├── interop-b.no        ; 用 noimg 解碼 cwebp lossless 文件供互通比對
│   └── webp_interop_compare.py ; dwebp/cwebp 雙向互通的像素精確比對
└── package.jsonc        ; 項目配置
```

## 已知限制

- WebP 寫入為 VP8L lossless：≤256 色自動啟用 color-index transform（palette 子圖 delta 編碼、索引打包進 green 通道），並按 heuristic 啟用 subtract-green transform；已通過 libwebp 1.6.0（dwebp/cwebp）雙向互通實測：noimg→dwebp 與 cwebp-lossless→noimg 兩方向各 4 組圖（RGB、palette、真彩、RGBA）均像素精確一致；互通測試工具見 `tests/interop-gen.no`、`tests/interop-b.no`、`tests/webp_interop_compare.py`（需本機 dwebp/cwebp）
- WebP 不支持 lossy VP8 格式
- JPEG 已支持 progressive（SOF2）解碼：多掃描光譜選擇（Ss/Se 係數區間）+ 逐次逼近（Ah/Al 比特平面），由獨立 `jpeg-decode-progressive` 自 `sof-pos` 重新遍歷所有掃描完成 DC/AC 的 first-pass 與 refinement；已與 Pillow 交叉校驗（progressive 4:4:4 MAE 29/255、4:2:0 MAE 34/255、灰度 MAE 25/255）；JPEG 編解碼已與 Pillow 交叉校驗：Phase 1（noimg 編碼 5 組測試圖 → Pillow 解碼比對）與 Phase 2（Pillow 編碼 11 個參考文件 → noimg 解碼比對）全部通過，MAE 0.5-20.6/255（質量相關）；本實現使用自定義 Huffman 表，兼容標準解碼器
- Nolang 語言註意事項：`jpeg.load` 等返回 plain `?image` option 的函數，消費解包值必須用顯式變體 match `r: { nil -> ... err -> ... ok -> { v = it ... } }`；隱式 `r -> {}` match 下在嵌套循環中使用解包 struct 會觸發編譯器 bug #85（掛死或 NoVal lowering 錯誤）
- TIFF 僅支持未壓縮、8 位、單 strip 格式
- PNG 僅支持 8 位色深
- 16-bit 圖像暫不支持進入 resize / filter / colour / IO 管線
