"""本地形式校验与主文档汇编；不替代人工编辑或事实核查。"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
PARTS = [
    '01-世界与人物.md', '02-术语知识库.md', '03-品牌与业务素材.md',
    '04-组织生态.md', '05A-十篇重点大纲.md', '05B-品牌选题大纲.md',
    '05C-精英文化十题.md', '05D-Buddy人物线十题.md',
    '06-技法与规范.md', '07-目录与连续性.md',
]
texts = [(ROOT / '分卷' / name).read_text(encoding='utf-8') for name in PARTS]
terms = re.findall(r'^\|(\d{3})／[ABCD]\|', texts[1], re.M)
assert len(terms) >= 150 and len(terms) == len(set(terms))
outlines = '\n'.join(texts[4:8])
topics = re.findall(r'^## (\d{2})《(.*?)》', outlines, re.M)
assert len(topics) == 64 and len(dict(topics)) == 64
assert [int(n) for n, _ in topics] == list(range(1, 65))
lengths = []
for section in re.split(r'\n## (?=\d)', texts[4])[1:]:
    title = section.splitlines()[0]
    body = section.split('### 详细大纲\n', 1)[1]
    count = len(re.sub(r'\s', '', body))
    assert 800 <= count <= 1200, (title, count)
    lengths.append((title, count))
with (ROOT / '作品目录.csv').open(encoding='utf-8', newline='') as file:
    rows = list(csv.DictReader(file))
assert len(rows) == 64
assert [(row['id'], row['title']) for row in rows] == topics
for row in rows:
    values = list(map(int, row['scores'].split('-')))
    assert len(values) == 10 and all(1 <= x <= 5 for x in values)
    assert sum(values) == int(row['total']) >= 40
brands = Counter(row['brand'] for row in rows if row['track'] == '虚构行业案例')
assert len(brands) == 12 and all(value >= 3 for value in brands.values())

profiles = json.loads((ROOT / '人物档案.json').read_text(encoding='utf-8'))
assert profiles['company'] == {
    'zh': '宝劫集团', 'en': 'Pain & Growth', 'abbreviation': 'P&G',
    'fictional': True, 'slogan_en': 'Touching Lives, Improving KPIs.',
    'slogan_zh': '亲近生活，改善指标。',
}
names = [person['name'] for person in profiles['characters']]
assert len(names) == len(set(names))
assert set(['Gregor', 'David', 'Michael', 'Jessica', 'Kevin', 'Emily',
            'Ryan', 'Alex', 'Sophia', 'Chris', 'Olivia', 'Daniel']) <= set(names)
for name in names:
    assert re.fullmatch(r'[A-Z][a-z]+', name) and f'|{name}|' in texts[0]
people = {person['name']: person for person in profiles['characters']}
positions = profiles['positions']
assert profiles['version'] == '5.0'
assert profiles['series_present']['month'] == 66
assert profiles['series_present']['gregor_experience_years'] == 5.5
assert people['Gregor']['current_at_T66']['band'] == 'Band 2'
assert people['Gregor']['language_background']['score'] == 7.5
expected_schools = {
    'Gregor': 'Top 20', 'Michael': '北京大学', 'David': '清华大学',
    'Jessica': '复旦大学', 'Kevin': '上海交通大学', 'Emily': '北京大学',
    'Ryan': '浙江大学', 'Alex': '华中科技大学', 'Sophia': '清华大学',
    'Chris': '南京大学', 'Olivia': '广东外语外贸大学', 'Daniel': '商学院MBA',
}
for name, school in expected_schools.items():
    assert school in people[name]['education']['summary']
    assert people[name]['education']['fictional'] is True
for person in people.values():
    assert 'education' in person and person['education']['fictional'] is True
    assert person['ability_profile']['caused_by_school'] is False
assert profiles['education_policy']['school_does_not_determine_ability'] is True
assert people['Kevin']['reports_to_name'] == 'Aaron'
assert people['Emily']['reports_to_name'] == 'Claire'
for name in ['Michael', 'Aaron', 'Claire']:
    assert people[name]['band'] == 'Band 3'
    assert '北京大学' in people[name]['education']['summary']
new_rows = [row for row in rows if 45 <= int(row['id']) <= 54]
assert len(new_rows) == 10
assert len({row['mechanism'] for row in new_rows}) == 10
assert all(row['status'] == '已建大纲／未成稿' for row in new_rows)
buddy_rows = [row for row in rows if int(row['id']) >= 55]
assert len(buddy_rows) == 10
assert len({row['mechanism'] for row in buddy_rows}) == 10
assert profiles['buddy_arc']['shared_work_months'] == [4, 5, 6, 7]
assert profiles['buddy_arc']['formal_first_buddy_recipient'] == 'Leo'
assert profiles['buddy_arc']['first_formal_buddy_month'] == 27
assert profiles['buddy_arc']['active_help_begins_month'] == 25
assert people['Thomas']['coach_assignment']['is_gregor_line_manager'] is False
assert people['Thomas']['coach_assignment']['quote'] == 'Life is your priority.'
assert people['Gregor']['reports_to_name'] == 'Michael'
for name, month, manager in [('Emma', 60, 'Michael'), ('Lucas', 59, None),
                             ('Grace', 54, 'Claire'), ('Ethan', 65, 'Aaron')]:
    assert people[name]['joined_at'] == f'T{month}'
    assert people[name]['reports_to_name'] == manager
    assert people[name]['career_events'][0]['band'] == 'Band 1'
    assert people[name]['has_direct_reports'] is False
assert people['Grace']['current_at_T66']['band'] == 'Band 2'
assert (people['Michael']['band'], people['Michael']['title'],
        people['Michael']['reports_to_name']) == ('Band 3', 'Marketing Director', 'David')
assert (people['David']['band'], people['David']['title'],
        people['David']['reports_to_name']) == ('Band 4', 'Marketing VP', 'Daniel')
assert (people['Daniel']['band'], people['Daniel']['title']) == ('Band 5', 'Regional VP')
assert people['Olivia']['band'] == 'Band 2'
for name in ['Gregor', 'Chris']:
    assert people[name]['joined_at'] == 'T0'
    assert people[name]['career_events'][:2] == [
        {'month': 0, 'band': 'Band 1', 'title': 'Brand Manager'},
        {'month': 12, 'band': 'Band 2', 'title': 'Brand Manager'},
    ]
for person in people.values():
    if person['employment_type'] == '宝劫集团内部':
        assert person['band'] and person['title']
        position = person['reports_to_position']
        assert position in positions
        assert person['reports_to_name'] == positions[position]['incumbent']
        assert person['tenure_reference_month'] is not None
        assert person['tenure_years_at_reference'] >= 0
    else:
        assert person['band'] == '不适用（外部）'
for position in positions:
    seen = set()
    while position is not None:
        assert position not in seen, ('汇报线循环', position)
        seen.add(position)
        position = positions[position]['reports_to']
active = '\n'.join(texts) + (ROOT / '作品目录.csv').read_text(encoding='utf-8')
assert 'Hair Care' in people['Gregor']['department']
assert not any(phrase in active for phrase in ['David为Marketing Director',
              'Michael没有自动获得Director', 'Band 1，品牌助理', 'Band 1为项目执行岗'])
assert next(row for row in rows if row['id'] == '01')['time'] == 'T12'
section06 = next(section for section in re.split(r'\n## (?=\d)', texts[4])[1:]
                 if section.startswith('06'))
assert 'Michael' in section06 and 'David生日' not in section06
legacy_names = ['恒澜', '周禾', '陈岚', '叶祺', '许曼', '邵言', '罗宁',
                '孟梨', '沈卓', '丁棠', '温夏', '李默', '苏敏', '顾衡', '郑姨']
assert not any(name in active for name in legacy_names)
fiction = sorted((ROOT / '小说正文').glob('*.md'))
for path in fiction:
    text = path.read_text(encoding='utf-8')
    assert not any(name in text for name in legacy_names)
    assert not re.search(r'[张王李刘陈赵]经理|[张王李刘陈赵]总|[张王李刘陈赵]主管|小[刘王张李]', text)
    assert '*人物、公司及事件均属虚构。*\n' in text
    body = text.split('*人物、公司及事件均属虚构。*\n', 1)[1]
    count = len(re.sub(r'\s', '', body))
    assert 2000 <= count <= 3000, (path.name, count)
    card = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    # 已有作品保留写作时版本，不因人物档案升级而改写其编辑卡。
    assert card['world_version'] in ['0.3', '4.0', '4.1']
    assert count == card['body_characters']
    assert sum(card['scores']) == card['total_score']
    assert all(name in names for name in card['named_characters'])
    assert card['published'] is False and card['user_approved'] is False
    if card['id'] == '01':
        assert card['time'] == 'T12' and '待了两年' not in body
        assert '刚满一年' in body and 'Band 3 Director Michael' in body
        assert 'Marketing VP David' in body
    if card['id'] == '58':
        assert card['time'] == 'T95—T96'
        assert {'Gregor', 'Emma', 'Lucas', 'Grace', 'Michael', 'Thomas', 'Ethan'} <= set(card['named_characters'])
        assert body.count('If you need help, you can talk to Gregor.') == 1
        assert body.count('Life is your priority.') == 1
        assert card['body_characters'] == 2729
assert len(fiction) == sum('稿已写' in row['status'] for row in rows)
frozen = json.loads((ROOT / '历史版本' / 'V4.0-既有正文保护摘要.json').read_text(encoding='utf-8'))
for item in frozen:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
buddy_frozen = json.loads((ROOT / '历史版本' / 'V4.1-升级前正文保护摘要.json').read_text(encoding='utf-8'))
for item in buddy_frozen:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']

# 来源完整性及冻结正文：不能由这些断言推断人工阅读全文或风格通过。
source = ROOT / '原著' / '快消市场部变形记-原始上传.txt'
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
assert source_hash == '13e84a812c9978f06957840d8aaaa926efefada44eafc8cace06e437cae6810e'
assert len(source.read_bytes()) == 13079
frozen_v5 = json.loads((ROOT / '历史版本' / 'V5.0-既有正文保护摘要.json').read_text())
for item in frozen_v5:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
assert len(fiction) == 2
assert 'legacy_time' in rows[0]
assert 'T95' in next(row for row in rows if row['id'] == '58')['legacy_time']
assert next(row for row in rows if row['id'] == '53')['title'] == '优秀毕业生的第五年之后'
assert (ROOT / '职业时间线.md').exists()
intro = """# 甲虫文学｜快消职场荒诞小说创作圣经

