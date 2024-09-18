from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import os
import chardet

# 저장할 데이터를 담을 리스트
Yestwo_stores = []

# 크롤링할 페이지 범위 설정
for page in range(1, 11):
    # URL 설정
    Yestwo_url = f"https://www.yes24.com/24/Category/Display/001001046003?PageNumber={page}"
    print(f"Crawling URL: {Yestwo_url}")

    # 페이지 요청
    try:
        response = urllib.request.urlopen(Yestwo_url)
        raw_html = response.read()

        # 인코딩 감지
        result = chardet.detect(raw_html)
        encoding = result['encoding']

        # HTML 콘텐츠를 감지된 인코딩으로 디코딩
        html_content = raw_html.decode(encoding)
        soup_Yestwo = BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        print(f"URL {Yestwo_url}을 가져오는 중 오류 발생: {e}")
        continue

    # 데이터가 있는 영역을 찾기
    main_content = soup_Yestwo.find('div', {'id': 'category_layout'})

    if main_content is None:
        print(f"페이지 {page}에서 콘텐츠를 찾을 수 없습니다.")
        continue

    # 데이터 추출
    for item in main_content.find_all('li'):
        try:
            # 도서명
            book_name_div = item.find('div', {'class': 'goods_name'})
            book_name_tag = book_name_div.find('a') if book_name_div else None
            book_name = book_name_tag.text.strip() if book_name_tag else ''

            # 저자 정보
            author_info_span = item.find('span', {'class': 'goods_auth'})
            author_info = author_info_span.text.strip() if author_info_span else ''

            # 출판사
            publisher_span = item.find('span', {'class': 'goods_pub'})
            publisher = publisher_span.text.strip() if publisher_span else ''

            # 평점
            rating_span = item.find('span', {'class': 'gd_rating'})
            rating_tag = rating_span.find('em', {'class': 'yes_b'}) if rating_span else None
            rating = rating_tag.text.strip() if rating_tag else ''

            # 회원리뷰수
            review_count_span = item.find('span', {'class': 'gd_reviewCount'})
            review_count_tag = review_count_span.find('em') if review_count_span else None
            review_count = review_count_tag.text.strip() if review_count_tag else ''

            # 데이터를 리스트에 추가
            Yestwo_stores.append([book_name, author_info, publisher, rating, review_count])
        except AttributeError as e:
            print(f"아이템 파싱 중 오류 발생: {e}")
            continue

# 데이터가 있는지 확인
if Yestwo_stores:
    print(f"크롤링 결과: \n{Yestwo_stores}")

    # 데이터프레임 생성
    Yestwo_tbl = pd.DataFrame(data=Yestwo_stores, columns=['도서명', '저자 정보', '출판사', '평점', '회원리뷰수'])

    # 데이터 정리
    Yestwo_tbl.replace('', pd.NA, inplace=True)
    Yestwo_tbl.dropna(how='all', inplace=True)
    Yestwo_tbl.reset_index(drop=True, inplace=True)
    Yestwo_tbl.columns = [col.strip() for col in Yestwo_tbl.columns]

    # CSV 파일로 저장 (utf-8 인코딩)
    Yestwo_tbl.to_csv("./Yestwo_table.csv", encoding='utf-8', mode='w', index=False, header=True)

    # 엑셀 파일로 저장
    try:
        file_path = "./Yestwo_table_new.xlsx"
        if os.path.exists(file_path):
            os.remove(file_path)  # 기존 파일이 있으면 삭제
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            Yestwo_tbl.to_excel(writer, index=False, sheet_name='Books')
        print("엑셀 파일로 데이터 저장 완료.")
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")
else:
    print("저장할 데이터가 없습니다.")
