import streamlit as st

from presence import attendance


def _status_style(status: str) -> str:
    color = "#16a34a" if status == attendance.PRESENT else "#dc2626"
    return f"color: {color}; font-weight: 600"


def history_page() -> None:
    st.title("Attendance history")

    dates = attendance.dates()
    if not dates:
        st.info("No attendance recorded yet.")
        return

    date = st.selectbox("Date", dates)
    records = attendance.for_date(date)

    present = int((records["Status"] == attendance.PRESENT).sum())
    c1, c2 = st.columns(2)
    c1.metric("Present", present)
    c2.metric("Absent", len(records) - present)

    st.dataframe(
        records.style.map(_status_style, subset=["Status"]),
        hide_index=True,
        width="stretch",
    )
    st.download_button(
        "Download CSV",
        records.to_csv(index=False),
        file_name=f"attendance_{date}.csv",
        mime="text/csv",
    )
