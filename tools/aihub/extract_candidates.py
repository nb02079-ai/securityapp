#!/usr/bin/env python3
"""
AI Hub '주제별 텍스트 일상 대화 데이터'에서 평가·개발용 일반 대화 후보를 뽑는 스크립트.

목적
  plan.md 5.2의 "헷갈리는 일반 대화"(연애·돈·만남 이야기가 섞였지만 정상인 대화)
  후보를 골라내고, 직접 고른 대화를 재생 형식으로 바꾼다.

사용법 (Python 3.8 이상, 기본 라이브러리만 사용)
  1) 후보 뽑기
     python extract_candidates.py scan --data-root "C:\\...\\020.주제별 텍스트 일상 대화 데이터\\01.데이터"

  2) 묶음별 무작위 검토 목록 만들기 (시드 고정 → 같은 명령이면 같은 목록)
     python extract_candidates.py sample --out "<scan 결과 폴더>" --split validation

  3) review_<split>.txt 로 대화를 읽고, review_<split>.csv 의 selected 칸에 Y 입력 후 저장

  4) 고른 대화를 재생 형식으로 내보내기
     python extract_candidates.py export --out "<scan 결과 폴더>" --split validation

원칙
  - 압축을 풀지 않고 zip 안의 라벨링 JSON을 바로 읽는다. 원천데이터(txt)는 읽지 않는다.
  - '라벨링데이터'로 시작하는 폴더를 모두 읽고, 같은 파일 이름이 겹치면 이름이 긴(나중에
    추가된) 폴더, 예: 라벨링데이터_250929_add 쪽을 쓴다.
  - 평가 세트 후보는 Validation에서, 규칙 개발용은 Training에서 뽑는다 (섞지 않음).
  - 결과는 저장소 밖에 둔다. 출력 폴더가 git 저장소 안이면 멈춘다.
  - 화면 출력에는 대화 내용을 찍지 않는다.
"""

import argparse
import csv
import json
import os
import re
import sys
import unicodedata
import zipfile
from collections import Counter

# ---------------------------------------------------------------------------
# 설정값
# ---------------------------------------------------------------------------

# 후보로 뽑을 주제 (비교할 때 공백은 무시). 실제 주제 이름은 scan 후 stats 파일에서 확인.
DEFAULT_TOPICS = ["연애/결혼", "상거래 전반", "회사/아르바이트"]

# 주제와 관계없이 후보로 뽑을 단어 묶음.
# 일반 대화에서 오경고를 유발할 만한 말을 넓게 잡는다 (걸린 단어는 CSV에서 직접 확인).
KEYWORD_GROUPS = {
    "금전": r"송금|입금|이체|계좌|통장|대출|수수료|선입금|돈\s?보내|돈\s?빌려|돈\s?갚|빌려\s?줘|갚을게",
    "투자": r"투자|수익|코인|주식|종목|리딩|(?<!지)원금|배당|수익률|비트",  # '재난지원금'의 '원금' 제외
    "만남": r"만나|만날래|데이트|얼굴\s?보|밥\s?먹자",
    "외부이동": r"텔레그램|오픈채팅|오픈톡|링크|http|www\.|\.com|앱\s?(?:설치|깔)|어플\s?(?:설치|깔)|아이디\s?알려",
    # 스미싱이 자주 사칭하는 소재 (재난지원금·환급 등). 정상 대화에서도 흔해 오탐 측정에 유용
    "지원금": r"지원금|환급|정부\s?지원",
}

TOPIC_MARKER = re.compile(r"^\$(.+)$")
# 원본 데이터 오류: 대화 끝에 앞선 메시지를 "1 : 내용" 형태로 한 번 더 붙인 줄이 있다.
# "2 : 1로 이겼어" 같은 정상 메시지를 지우지 않도록, 뒤 내용이 앞선 메시지와 같을 때만 제외한다.
ECHO_LINE = re.compile(r"^(\d+)\s*:\s*(.+)$")
MAX_TOPIC_LEN = 20  # "$100 벌었어" 같은 일반 메시지를 주제 표시로 오인하지 않기 위한 제한
SPLIT_NAMES = ("training", "validation")
LABEL_DIR_PREFIX = "라벨링데이터"

