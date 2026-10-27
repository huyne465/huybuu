# ROXY ENGLISH – Sách tiếng Anh lớp 2, 3, 4

Ba quyển sách riêng biệt (mỗi lớp một quyển), mỗi quyển **10 unit**, mỗi unit **20 phần**
(mẫu gốc có 15 phần), có bìa, trang hướng dẫn, mục lục có số trang, bookmark PDF và
đáp án cho giáo viên ở cuối sách.

| File | Nội dung |
|---|---|
| `output/ROXY_English_Grade_2.pdf` | Lớp 2 – Beginner |
| `output/ROXY_English_Grade_3.pdf` | Lớp 3 – Elementary |
| `output/ROXY_English_Grade_4.pdf` | Lớp 4 – Pre-Intermediate |

## 20 phần của mỗi unit

1. Big Question · 2. Vocabulary (20 thẻ từ có hình) · 3. Phonics Fun · 4. Sentence Patterns ·
5. Grammar in Use · 6. Sing & Chant · 7. Reading 1 – Easy · 8. Reading 2 – More Practice ·
9. Reading 3 – Challenge · 10. Comic Story · 11. Speak Up! · 12. Real-life Conversations ·
13. Listen & Respond · 14. Brain Games (tìm từ, xếp chữ, từ khác loại, câu đố) ·
15. Let's Play Together · 16. Write About You · 17. Life Skill & Value · 18. Did You Know? ·
19. ROXY Project · 20. Review & I Can… (+ Unit Message)

Phần mới so với mẫu: Phonics, Sing & Chant, Comic Story, Brain Games, Let's Play, Did You Know?,
bài đúng/sai và ô "vẽ lại câu chuyện" cho mỗi bài đọc, đáp án cuối sách.

## Danh sách unit

Sửa trong `scripts/topics.py` (thêm unit = thêm một dòng).

- **Lớp 2:** My School · My Family · My Body · Colours and Shapes · My Toys · Animals at the Zoo ·
  Food and Drinks · My House · My Clothes · Weather and Seasons
- **Lớp 3:** Me and My Friends · My School Things · My Hobbies · My Day · Rooms in My Home ·
  My Pets · Jobs People Do · Sports and Games · At the Park · Food I Like
- **Lớp 4:** Countries and Nationalities · My Week and Timetable · Birthdays and Months ·
  What I Can Do · Places in My Town · Tet and Festivals · Healthy Habits · Going Shopping ·
  Wild Animals · My Summer Holiday

## Cách chạy lại

Cần `GEMINI_API_KEY`, Python 3 (`pillow`, `pypdf`), Node + Playwright (Chromium), `pdftoppm` (tuỳ chọn).

```bash
cd english-books/scripts
python3 gen_content.py        # Gemini soạn nội dung -> content/gradeN/unitXX.json (bỏ qua unit đã có)
python3 proofread.py          # Gemini biên tập/soát lỗi từng unit (ghi lại danh sách sửa trong "edits")
python3 check_content.py      # kiểm tra số lượng, đáp án, emoji, độ dài bài đọc
python3 gen_images.py         # Gemini tạo ~260 ảnh minh hoạ / quyển -> images/ (bỏ qua ảnh đã có)
python3 build_book.py         # xuất 3 file PDF vào output/
```

`TEXT_MODEL` / `IMAGE_MODEL` / `WORKERS` đổi model và số luồng.

### Về ảnh minh hoạ

Ảnh minh hoạ cần key Gemini **có bật billing** (Free Tier có hạn mức tạo ảnh = 0).
Khi chưa có ảnh, sách tự dùng hình minh hoạ bằng emoji màu. Sau khi bật billing chỉ cần chạy
`gen_images.py` rồi `build_book.py` — ảnh AI sẽ tự thay vào: bìa sách, ảnh mở đầu mỗi unit,
20 thẻ từ vựng, 3 ảnh bài đọc, truyện tranh 4 khung, 2 ảnh hội thoại, ảnh kỹ năng sống và dự án
(≈ 28 ảnh/unit, ≈ 840 ảnh cho 3 quyển).

Nội dung do AI soạn và đã qua một vòng biên tập tự động; giáo viên nên đọc duyệt lại trước khi in.