版本：V5.0 · 原著风格与人物一致性修订 · 维护日期2026-10-16

本轮先完整阅读用户上传的《快消市场部变形记》八节，再修订创作规范。原著原样保存于原著目录，风格分析在下文；摘要和自动校验不能替代每次写作前阅读全文。

宝劫集团（Pain & Growth，P&G）为虚构雇主。Gregor现在时5年多，维护锚点T66；Marketing / Hair Care，Band 1 Manager入职、T12约一年升Band 2，Michael为Band 3 Director直属经理，David为Band 4 Marketing VP。人物姓名、学校、汇报关系见人物档案.json；学校不是性格或能力的判决。无新增Gregor晋升。

Gregor认真、有能力、虚荣且会犯错。他不只观察荒诞，还主动输出Corporate Buzzwords，并可能对自己的熟练感到满意。Thomas与Buddy线保留，以行为传递善意，继续使用原著一本正经的反讽，不转为励志文章。英文黑话须改变任务、决定、资源或责任。

原著开头五年后变形，第八节“第二年”有跨度歧义，已记录且不改原句；T66不是对原文精确月份的宣称。T60以前回溯不提前使用字面甲虫身体。E&I在原著为Exposure & Influence，不是Image；Growth Mindset、Critical Thinking、OGSM是允许扩展的表达，不能伪称来自原文。

