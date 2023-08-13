month_total_by_pvz_query = '''
    SELECT
        wp.id id,
        wp.title title,
        SUM(IIF(ww.from_date >= %s and DATE(ww.from_date, '+7 days') <= %s, ww.total,
            IIF(ww.from_date >= %s and ww.to_date > %s,  ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(%s))),
            IIF(ww.from_date < %s and ww.to_date <= %s,  ww.total / 7 * (7 - (JULIANDAY(%s) - JULIANDAY(ww.from_date))),
            0)))) total,
           
        SUM(IIF(ww.from_date >= %s and DATE(ww.from_date, '+7 days') <= %s, ww.total_charge,
            IIF(ww.from_date >= %s and ww.to_date > %s,  ww.total_charge / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(%s))),
            IIF(ww.from_date < %s and ww.to_date <= %s,  ww.total_charge / 7 * (7 - (JULIANDAY(%s) - JULIANDAY(ww.from_date))),
            0)))) charged,
        
        SUM(IIF(ww.from_date >= %s and DATE(ww.from_date, '+7 days') <= %s, ww.total_hold,
            IIF(ww.from_date >= %s and ww.to_date > %s,  ww.total_hold / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(%s))),
            IIF(ww.from_date < %s and ww.to_date <= %s,  ww.total_hold / 7 * (7 - (JULIANDAY(%s) - JULIANDAY(ww.from_date))),
            0)))) holded,
        
        SUM(IIF(ww.from_date >= %s and DATE(ww.from_date, '+7 days') <= %s, COALESCE(pp.count_big_boxes, 0),
            IIF(ww.from_date >= %s and ww.to_date > %s,  pp.count_big_boxes / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(%s))),
            IIF(ww.from_date < %s and ww.to_date <= %s,  pp.count_big_boxes / 7 * (7 - (JULIANDAY(%s) - JULIANDAY(ww.from_date))),
            0)))) boxes
    FROM
        wildberries_wbpayment ww
    join wildberries_pvz wp ON
        ww.pvz_id_id = wp.id
    left join wildberries_pvzpaiment pp ON
        pp.pvz_id_id = wp.id
    WHERE
        ww.from_date >= %s
        and ww.to_date <= %s
    GROUP BY
        wp.id, wp.title
'''