# sample: 검토 목록 묶음. 위에서부터 차례로 배정하며, 한 대화는 한 묶음에만 들어간다.
#   (이름, 설명, 기본 개수)
SAMPLE_BUCKETS = [
    ("다자간", "다자간 대화 (단체방 비교용)", 999),
    ("금전_투자_외부_지원금", "금전·투자·외부이동·지원금 단어가 걸린 대화", 50),
    ("연애_만남", "연애/결혼 주제 + 만남 단어 (로맨스 사기 비교용)", 25),
    ("주제만", "키워드 없이 주제만 맞는 대화 (쉬운 정상 대화)", 15),
]
DEFAULT_SEED = 20261020

CSV_FIELDS = [
    "candidate_id", "split", "label_folder", "container", "platform", "speaker_type",
    "n_speakers", "topic", "topic_match", "keyword_groups", "matched_words",
    "n_messages", "selected",
]


def nfc(s):
    return unicodedata.normalize("NFC", s)


def squash(s):
    return re.sub(r"\s+", "", nfc(s))


# ---------------------------------------------------------------------------
# 파일 찾기
# ---------------------------------------------------------------------------

def find_split_dirs(data_root):
    """data_root 아래에서 Training / Validation 폴더를 찾는다."""
    found = {}
    for name in sorted(os.listdir(data_root)):
        path = os.path.join(data_root, name)
        if not os.path.isdir(path):
            continue
        low = nfc(name).lower()
        for split in SPLIT_NAMES:
            if split in low:
                if split in found:
                    sys.exit(f"[오류] '{split}' 폴더가 두 개 이상입니다: {found[split]}, {path}")
                found[split] = path
    if not found:
        subdirs = [n for n in os.listdir(data_root) if os.path.isdir(os.path.join(data_root, n))]
        sys.exit(f"[오류] {data_root} 안에서 Training/Validation 폴더를 찾지 못했습니다. 하위 폴더: {subdirs}")
    return found


def find_label_dirs(split_dir):
    """'라벨링데이터'로 시작하는 폴더들. 이름순 정렬 → 뒤에 오는 폴더가 우선."""
    dirs = []
    for name in os.listdir(split_dir):
        path = os.path.join(split_dir, name)
        if os.path.isdir(path) and nfc(name).startswith(LABEL_DIR_PREFIX):
            dirs.append((nfc(name), path))
    dirs.sort(key=lambda x: (len(x[0]), x[0]))  # '라벨링데이터'가 '_add'보다 먼저
    return dirs


def index_json_files(label_dirs):
    """
    파일 이름 → (폴더 이름, 컨테이너 경로, zip 안 경로 또는 None) 색인.
    zip 파일과 이미 압축이 풀린 json 파일을 모두 지원한다.
    같은 이름이 여러 폴더에 있으면 나중 폴더가 덮어쓴다.
    """
    index = {}
    overlaps = 0
    for folder_name, folder_path in label_dirs:
        seen_here = set()
        for root, _, files in os.walk(folder_path):
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                low = fname.lower()
                entries = []
                if low.endswith(".zip"):
                    try:
                        with zipfile.ZipFile(fpath) as zf:
                            for member in zf.namelist():
                                if member.lower().endswith(".json") and not member.endswith("/"):
                                    entries.append((os.path.basename(member), fpath, member))
                    except zipfile.BadZipFile:
                        print(f"[경고] 열 수 없는 zip: {fpath}")
                        continue
                elif low.endswith(".json"):
                    entries.append((fname, fpath, None))
                for key, container, member in entries:
                    key = nfc(key)
                    if key in seen_here:
                        continue  # 같은 폴더 안 중복은 처음 것만
                    seen_here.add(key)
                    if key in index and index[key][0] != folder_name:
                        overlaps += 1
                    index[key] = (folder_name, container, member)
    return index, overlaps


