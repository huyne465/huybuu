# Phố đi bộ Nguyễn Huệ về đêm: bộ prompt ảnh chân thực

Mục tiêu: dựng lại bộ ảnh tham chiếu thành ảnh **trông như chụp thật**, bỏ hết dấu vết AI
(sáng đều, mọi thứ đều nét, siêu chi tiết, màu cam–xanh quá đà, bố cục đối xứng gương, trăng to bất thường).
Bối cảnh chung: **Phố đi bộ Nguyễn Huệ, Quận 1, TP.HCM, ban đêm**.
Riêng ảnh 4 giữ lối ảnh xưa thật (ảnh tấm kính / bạc gelatin).

---

## Khối dùng chung (dán vào cuối mọi prompt màu, tức ảnh 1–3)

```
shot on a full-frame mirrorless camera, real lens characteristics, natural
mixed color temperatures (warm sodium and 3000K LED street lamps against cool
5600K shop light and bluish ambient sky glow), realistic exposure with
crushed shadows and a few clipped highlights, visible fine luminance noise at
high ISO, slight chromatic aberration at frame edges, mild vignetting, shallow
but believable depth of field, real-world clutter, imperfect candid
composition, unretouched documentary street photography, no HDR
```

## Negative chung (Stable Diffusion / Flux / Leonardo…)

```
hdr, oversaturated, teal and orange grading, glowing outlines, overly sharp
everywhere, plastic skin, airbrushed, painting, illustration, 3d render,
cgi, concept art, fantasy, surreal, mirrored symmetry, giant moon, perfect
clouds, lens flare stars, bokeh hearts, extra fingers, warped text, gibberish
signage, duplicated buildings, impossible architecture, cinematic poster,
artstation, unreal engine, octane, dramatic god rays
```

Midjourney: thêm `--style raw --stylize 50 --ar 9:16`, kèm `--no hdr, illustration, cgi, surreal`.

---

## Ảnh 1: Chàng trai đeo tai nghe trước tòa nhà cũ, Bitexco phía xa

Thay đổi so với ảnh gốc: bỏ bức "bích họa" bịa trên mặt tiền, bỏ ánh vàng phủ đều.
Thay bằng mặt tiền thật, cũ, dọc Nguyễn Huệ. Bitexco có tỉ lệ đúng và nằm ở cuối phố.

```
Candid night street photograph on Nguyen Hue walking street, District 1,
Ho Chi Minh City, shortly after rain. A young Vietnamese man seen from behind,
three-quarter rear view, wearing over-ear headphones, an olive overshirt,
dark jeans, white sneakers and a worn backpack, glancing at his phone. He
stands on the wet grey granite paving of the pedestrian plaza. To his right,
an old French-colonial era building with peeling cream paint, water stains,
green wooden shutters, air-conditioner units, tangled electric cables and a
small cafe sign on a balcony. At the far end of the street the Bitexco
Financial Tower rises, small in the frame and slightly hazy in humid air.
Tamarind trees, rows of white street lamps, scattered pedestrians, a couple
taking selfies, a street vendor with a cart, motorbike headlights on the side
lane. Puddles reflect lamps unevenly. 35mm lens at f/1.8, 1/60s, ISO 3200,
eye-level, vertical 9:16.
```
+ khối dùng chung.

---

## Ảnh 2: Trụ sở UBND TP.HCM nhìn từ phố đi bộ, trăng lên

Thay đổi: bỏ bố cục gương siêu thực "phố trên, làng sông nước dưới".
Giữ trục nhìn về UBND, mặt sàn ướt phản chiếu và vầng trăng. Trăng chỉ to được nhờ ống tele nén phối cảnh, không phải vì phóng đại.

```
Night photograph looking straight down Nguyen Hue walking street toward the
Ho Chi Minh City People's Committee building (former Hotel de Ville), its
cream and yellow facade and clock tower floodlit, red flag with yellow star
on the tower. The bronze statue of President Ho Chi Minh on its plinth in
front, with flower beds. Wet granite plaza in the foreground with patchy,
broken reflections and shallow puddles. Crowds of locals and tourists
walking, kids on rental electric cars, a family sitting on a planter edge,
vendors selling balloons. Low-rise and high-rise buildings on both sides with
lit shop windows and real signage. A full moon partly veiled by thin humid
clouds above the clock tower, rendered at realistic size for a 135mm
telephoto lens. Shot handheld, 135mm at f/2.8, 1/125s, ISO 4000, slight
compression, vertical 9:16.
```
+ khối dùng chung.

