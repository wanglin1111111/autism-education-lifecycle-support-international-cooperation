#!/usr/bin/env python3
"""autism-education-lifecycle-support-international-cooperation 技能验证脚本。

断言“产出=合规成立”而非“动作已执行”：
- GOOD 样例：含全部合规要素，且无违规 → exit 0
- BAD 样例：命中任一违规模式 → exit 1

退出码契约：0=通过，1=存在错误，2=文件错误。
"""
import re
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_FILE_ERROR = 2


def read_sample(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        print(f"文件不存在: {path}", file=sys.stderr)
        sys.exit(EXIT_FILE_ERROR)
    return p.read_text(encoding="utf-8")


GOOD_REQUIREMENTS = [
    ('孤独症|ASD', '缺少规范称谓（孤独症/ASD）'),
    ('脱敏|敏感个人信息|监护人.{0,4}(书面)?同意', '缺少儿童数据保护（脱敏+监护人同意）'),
    ('诊断.{0,10}(医疗机构|医院|医生)|教育评估', '缺少医教边界（诊断归医疗机构）'),
    ('循证|证据等级|负面清单', '缺少循证分级要求'),
    ('数据出境|三路径|标准合同|安全评估', '缺少国际合作数据出境核查'),
    ('gotchas|坑位|红线', '缺少 gotchas 坑位引用'),
]

BAD_VIOLATIONS = [
    ('(治愈|根治|摘帽|脱帽)', '命中违规：孤独症治愈/摘帽宣称'),
    ('(机构|学校|中心).{0,8}(可以|能|出具).{0,4}诊断', '命中违规：教育机构出诊断'),
    ('(公开|展示|放).{0,6}(儿童|孩子|学生).{0,10}(照片|姓名|视频|正脸)', '命中违规：未经同意公开儿童可识别信息'),
    ('辅助沟通', '命中违规：推荐已证伪的辅助沟通（FC）'),
    ('自闭儿|傻孩子|弱智|不正常', '命中违规：贬损性称谓'),
]


def find_violations(text: str) -> list:
    hits = []
    for pattern, msg in BAD_VIOLATIONS:
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(msg)
    return hits


def find_missing_good(text: str) -> list:
    missing = []
    for pattern, msg in GOOD_REQUIREMENTS:
        if not re.search(pattern, text, re.IGNORECASE):
            missing.append(msg)
    return missing


def main():
    if len(sys.argv) < 2:
        print("用法: validate.py <sample.md>", file=sys.stderr)
        sys.exit(EXIT_FILE_ERROR)

    sample_path = sys.argv[1]
    text = read_sample(sample_path)
    fname = Path(sample_path).name.lower()
    is_bad = "bad" in fname

    errors = []

    violations = find_violations(text)
    if is_bad:
        if not violations:
            errors.append("BAD 样例未命中任何已知违规模式（应至少命中一条）")
        else:
            errors.append(f"BAD 样例命中 {len(violations)} 条违规（预期失败）：{'; '.join(violations)}")
    else:
        if violations:
            errors.append(f"GOOD 样例命中违规（不应有）：{'; '.join(violations)}")
        missing = find_missing_good(text)
        errors.extend(missing)

    if errors:
        print(f"验证失败（{len(errors)} 项）：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    print("验证通过")
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
