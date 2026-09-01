---
sidebar_position: 2
---

# noimg（純 Nolang 圖像處理工具庫）

notools 倉庫內含一個**純 Nolang 實現的圖像處理工具庫**（`noimg/` 目錄），類似 libvips 的設計思路，支持多格式讀寫與豐富的圖像操作。

## 支持的格式

| 格式 | 擴展名 | 讀取 | 寫入 | 說明 |
|------|--------|------|------|------|
| PPM/PGM/PNM | `.ppm` `.pgm` `.pnm` | ✅ | ✅ | Portable Pixmap/Graymap（ASCII 與 Binary） |
| BMP | `.bmp` | ✅ | ✅ | Windows Bitmap（僅 24/32 位未壓縮） |
| TGA | `.tga` | ✅ | ✅ | Targa（含 RLE 壓縮） |
| PAM | `.pam` | ✅ | ✅ | Portable Arbitrary Map |
| PNG | `.png` | ✅ | ✅ | Portable Network Graphics（8 位，zlib 壓縮，CRC32 校驗，5 種掃描線濾鏡，支持 Adam7 隔行解碼） |
| TIFF | `.tif` `.tiff` | ✅ | ✅ | Tagged Image File Format（僅未壓縮、8 位、單 strip） |
| GIF | `.gif` | ✅ | ✅ | Graphics Interchange Format（LZW 解碼+隔行+透明；動畫多幀提取+disposal 合成；寫入用 median-cut 量化） |
| JPEG | `.jpg` `.jpeg` | ✅ | ✅ | baseline JPEG 讀寫（DCT+Huffman 編碼/解碼+IDCT+YCbCr→RGB），不支持 progressive |
| WebP | `.webp` | ⚠️ | ⚠️ | VP8L lossless 解碼（Huffman+LZ77 距離+顏色快取+predictor 逆變換(14 模式)+顏色變換逆變換(定點乘)+subtract-green+顏色索引）；不支持 lossy VP8；寫入為 VP8L 容器（真實像素跨碼），但 **save 不寫 transform 頭（無 predictor/subtract-green/color-transform），與標準 WebP 解碼器不互通**——僅 noimg save→noimg load 可 round-trip |

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
| `bmp` | BMP 讀寫（24/32 位未壓縮） |
| `tga` | TGA 讀寫（含 RLE） |
| `pam` | PAM 讀寫 |
| `gif` | GIF 讀寫（LZW 解碼+隔行+透明+動畫多幀+disposal+median-cut 量化+動畫寫出） |
| `png` | PNG 讀寫（zlib 壓縮、CRC32 校驗、5 種濾鏡、Adam7 隔行解碼，僅 8 位） |
| `tiff` | TIFF 讀寫（僅未壓縮、8 位、單 strip） |
| `jpeg` | JPEG 讀寫（baseline DCT+Huffman 跨碼/解碼+IDCT+YCbCr→RGB，不支持 progressive） |
| `webp` | WebP VP8L lossless 解碼 |
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
│   ├── webp.no          ; WebP VP8L lossless 解碼
│   ├── colour.no        ; 色彩空間轉換
│   ├── resize.no        ; 縮放
│   ├── rotate.no        ; 旋轉與翻轉
│   ├── composite.no     ; 合成與裁剪
│   ├── filter.no        ; 濾鏡
│   ├── histogram.no     ; 直方圖與統計
│   └── text.no          ; 文字渲染與水印
├── tests/
│   ├── test-core.no       ; 核心圖像操作測試
│   ├── test-pnm.no        ; PNM 格式往返測試
│   ├── test-colour.no     ; 色彩空間轉換測試
│   ├── test-filter.no     ; 濾鏡操作測試
│   ├── test-composite.no  ; 合成操作測試
│   ├── test-histogram.no  ; 直方圖操作測試
│   └── test-resize-rotate.no ; 縮放與旋轉測試
└── package.jsonc        ; 項目配置
```