def load_json(container, member, zip_cache):
    if member is None:
        with open(container, "rb") as f:
            raw = f.read()
    else:
        zf = zip_cache.get(container)
        if zf is None:
            zf = zipfile.ZipFile(container)
            zip_cache[container] = zf
        raw = zf.read(member)
    return json.loads(raw.decode("utf-8-sig"))


# ---------------------------------------------------------------------------
# 대화 처리
# ---------------------------------------------------------------------------

def speaker_of(line):
    sp = line.get("speaker") or {}
    sid = str(sp.get("id", "")).replace("번", "").strip()
    if not sid:
        m = re.match(r"^\s*(\S+)\s*:", line.get("text", ""))
        sid = m.group(1) if m else "?"
    return sid, sp.get("sex", ""), sp.get("age", "")


def is_topic_marker(topic, line):
    """'$주제' 줄인지 판정. 화행이 N/A이거나, 숫자로 시작하지 않는 짧은 텍스트일 때만 인정."""
    if not topic:
        return False
    if str(line.get("speechAct", "")).strip().upper() == "N/A":
        return True
    return len(topic) <= MAX_TOPIC_LEN and not topic[0].isdigit()


def split_segments(annotations):
    """
    '$주제' 줄을 기준으로 대화를 구간으로 나눈다.
    첫 구간의 주제 = annotations.subject, 이후는 '$' 뒤의 주제.
    반환: [(주제, [메시지...]), ...], 첫 줄 '$' 주제(없으면 None),
          제외한 오류 줄 수, 모양만 비슷해 남긴 줄 수
    """
    subject = nfc(str(annotations.get("subject", ""))).strip()
    segments = []
    current_topic = subject
    current = []
    first_marker_topic = None
    seen_texts = set()
    echo_dropped = 0
    echo_kept = 0
    lines = annotations.get("lines") or []
    for i, line in enumerate(lines):
        text = nfc(str(line.get("norm_text", line.get("text", "")))).strip()
        m = TOPIC_MARKER.match(text)
        if m and not is_topic_marker(m.group(1).strip(), line):
            m = None
        if m:
            if i == 0:
                first_marker_topic = m.group(1).strip()
            if current:
                segments.append((current_topic, current))
            current_topic = m.group(1).strip()
            current = []
            continue
        e = ECHO_LINE.match(text)
        if e:
            if squash(e.group(2)) in seen_texts:
                echo_dropped += 1
                continue
            echo_kept += 1
        seen_texts.add(squash(text))
        sid, sex, age = speaker_of(line)
        current.append({"sender": sid, "sex": sex, "age": age, "text": text})
    if current:
        segments.append((current_topic, current))
    return segments, first_marker_topic, echo_dropped, echo_kept


def keyword_hits(messages, compiled):
    groups, words = [], []
    for gname, pattern in compiled.items():
        found = set()
        for msg in messages:
            for m in pattern.finditer(msg["text"]):
                found.add(m.group(0))
        if found:
            groups.append(gname)
            words.extend(sorted(found))
    return groups, words


