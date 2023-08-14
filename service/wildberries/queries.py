month_total_by_pvz_query = '''      
        WITH sub AS (SELECT
            wp.id id,
            wp.title title,
            SUM(IIF(ww.from_date >= %s and DATE(ww.from_date, '+7 days') <= %s, ww.total,
                IIF(ww.from_date >= %s and ww.to_date > %s,  ROUND(ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(%s))), 2),
                IIF(ww.from_date < %s and ww.to_date <= %s,  ROUND(ww.total / 7 * (7 - (JULIANDAY(%s) - JULIANDAY(ww.from_date))), 2),
                0)))) total,
               
            SUM(IIF(ww.from_date >= %s and DATE(ww.from_date, '+7 days') <= %s, ww.total_charge,
                IIF(ww.from_date >= %s and ww.to_date > %s,  ROUND(ww.total_charge / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(%s))), 2),
                IIF(ww.from_date < %s and ww.to_date <= %s,  ROUND(ww.total_charge / 7 * (7 - (JULIANDAY(%s) - JULIANDAY(ww.from_date))), 2),
                0)))) charged,
            
            SUM(IIF(ww.from_date >= %s and DATE(ww.from_date, '+7 days') <= %s, ww.total_hold,
                IIF(ww.from_date >= %s and ww.to_date > %s,  ROUND(ww.total_hold / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(%s))), 2),
                IIF(ww.from_date < %s and ww.to_date <= %s,  ROUND(ww.total_hold / 7 * (7 - (JULIANDAY(%s) - JULIANDAY(ww.from_date))), 2),
                0)))) holded,
            
            SUM(IIF(pp.from_date >= %s and DATE(pp.from_date, '+7 days') <= %s, COALESCE(pp.count_big_boxes, 0),
                IIF(pp.from_date >= %s and pp.to_date > %s,  CAST(pp.count_big_boxes AS REAL) / 7 * (7 - (JULIANDAY(pp.to_date) - JULIANDAY(%s))),
                IIF(pp.from_date < %s and pp.to_date <= %s,  CAST(pp.count_big_boxes AS REAL) / 7 * (7 - (JULIANDAY(%s) - JULIANDAY(pp.from_date))),
                0)))) boxes
        FROM
            wildberries_pvz wp
        join wildberries_pvzpaiment pp ON
            wp.id = pp.pvz_id_id 
        left join wildberries_wbpayment ww ON
            ww.pvz_id_id = wp.id
        WHERE
            (ww.from_date >= %s and ww.from_date <= %s) or (ww.to_date >= %s and ww.to_date <= %s) or 
            (pp.from_date >= %s and pp.from_date <= %s) or (pp.to_date >= %s and pp.to_date <= %s)
        GROUP BY
            wp.id, wp.title)
        SELECT 
            wp.id id,
            wp.title title,
            COALESCE(sub.total, 0) total,
            COALESCE(sub.charged, 0) charged,
            COALESCE(sub.holded, 0) holded,
            COALESCE(sub.boxes, 0) boxes
        FROM wildberries_pvz wp 
        LEFT JOIN sub ON wp.id = sub.id
        ORDER BY title
'''

month_total_query = '''
    with incomes as (
    Select 
    SUM(IIF(ww.from_date >= %s and DATE(ww.from_date, '+7 days') <= %s, ww.total,
        IIF(ww.from_date >= %s and ww.to_date > %s,  ROUND(ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(%s))), 2),
        IIF(ww.from_date < %s and ww.to_date <= %s,  ROUND(ww.total / 7 * (7 - (JULIANDAY(%s) - JULIANDAY(ww.from_date))), 2),
        0)))) income
    from wildberries_wbpayment ww 
    WHERE (ww.from_date >= %s and ww.from_date <= %s) or (ww.to_date >= %s and ww.to_date <= %s)
    ),
    outcomes as (
    SELECT 
    SUM(IIF(wp.from_date >= %s and DATE(wp.from_date, '+7 days') <= %s, wp.total,
        IIF(wp.from_date >= %s and wp.to_date > %s,  ROUND(wp.total / 7 * (7 - (JULIANDAY(wp.to_date) - JULIANDAY(%s))), 2),
        IIF(wp.from_date < %s and wp.to_date <= %s,  ROUND(wp.total / 7 * (7 - (JULIANDAY(%s) - JULIANDAY(wp.from_date))), 2),
        0)))) outcome
    FROM wildberries_pvzpaiment wp 
    WHERE (wp.from_date >= %s and wp.from_date <= %s) or (wp.to_date >= %s and wp.to_date <= %s)
    )
    Select 
    ROUND(o.outcome, 2) salaryes,
    ROUND(i.income * 0.94 - o.outcome, 2) profit,
    ROUND(i.income * 0.06, 2) taxes
    From 
    incomes i CROSS JOIN outcomes o;
'''