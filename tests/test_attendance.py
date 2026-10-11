from conftest import make_image

from presence import attendance, students


def test_open_today_marks_roster_absent_once():
    students.add("ada lovelace", make_image(120))
    students.add("Alan Turing", make_image(200))

    attendance.open_today()
    attendance.open_today()

    records = attendance.for_date(attendance.today())
    assert list(records["Name"]) == ["Ada Lovelace", "Alan Turing"]
    assert set(records["Status"]) == {attendance.ABSENT}


def test_mark_present_updates_existing_row_case_insensitively():
    students.add("Ada Lovelace", make_image(120))
    attendance.open_today()

    time, newly = attendance.mark_present("ada lovelace")
    assert newly

    records = attendance.for_date(attendance.today())
    assert len(records) == 1
    assert records.loc[0, "Status"] == attendance.PRESENT
    assert records.loc[0, "Time"] == time


def test_mark_present_twice_keeps_first_time():
    first, _ = attendance.mark_present("alice")
    again, newly = attendance.mark_present("alice")
    assert (again, newly) == (first, False)
    assert len(attendance.for_date(attendance.today())) == 1
