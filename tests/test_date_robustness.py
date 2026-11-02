"""
Test date parsing robustness against all Streamlit st.date_input return permutations.
"""

import datetime

def parse_date_selection(date_selection, min_date, max_date):
    if isinstance(date_selection, (tuple, list)):
        if len(date_selection) == 2:
            start_date, end_date = date_selection
        elif len(date_selection) == 1:
            start_date = date_selection[0]
            end_date = date_selection[0]
        else:
            start_date = min_date
            end_date = max_date
    elif isinstance(date_selection, datetime.date):
        start_date = date_selection
        end_date = date_selection
    else:
        start_date = min_date
        end_date = max_date

    if start_date and end_date and start_date > end_date:
        start_date, end_date = end_date, start_date
        
    return start_date, end_date

def test_date_robustness():
    min_d = datetime.date(2016, 9, 4)
    max_d = datetime.date(2018, 10, 17)
    
    # 1. Normal 2-date range
    s, e = parse_date_selection((datetime.date(2017, 1, 1), datetime.date(2018, 8, 31)), min_d, max_d)
    assert s == datetime.date(2017, 1, 1) and e == datetime.date(2018, 8, 31)
    
    # 2. Single clicked date (user hasn't selected second date yet)
    s, e = parse_date_selection((datetime.date(2017, 5, 10),), min_d, max_d)
    assert s == datetime.date(2017, 5, 10) and e == datetime.date(2017, 5, 10)
    
    # 3. Reversed range
    s, e = parse_date_selection((datetime.date(2018, 1, 1), datetime.date(2017, 1, 1)), min_d, max_d)
    assert s == datetime.date(2017, 1, 1) and e == datetime.date(2018, 1, 1)
    
    # 4. Cleared selection
    s, e = parse_date_selection((), min_d, max_d)
    assert s == min_d and e == max_d
    
    # 5. Single date object
    s, e = parse_date_selection(datetime.date(2017, 12, 25), min_d, max_d)
    assert s == datetime.date(2017, 12, 25) and e == datetime.date(2017, 12, 25)
    
    # 6. None
    s, e = parse_date_selection(None, min_d, max_d)
    assert s == min_d and e == max_d
    
    print("[PASS] All 6 date parsing edge cases handled successfully with ZERO unpack errors!")

if __name__ == "__main__":
    test_date_robustness()