def find_git_root(path):
    cur = os.path.abspath(path)
    while True:
        if os.path.exists(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


# ---------------------------------------------------------------------------
# scan
# ---------------------------------------------------------------------------

def scan_split(split, split_dir, out_dir, topics, compiled, min_messages):
    label_dirs = find_label_dirs(split_dir)
    if not label_dirs:
        print(f"[경고] {split}: '{LABEL_DIR_PREFIX}' 폴더가 없어 건너뜁니다.")
        return None
    print(f"[{split}] 라벨 폴더: {[n for n, _ in label_dirs]}")

    index, overlaps = index_json_files(label_dirs)
    print(f"[{split}] JSON 파일 {len(index):,}개 (폴더 간 겹침 {overlaps:,}개, 뒤 폴더 우선)")

    topic_keys = {squash(t) for t in topics}
    stats = {
        "split": split,
        "label_folders": [n for n, _ in label_dirs],
        "files_indexed": len(index),
        "folder_overlaps": overlaps,
        "files_parsed": 0,
        "parse_errors": 0,
        "files_with_topic_change": 0,
        "files_first_line_marker_differs_from_subject": 0,
        "echo_lines_dropped": 0,
        "echo_like_lines_kept": 0,
        "segments_total": 0,
        "segments_by_topic": Counter(),
        "segments_by_speaker_type": Counter(),
        "candidates_total": 0,
        "skipped_too_short": 0,
        "candidates_by_reason": Counter(),
        "candidates_by_keyword_group": Counter(),
        "candidates_by_speaker_type": Counter(),
    }
    error_files = []

    csv_path = os.path.join(out_dir, f"candidates_{split}.csv")
    jsonl_path = os.path.join(out_dir, f"candidates_{split}.jsonl")
    zip_cache = {}
    try:
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as fcsv, \
             open(jsonl_path, "w", encoding="utf-8") as fjl:
            writer = csv.DictWriter(fcsv, fieldnames=CSV_FIELDS)
            writer.writeheader()

            for n, key in enumerate(sorted(index), 1):
                folder_name, container, member = index[key]
                try:
                    data = load_json(container, member, zip_cache)
                    infos = data.get("info") or []
                except Exception as e:  # 파일 하나가 깨져도 전체는 계속
                    stats["parse_errors"] += 1
                    error_files.append(f"{key}: {type(e).__name__}")
                    continue
                stats["files_parsed"] += 1

                for info_i, info in enumerate(infos):
                    ann = info.get("annotations") or {}
                    title = nfc(str(info.get("title") or os.path.splitext(key)[0]))
                    if len(infos) > 1:
                        title = f"{title}__i{info_i + 1}"
                    platform = nfc(str(info.get("medianame", "")))
                    speaker_type = nfc(str(ann.get("speaker_type", "")))
                    subject = nfc(str(ann.get("subject", ""))).strip()

                    segments, first_marker, dropped, kept = split_segments(ann)
                    stats["echo_lines_dropped"] += dropped
                    stats["echo_like_lines_kept"] += kept
                    if len(segments) > 1:
                        stats["files_with_topic_change"] += 1
                    if first_marker is not None and squash(first_marker) != squash(subject):
                        stats["files_first_line_marker_differs_from_subject"] += 1

                    for s_i, (topic, msgs) in enumerate(segments, 1):
                        stats["segments_total"] += 1
                        stats["segments_by_topic"][topic] += 1
                        stats["segments_by_speaker_type"][speaker_type] += 1

                        topic_match = squash(topic) in topic_keys
                        groups, words = keyword_hits(msgs, compiled)
                        if not (topic_match or groups):
                            continue
                        if len(msgs) < min_messages:
                            stats["skipped_too_short"] += 1
                            continue

                        cid = f"{title}__s{s_i}"
                        reason = ("주제+키워드" if topic_match and groups
                                  else "주제" if topic_match else "키워드")
                        stats["candidates_total"] += 1
                        stats["candidates_by_reason"][reason] += 1
                        stats["candidates_by_speaker_type"][speaker_type] += 1
                        for g in groups:
                            stats["candidates_by_keyword_group"][g] += 1

                        writer.writerow({
                            "candidate_id": cid,
                            "split": split,
                            "label_folder": folder_name,
                            "container": os.path.basename(container),
                            "platform": platform,
                            "speaker_type": speaker_type,
                            "n_speakers": len({m["sender"] for m in msgs}),
                            "topic": topic,
                            "topic_match": "Y" if topic_match else "",
                            "keyword_groups": "|".join(groups),
                            "matched_words": "|".join(words),
                            "n_messages": len(msgs),
                            "selected": "",
                        })
                        fjl.write(json.dumps({
                            "candidate_id": cid,
                            "split": split,
                            "source_file": key,
                            "platform": platform,
                            "speaker_type": speaker_type,
                            "topic": topic,
                            "messages": msgs,
                        }, ensure_ascii=False) + "\n")

                if n % 5000 == 0:
                    print(f"[{split}] {n:,}/{len(index):,} 처리")
    finally:
        for zf in zip_cache.values():
            zf.close()

    stats_out = {k: (dict(v.most_common()) if isinstance(v, Counter) else v) for k, v in stats.items()}
    stats_out["error_files"] = error_files[:200]
    with open(os.path.join(out_dir, f"stats_{split}.json"), "w", encoding="utf-8") as f:
        json.dump(stats_out, f, ensure_ascii=False, indent=2)

    print(f"[{split}] 완료: 파일 {stats['files_parsed']:,}개 읽음, 오류 {stats['parse_errors']:,}개, "
          f"구간 {stats['segments_total']:,}개, 후보 {stats['candidates_total']:,}개 "
          f"(메시지 {min_messages}개 미만이라 제외 {stats['skipped_too_short']:,}개)")
    print(f"[{split}] 주제가 바뀌는 파일 {stats['files_with_topic_change']:,}개, "
          f"첫 줄 $주제가 subject와 다른 파일 {stats['files_first_line_marker_differs_from_subject']:,}개")
    print(f"[{split}] 앞 메시지를 반복한 오류 줄 제외 {stats['echo_lines_dropped']:,}개, "
          f"'숫자 : '로 시작하지만 정상으로 보고 남긴 줄 {stats['echo_like_lines_kept']:,}개")
    missing = [t for t in topics if squash(t) not in {squash(k) for k in stats["segments_by_topic"]}]
    if missing:
        print(f"[{split}] [주의] 데이터에 없는 주제 이름: {missing} → stats_{split}.json의 segments_by_topic에서 실제 이름 확인")
    return stats_out


def cmd_scan(args):
    data_root = os.path.abspath(args.data_root)
    if not os.path.isdir(data_root):
        sys.exit(f"[오류] 데이터 폴더가 없습니다: {data_root}")
    out_dir = os.path.abspath(args.out or os.path.join(os.path.dirname(data_root), "candidates_out"))

    git_root = find_git_root(out_dir)
    if git_root and not args.allow_in_repo:
        sys.exit(f"[오류] 출력 폴더가 git 저장소({git_root}) 안에 있습니다. "
                 f"재배포 금지 데이터가 커밋될 수 있어 멈춥니다. --out 으로 저장소 밖 폴더를 지정하세요.")
    os.makedirs(out_dir, exist_ok=True)

    compiled = {g: re.compile(p) for g, p in KEYWORD_GROUPS.items()}
    topics = args.topics or DEFAULT_TOPICS
    splits = find_split_dirs(data_root)
    targets = SPLIT_NAMES if args.split == "both" else (args.split,)

    for split in targets:
        if split not in splits:
            print(f"[경고] {split} 폴더를 찾지 못해 건너뜁니다.")
            continue
        scan_split(split, splits[split], out_dir, topics, compiled, args.min_messages)

    print(f"\n결과 폴더: {out_dir}")
    print("평가 세트 후보는 candidates_validation.csv, 규칙 개발용은 candidates_training.csv를 쓰세요.")


def read_csv_rows(path):
    """엑셀이 저장하며 인코딩을 바꿀 수 있어 UTF-8과 cp949를 차례로 시도한다."""
    for enc in ("utf-8-sig", "cp949"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    sys.exit(f"[오류] CSV 인코딩을 읽지 못했습니다. UTF-8로 다시 저장해 주세요: {path}")


def is_selected(value):
    return str(value or "").strip().upper() in ("Y", "1", "O", "TRUE")


def load_candidates(jsonl_path, wanted):
    """jsonl에서 wanted에 든 candidate_id만 읽어 {id: 레코드}로 돌려준다."""
    found = {}
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec["candidate_id"] in wanted:
                found[rec["candidate_id"]] = rec
    return found


# ---------------------------------------------------------------------------
# sample
# ---------------------------------------------------------------------------

def bucket_of(row):
    groups = set(filter(None, row.get("keyword_groups", "").split("|")))
    if row.get("speaker_type", "") == "다자간 대화":
        return "다자간"
    if groups & {"금전", "투자", "외부이동", "지원금"}:
        return "금전_투자_외부_지원금"
    if squash(row.get("topic", "")) == squash("연애/결혼") and "만남" in groups:
        return "연애_만남"
    if row.get("topic_match") == "Y" and not groups:
        return "주제만"
    return None


def cmd_sample(args):
    import random

    out_dir = os.path.abspath(args.out)
    csv_path = os.path.join(out_dir, f"candidates_{args.split}.csv")
    jsonl_path = os.path.join(out_dir, f"candidates_{args.split}.jsonl")
    for p in (csv_path, jsonl_path):
        if not os.path.isfile(p):
            sys.exit(f"[오류] 파일이 없습니다: {p} (먼저 scan을 실행하세요)")

    review_csv = os.path.join(out_dir, f"review_{args.split}.csv")
    if os.path.exists(review_csv) and not args.force:
        sys.exit(f"[오류] {review_csv} 가 이미 있습니다. 검토 중인 표시를 지우지 않도록 멈춥니다. "
                 f"다시 만들려면 --force 를 붙이세요.")

    sizes = {"다자간": args.n_group, "금전_투자_외부_지원금": args.n_money,
             "연애_만남": args.n_romance, "주제만": args.n_topic}

    pools = {name: [] for name, _, _ in SAMPLE_BUCKETS}
    for row in read_csv_rows(csv_path):
        b = bucket_of(row)
        if b:
            pools[b].append(row)

    rng = random.Random(args.seed)
    picked = []
    print(f"[sample] {args.split}, 시드 {args.seed}")
    for name, desc, _ in SAMPLE_BUCKETS:
        pool = sorted(pools[name], key=lambda r: r["candidate_id"])  # 같은 시드 → 같은 결과
        n = min(sizes[name], len(pool))
        chosen = sorted(rng.sample(pool, n), key=lambda r: r["candidate_id"])
        for r in chosen:
            r = dict(r)
            r["bucket"] = name
            r["selected"] = ""
            picked.append(r)
        note = "" if n == sizes[name] or sizes[name] >= 999 else f" (요청 {sizes[name]}개보다 적음)"
        print(f"  {name}: 후보 {len(pool):,}개 중 {n}개{note} - {desc}")

    fields = ["bucket"] + CSV_FIELDS
    with open(review_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(picked)

    # 대화를 읽으며 고를 수 있도록 원문을 한 파일에 모은다
    recs = load_candidates(jsonl_path, {r["candidate_id"] for r in picked})
    review_txt = os.path.join(out_dir, f"review_{args.split}.txt")
    with open(review_txt, "w", encoding="utf-8") as f:
        for i, r in enumerate(picked, 1):
            rec = recs.get(r["candidate_id"])
            f.write(f"===== [{i}/{len(picked)}] {r['candidate_id']}  |  묶음: {r['bucket']}  |  "
                    f"주제: {r['topic']}  |  {r['speaker_type']}  |  걸린 단어: {r['matched_words'] or '-'}\n")
            if rec is None:
                f.write("(원문을 찾지 못함)\n\n")
                continue
            for m in rec["messages"]:
                f.write(f"{m['sender']} : {m['text']}\n")
            f.write("\n")

    print(f"\n검토 목록 {len(picked)}개: {review_csv}")
    print(f"대화 원문: {review_txt}")
    print("원문을 읽고 review CSV의 selected 칸에 Y를 적은 뒤 export --csv review 로 내보내세요.")


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------

def cmd_export(args):
    out_dir = os.path.abspath(args.out)
    csv_name = f"{args.csv}_{args.split}.csv"
    csv_path = os.path.join(out_dir, csv_name)
    jsonl_path = os.path.join(out_dir, f"candidates_{args.split}.jsonl")
    if not os.path.isfile(jsonl_path):
        sys.exit(f"[오류] 파일이 없습니다: {jsonl_path}\n→ 먼저 scan을 실행하세요.")
    if not os.path.isfile(csv_path):
        hint = ("먼저 sample을 실행해 검토 목록을 만드세요." if args.csv == "review"
                else "먼저 scan을 실행하세요.")
        sys.exit(f"[오류] 파일이 없습니다: {csv_path}\n→ {hint}")

    rows = {r["candidate_id"].strip(): r for r in read_csv_rows(csv_path) if is_selected(r.get("selected"))}
    if not rows:
        sys.exit(f"[오류] {csv_name}의 selected 칸에 Y로 표시된 대화가 없습니다.")

    replay_dir = os.path.join(out_dir, f"replay_{args.split}")
    os.makedirs(replay_dir, exist_ok=True)
    recs = load_candidates(jsonl_path, set(rows))
    for cid, rec in recs.items():
        # 재생 형식: 첫 줄 = 메타, 이후 한 줄 = 메시지(알림) 하나
        path = os.path.join(replay_dir, f"{cid}.jsonl")
        with open(path, "w", encoding="utf-8") as fo:
            meta = {k: rec[k] for k in ("candidate_id", "split", "source_file",
                                         "platform", "speaker_type", "topic")}
            meta.update({"type": "meta", "label": "normal",
                         "senders": sorted({m["sender"] for m in rec["messages"]})})
            if rows[cid].get("bucket"):
                meta["bucket"] = rows[cid]["bucket"]
            fo.write(json.dumps(meta, ensure_ascii=False) + "\n")
            for seq, m in enumerate(rec["messages"], 1):
                fo.write(json.dumps({"type": "message", "seq": seq, "sender": m["sender"],
                                     "text": m["text"]}, ensure_ascii=False) + "\n")

    missing = set(rows) - set(recs)
    print(f"재생 파일 {len(recs)}개 저장: {replay_dir}")
    if missing:
        print(f"[경고] 고른 {len(missing)}개를 jsonl에서 찾지 못했습니다: {sorted(missing)[:10]}")


# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="AI Hub 일상 대화 데이터에서 일반 대화 후보 추출")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="후보 뽑기")
    s.add_argument("--data-root", required=True, help="Training/Validation 폴더가 있는 '01.데이터' 폴더")
    s.add_argument("--out", help="결과 폴더 (기본: data-root 옆 candidates_out)")
    s.add_argument("--split", choices=["training", "validation", "both"], default="both")
    s.add_argument("--topics", nargs="+", help=f"후보 주제 (기본: {DEFAULT_TOPICS})")
    s.add_argument("--min-messages", type=int, default=4, help="후보 구간의 최소 메시지 수 (기본 4)")
    s.add_argument("--allow-in-repo", action="store_true", help="출력 폴더가 git 저장소 안이어도 진행")
    s.set_defaults(func=cmd_scan)

    m = sub.add_parser("sample", help="묶음별 무작위 검토 목록 만들기")
    m.add_argument("--out", required=True, help="scan 결과 폴더")
    m.add_argument("--split", choices=["training", "validation"], default="validation")
    m.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"무작위 시드 (기본 {DEFAULT_SEED})")
    m.add_argument("--n-group", type=int, default=999, help="다자간 대화 개수 (기본: 전부)")
    m.add_argument("--n-money", type=int, default=50, help="금전·투자·외부이동·지원금 묶음 개수 (기본 50)")
    m.add_argument("--n-romance", type=int, default=25, help="연애/결혼+만남 묶음 개수 (기본 25)")
    m.add_argument("--n-topic", type=int, default=15, help="주제만 맞는 묶음 개수 (기본 15)")
    m.add_argument("--force", action="store_true", help="기존 review 파일을 덮어쓰기")
    m.set_defaults(func=cmd_sample)

    e = sub.add_parser("export", help="selected=Y 대화를 재생 형식으로 내보내기")
    e.add_argument("--out", required=True, help="scan 결과 폴더")
    e.add_argument("--split", choices=["training", "validation"], default="validation")
    e.add_argument("--csv", choices=["candidates", "review"], default="review",
                   help="어느 CSV의 selected 표시를 쓸지 (기본: review)")
    e.set_defaults(func=cmd_export)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
