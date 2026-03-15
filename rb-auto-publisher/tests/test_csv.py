from pathlib import Path

from publisher.io_csv import load_designs


def test_load_designs(tmp_path: Path):
    csv_path = tmp_path / 'designs.csv'
    csv_path.write_text(
        'file_path,title,description,tags,maturity,is_public,default_status\n'
        '/tmp/a.png,T,D,"x,y",safe,true,draft\n',
        encoding='utf-8',
    )
    rows = load_designs(csv_path)
    assert len(rows) == 1
    assert rows[0].title == 'T'
    assert rows[0].is_public is True