---

## Ảnh 3: Toàn cảnh Nguyễn Huệ từ trên cao, hướng ra sông Sài Gòn

Thay đổi: ảnh gốc là con kênh tưởng tượng. Nguyễn Huệ vốn là **kênh Chợ Vải (Canal Charner), bị lấp năm 1887**,
nên ảnh làm lại giữ góc nhìn từ trên cao dọc trục phố ra tới mặt sông thật.

```
Elevated night photograph from a rooftop bar on Nguyen Hue, looking down the
full length of the pedestrian boulevard toward the Saigon River. The long
granite plaza glows with rows of street lamps and fountain lights, small
crowds visible as tiny figures. Both sides lined with a mix of old
French-colonial facades with tile roofs, the old 42 Nguyen Hue apartment
block full of small cafes with mismatched lit windows, and modern glass
towers. Taxis and motorbikes stream as light trails on the parallel side
lanes (long exposure). At the end, the dark Saigon River with lit ferries and
the Thu Thiem bank skyline beyond. Moon low over the river, small, with light
haze and city light pollution in the sky. Tripod, 24mm at f/8, 4-second
exposure, ISO 200, vertical 9:16.
```
+ khối dùng chung (bỏ cụm "visible fine luminance noise at high ISO", vì ảnh này chụp ISO thấp).

---

## Ảnh 4: Ảnh xưa thật, Boulevard Charner (Nguyễn Huệ ngày nay) lúc chạng vạng, khoảng 1920

Giữ tinh thần ảnh gốc: đường rợp cây, xe kéo, người áo trắng đội nón cối, đầu máy hơi nước.
Chuyển thời điểm sang lúc chạng vạng, khi đèn đường vừa thắp. Chụp phơi sáng lâu nên người đi lại bị nhòe như ảnh thật thời ấy.

```
Authentic vintage photograph circa 1920, Boulevard Charner in Saigon (today's
Nguyen Hue street), French Indochina, at dusk just as the gas street lamps
are lit. Wide unpaved boulevard lined with tall tamarind trees, cast-iron
lamp posts with soft halos, rickshaws parked along the curb, a small steam
tram with wooden carriages and a plume of smoke, men in white cotton suits
and pith helmets, Vietnamese vendors in ao dai and conical hats with
shoulder-pole baskets. Long exposure: moving people appear as soft ghostly
blurs, stationary figures sharp. Gelatin silver print from a glass plate
negative, warm sepia toning, low contrast, lifted blacks, soft corners,
lens falloff, film grain, faint hand-tinting, dust specks, fine scratches,
emulsion flaws near the edges, slightly uneven development, aged paper.
Horizontal 4:3.
```

Negative riêng cho ảnh 4:
```
modern objects, cars, asphalt markings, LED lights, sharp digital detail,
high contrast, saturated color, colorized look, clean restoration, hdr,
painting, illustration, smiling posed faces
```
Midjourney: `--style raw --stylize 25 --ar 4:3`.

---

## Ảnh 5

Chỉ nhận được 4 ảnh tham chiếu. Gửi ảnh thứ 5 để bổ sung prompt tương ứng.

---

## Mẹo hậu kỳ để ảnh bớt "mùi AI"

1. Xuất ra rồi thêm grain thật (ví dụ Lightroom: Grain 15–25, Size 20). Riêng ảnh 4 dùng mức cao hơn.
2. Hạ Clarity/Texture khoảng −5 đến −10. Ảnh AI thường nét gắt vô lý ở vùng tối.
3. Kiểm tra lại chữ trên biển hiệu. Chữ méo thì inpaint hoặc làm mờ nhẹ cho giống bị lệch nét.
4. Kiểm tra tay, chân, bóng đổ người và vật phản chiếu trên mặt sàn ướt có khớp với nguồn sáng không.
5. Ảnh 1–3: crop lệch tâm một chút, đừng để chủ thể ngay giữa khung.
