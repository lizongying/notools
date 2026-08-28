# noimg

纯 [Nolang](https://github.com/lizongying/nolang) 实现的图像处理工具库，类似 libvips 的设计思路，支持多格式读写与丰富的图像操作。

## 特性

- 纯 Nolang 实现，不依赖任何外部图像处理库
- 支持 9 种图像格式读写
- 55+ 种图像操作命令（滤镜、色彩变换、几何变换、合成等）
- 可作为 Nolang 库使用（通过 `lib.no` 导出）
- 支持 8-bit 和 16-bit 图像

## 安装

### 方式一：从 Releases 下载预编译二进制

```bash
# Linux amd64 示例
curl -fsSL -o noimg https://github.com/lizongying/notools/releases/latest/download/noimg-linux-amd64
chmod +x noimg && sudo mv noimg /usr/local/bin/
```

### 方式二：从源码构建

```bash
cd noimg
no build
# 产物位于 noimg/dist/noimg
```

## 支持的格式

| 格式 | 扩展名 | 读取 | 写入 | 说明 |
|------|--------|------|------|------|
| PPM/PGM/PNM | `.ppm` `.pgm` `.pnm` | ✅ | ✅ | Portable Pixmap/Graymap（ASCII 与 Binary） |
| BMP | `.bmp` | ✅ | ✅ | Windows Bitmap（仅 24/32 位未压缩） |
| TGA | `.tga` | ✅ | ✅ | Targa（含 RLE 压缩） |
| PAM | `.pam` | ✅ | ✅ | Portable Arbitrary Map |
| PNG | `.png` | ✅ | ✅ | Portable Network Graphics（8 位，zlib 压缩，CRC32 校验，5 种扫描线滤镜，支持 Adam7 隔行解码） |
| TIFF | `.tif` `.tiff` | ✅ | ✅ | Tagged Image File Format（仅未压缩、8 位、单 strip） |
| GIF | `.gif` | ✅ | ✅ | Graphics Interchange Format（LZW 解码+隔行+透明；动画多帧提取+disposal 合成；写入用 median-cut 量化） |
| JPEG | `.jpg` `.jpeg` | ✅ | ✅ | baseline JPEG 读写（DCT+Huffman 编码/解码+IDCT+YCbCr→RGB），不支持 progressive |
| WebP | `.webp` | ⚠️ | ⚠️ | VP8L lossless 解码（Huffman+LZ77 距离+颜色缓存+predictor 逆变换(14 模式)+颜色变换逆变换(定点乘)+subtract-green+颜色索引）；不支持 lossy VP8；写入为 VP8L 容器（真实像素编码），但 save 不写 transform 头（无 predictor/subtract-green/color-transform），与标准 WebP 解码器不互通——仅 noimg save→noimg load 可 round-trip |

## CLI 命令

### 图像信息与格式转换

| 命令 | 说明 | 示例 |
|------|------|------|
| `info` | 显示图像属性 | `noimg info photo.png` |
| `convert` | 格式转换 | `noimg convert input.png output.jpg` |
| `stats` | 图像统计信息 | `noimg stats in.png` |
| `entropy` | 图像香农熵 | `noimg entropy in.png` |
| `histogram` | 打印直方图 | `noimg histogram in.png` |

### 几何变换

| 命令 | 说明 | 示例 |
|------|------|------|
| `resize` | 调整大小（可选插值方法） | `noimg resize in.png out.png 800 600 1` |
| `thumbnail` | 缩略图（最大边长） | `noimg thumbnail in.png out.png 128` |
| `scale` | 独立 x/y 缩放 | `noimg scale in.png out.png 50 100` |
| `rotate` | 旋转（90/180/270） | `noimg rotate in.png out.png 90` |
| `rot-free` | 任意角度旋转 | `noimg rot-free in.png out.png 45.0` |
| `flip` | 翻转（h/v/both） | `noimg flip in.png out.png h` |
| `transpose` | 矩阵转置 | `noimg transpose in.png out.png` |
| `crop` | 裁剪区域 | `noimg crop in.png out.png 10 10 100 100` |
| `embed` | 嵌入大画布 | `noimg embed in.png out.png 10 10 200 200` |
| `pad` | 添加边框 | `noimg pad in.png out.png 10` |

### 色彩调整

| 命令 | 说明 | 示例 |
|------|------|------|
| `grayscale` | 灰度转换 | `noimg grayscale in.png out.png` |
| `sepia` | 棕褐色调复古效果 | `noimg sepia in.png out.png` |
| `invert` | 反色 | `noimg invert in.png out.png` |
| `brightness` | 亮度调整 | `noimg brightness in.png out.png 20` |
| `contrast` | 对比度调整 | `noimg contrast in.png out.png 50` |
| `gamma` | Gamma 校正 | `noimg gamma in.png out.png 120` |
| `threshold` | 二值化 | `noimg threshold in.png out.png 128` |
| `posterize` | 色阶缩减 | `noimg posterize in.png out.png 4` |
| `solarize` | 日晒效果 | `noimg solarize in.png out.png 128` |
| `adjust-hsv` | HSV 色彩调整 | `noimg adjust-hsv in.png out.png 10 0 0` |
| `otsu` | Otsu 自动阈值二值化 | `noimg otsu in.png out.png` |

### 直方图操作

| 命令 | 说明 | 示例 |
|------|------|------|
| `hist-eq` | 直方图均衡化 | `noimg hist-eq in.png out.png` |
| `hist-norm` | 直方图归一化 | `noimg hist-norm in.png out.png` |
| `hist-stretch` | 直方图拉伸 | `noimg hist-stretch in.png out.png 1` |
| `auto-level` | 自动色阶 | `noimg auto-level in.png out.png` |
| `auto-contrast` | 自动对比度 | `noimg auto-contrast in.png out.png 1` |

### 滤镜与效果

| 命令 | 说明 | 示例 |
|------|------|------|
| `blur` | 高斯模糊 | `noimg blur in.png out.png 15` |
| `sharpen` | 锐化 | `noimg sharpen in.png out.png 150` |
| `edge` | 边缘检测（Sobel） | `noimg edge in.png out.png` |
| `emboss` | 浮雕效果 | `noimg emboss in.png out.png` |
| `oil` | 油画效果 | `noimg oil in.png out.png 3 32` |
| `median` | 中值滤波 | `noimg median in.png out.png 3` |
| `dilate` | 形态学膨胀 | `noimg dilate in.png out.png 2` |
| `erode` | 形态学腐蚀 | `noimg erode in.png out.png 2` |
| `gradient` | 形态学梯度 | `noimg gradient in.png out.png 2` |
| `vignette` | 暗角效果 | `noimg vignette in.png out.png 40` |
| `noise` | 添加噪声 | `noimg noise in.png out.png 30` |
| `unsharp-mask` | USM 锐化（带阈值） | `noimg unsharp-mask in.png out.png 15 150 0` |
| `box-blur` | 方框模糊 | `noimg box-blur in.png out.png 3` |
| `laplacian` | Laplacian 边缘检测 | `noimg laplacian in.png out.png` |

### 合成与通道操作

| 命令 | 说明 | 示例 |
|------|------|------|
| `composite` | 图像合成 | `noimg composite base.png overlay.png out.png 10 10` |
| `band` | 提取单通道 | `noimg band in.png out.png 0` |
| `bandjoin2` | 两图通道拼接 | `noimg bandjoin2 r.png g.png out.png` |
| `add-alpha` | 添加 Alpha 通道 | `noimg add-alpha in.png out.png` |
| `remove-alpha` | 移除 Alpha 通道 | `noimg remove-alpha in.png out.png` |
| `flatten` | Alpha 混平（RGBA→RGB） | `noimg flatten in.png out.png` |
| `roi-blend` | 区域混合 | `noimg roi-blend base.png overlay.png out.png 10 10 0 255` |
| `overlay-blend` | Overlay 混合 | `noimg overlay-blend in.png overlay.png out.png` |

### 色彩空间转换

| 命令 | 说明 | 示例 |
|------|------|------|
| `rgb2lab` | RGB 转 Lab | `noimg rgb2lab in.png out.png` |
| `lab2rgb` | Lab 转 RGB | `noimg lab2rgb in.png out.png` |
| `rgb2cmyk` | RGB 转 CMYK | `noimg rgb2cmyk in.png out.png` |
| `cmyk2rgb` | CMYK 转 RGB | `noimg cmyk2rgb in.png out.png` |

### 其他

| 命令 | 说明 | 示例 |
|------|------|------|
| `watermark` | 文字水印 | `noimg watermark in.png out.png "©2024" 4 2` |
| `to-u16` | 8-bit 转 16-bit | `noimg to-u16 in.png out.png` |
| `to-u8` | 16-bit 转 8-bit | `noimg to-u8 in.png out.png` |
| `animate` | 创建动画 GIF | `noimg animate out.gif 20 f1.png f2.png f3.png` |

## 库 API

noimg 可作为 Nolang 库使用，通过 `lib.no` 导出以下模块：

| 模块 | 职责 |
|------|------|
| `image` | 图像创建、复制、填充、像素读写、统计、常量运算、Alpha 通道管理、属性检查 |
| `pnm` | PPM/PGM/PNM 读写 |
| `bmp` | BMP 读写（24/32 位未压缩） |
| `tga` | TGA 读写（含 RLE） |
| `pam` | PAM 读写 |
| `gif` | GIF 读写（LZW 解码+隔行+透明+动画多帧+disposal+median-cut 量化+动画写出） |
| `png` | PNG 读写（zlib 压缩、CRC32 校验、5 种滤镜、Adam7 隔行解码，仅 8 位） |
| `tiff` | TIFF 读写（仅未压缩、8 位、单 strip） |
| `jpeg` | JPEG 读写（baseline DCT+Huffman 编码/解码+IDCT+YCbCr→RGB，不支持 progressive） |
| `webp` | WebP VP8L lossless 解码（Huffman+LZ77+颜色缓存+predictor(14 模式)+颜色变换(定点乘)+subtract-green+颜色索引）；写入为 VP8L 容器（真实像素，但不写 transform 头，与标准解码器不互通） |
| `colour` | 色彩空间转换（RGB↔Gray、RGB↔HSV、RGB↔HSL、RGB↔YCbCr、RGB↔Lab、RGB↔CMYK）、亮度/对比度/Gamma/阈值/色调分离/日晒/棕褐/HSV 调整/Overlay 混合/Otsu 自动阈值 |
| `resize` | 双线性缩放、缩略图、缩放、最近邻/双三次/面积平均 |
| `rotate` | 旋转（90/180/270/任意角度）、翻转、转置/反对角转置 |
| `composite` | 裁剪、自动裁剪、合成、边框、嵌入、通道合并/提取/选择、Alpha 混平、ROI 混合、多模式混合（Normal/Multiply/Screen/Overlay/Add/Subtract/Diff/Lighten/Darken/Copy）、平铺 |
| `filter` | 卷积、高斯模糊（含可分离优化）、方框模糊、锐化（含 USM）、Sobel/Laplacian 边缘检测、浮雕、中值滤波、油画、噪声、形态学（膨胀/腐蚀/梯度）、暗角 |
| `histogram` | 直方图查找/累积/打印、均衡化/归一化/拉伸、自动色阶/对比度、LUT 应用、均值/方差/标准差/熵/百分位/CDF |
| `text` | 位图字体渲染、文字水印（5x7 点阵字体，9 种位置） |

## 快速开始

```bash
# 格式转换
noimg convert input.png output.jpg

# 图像处理
noimg blur input.png blurred.png 15
noimg grayscale input.png gray.png
noimg resize input.png small.png 200 200

# 创建缩略图
noimg thumbnail photo.png thumb.png 128

# 批量处理
noimg sepia old.jpg sepia.jpg
noimg edge photo.png edges.png
noimg composite base.png overlay.png result.png 10 10
```

## 项目结构

```
noimg/
├── main.no              ; CLI 入口与命令分发
├── lib.no               ; 库导出声明
├── package.jsonc        ; 项目配置
├── src/
│   ├── image.no         ; 图像核心结构与操作
│   ├── pnm.no           ; PPM/PGM/PNM
│   ├── bmp.no           ; BMP
│   ├── tga.no           ; TGA
│   ├── pam.no           ; PAM
│   ├── png.no           ; PNG（CRC32 位运算、zlib）
│   ├── tiff.no          ; TIFF
│   ├── gif.no           ; GIF（LZW 编解码）
│   ├── jpeg.no          ; JPEG 读写（baseline DCT+Huffman 编码/解码+IDCT+YCbCr→RGB）
│   ├── webp.no          ; WebP VP8L lossless 解码（Huffman+LZ77+predictor(14 模式)+颜色变换(定点乘)+subtract-green+颜色索引）；save 不写 transform 头，仅内部 round-trip
│   ├── colour.no        ; 色彩空间转换（RGB↔Gray/HSV/HSL/YCbCr/Lab/CMYK）
│   ├── resize.no        ; 缩放
│   ├── rotate.no        ; 旋转与翻转
│   ├── composite.no     ; 合成与裁剪
│   ├── filter.no        ; 滤镜（模糊/锐化/边缘/浮雕/油画/中值/噪声/形态学/暗角）
│   ├── histogram.no     ; 直方图与统计
│   └── text.no          ; 文字渲染与水印（5x7 点阵字体）
├── tests/
│   ├── test-core.no       ; 核心图像操作测试
│   ├── test-pnm.no        ; PNM 格式往返测试
│   ├── test-colour.no     ; 色彩空间转换测试
│   ├── test-filter.no     ; 滤镜操作测试
│   ├── test-composite.no  ; 合成操作测试
│   ├── test-histogram.no  ; 直方图操作测试
│   └── test-resize-rotate.no ; 缩放与旋转测试
└── dist/                ; 构建产物
```

## 已知限制

- WebP 写入不写 transform 头，与标准 WebP 解码器不互通（仅 noimg save→noimg load 可 round-trip）
- WebP 不支持 lossy VP8 格式
- JPEG 不支持 progressive 格式
- TIFF 仅支持未压缩、8 位、单 strip 格式
- PNG 仅支持 8 位色深
- 16-bit 图像暂不支持进入 resize/filter/colour/IO 管线

## 许可证

MIT