保留156条表达、12品牌素材及64个选题；前10篇为详细大纲。45—54精英文化题、55—64 Buddy题继续维护。原著独立登记；两篇历史生成正文01和58未通过当前原著一致性检查，全部冻结保存。目录中的计划时间调整不等于旧正文已改。53更名《优秀毕业生的第五年之后》。本轮没有创作新小说。

新作2000—3000字且至少三个推动情节的场景；原著不按此长度目标删改。真实品牌仅作产品背景与虚构案例，不暗示真实品牌发生过小说事件。品牌信息未完成现场核验，不能将虚构学校分布、年龄、职级或制度当作真实宝洁事实。

维护源：原著风格与人物基准.md、职业时间线.md、人物档案.json、分卷及作品目录.csv。长期执行规则见仓库AGENTS.md；冲突与保护记录见V5.0-原著对照与修改记录.md。旧版本只作历史资料。

---

"""
baseline = (ROOT / '原著风格与人物基准.md').read_text(encoding='utf-8')
timeline = (ROOT / '职业时间线.md').read_text(encoding='utf-8')
master = intro + baseline + '\n\n---\n\n' + timeline + '\n\n---\n\n' + '\n\n---\n\n'.join(texts)
master = master.replace('(../作品目录.csv)', '(作品目录.csv)')
target = ROOT / '甲虫文学｜快消职场荒诞小说创作圣经.md'
target.write_text(master.rstrip() + '\n', encoding='utf-8')
print(f'术语{len(terms)}，选题{len(topics)}，品牌{len(brands)}；大纲字段与结构检查通过。')
print(f'原著SHA-256一致；冻结正文及其编辑卡／Word共{len(frozen_v5)}文件未变。')
print('五年多／T66、学历、Band及汇报线检查通过；两篇历史正文的已知冲突保留，不计作风格通过。')
print('文学风格须人工对照，自动校验不能代替完整阅读。')
print(f'已汇编：{target.name}（{len(master):,}字符）。')
