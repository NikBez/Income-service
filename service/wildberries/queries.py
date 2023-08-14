month_total_by_pvz_query = '''      
    with sub as (SELECT
        wp.id id,
        wp.title title,
        SUM(IIF(ww.from_date >= :start_date and DATE(ww.from_date, 'weekday 0') <= :end_date, ww.total,
            IIF(ww.from_date >= :start_date and ww.to_date > :end_date,  ROUND(ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(:end_date))), 2),
            IIF(ww.from_date < :start_date and ww.to_date <= :end_date,  ROUND(ww.total / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(ww.from_date))), 2),
            0)))) total, 
        SUM(IIF(ww.from_date >= :start_date and DATE(ww.from_date, 'weekday 0') <= :end_date, ww.total_charge,
            IIF(ww.from_date >= :start_date and ww.to_date > :end_date,  ROUND(ww.total_charge / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(:end_date))), 2),
            IIF(ww.from_date < :start_date and ww.to_date <= :end_date,  ROUND(ww.total_charge / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(ww.from_date))), 2),
            0)))) charged,
        SUM(IIF(ww.from_date >= :start_date and DATE(ww.from_date, 'weekday 0') <= :end_date, ww.total_hold,
            IIF(ww.from_date >= :start_date and ww.to_date > :end_date,  ROUND(ww.total_hold / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(:end_date))), 2),
            IIF(ww.from_date < :start_date and ww.to_date <= :end_date,  ROUND(ww.total_hold / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(ww.from_date))), 2),
            0)))) holded,	    
        SUM(IIF(pp.start_of_month = JULIANDAY(:start_date) and pp.end_of_week <= JULIANDAY(:end_date), COALESCE(pp.boxes, 0),
            IIF(pp.start_of_week >= JULIANDAY(:start_date) and pp.end_of_week > JULIANDAY(:end_date), CAST(CAST(pp.boxes AS REAL) / 7 * (7 - (JULIANDAY(pp.end_of_week) - JULIANDAY(:end_date))) AS INTEGER),   
            IIF(pp.start_of_week < JULIANDAY(:start_date) and pp.end_of_week <= JULIANDAY(:end_date), CAST(CAST(pp.boxes AS REAL) / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(pp.start_of_week))) AS INTEGER),
            0)))) boxes
        FROM
            wildberries_pvz wp 
        join (
            SELECT 
                pp.pvz_id_id id,
                pp.boxes_count boxes, 
                pp.date as date,
                JULIANDAY(date(date(pp.date,'weekday 1'),'start of month')) start_of_month,
                JULIANDAY(date(pp.date,'weekday 1')) start_of_week,
                JULIANDAY(date(pp.date,'weekday 0')) end_of_week
            FROM 
                wildberries_pvzpaiment pp) pp ON
            wp.id = pp.id 
        left join wildberries_wbpayment ww ON
            ww.pvz_id_id = wp.id
        WHERE
            (ww.from_date >= :start_date and ww.from_date <= :end_date) or (ww.to_date >= :start_date and ww.to_date <= :end_date) or 
            (start_of_week >= JULIANDAY(:start_date) and start_of_week <= JULIANDAY(:end_date)) or (end_of_week >= JULIANDAY(:start_date) and end_of_week <= JULIANDAY(:end_date)) 
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
    SUM(IIF(ww.from_date >= :start_date and DATE(ww.from_date, 'weekday 0') <= :end_date, ww.total,
            IIF(ww.from_date >= :start_date and ww.to_date > :end_date,  ROUND(ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(:end_date))), 2),
            IIF(ww.from_date < :start_date and ww.to_date <= :end_date,  ROUND(ww.total / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(ww.from_date))), 2),
            0)))) income
    from wildberries_wbpayment ww 
    WHERE (ww.from_date >= :start_date and ww.from_date <= :end_date) or (ww.to_date >= :start_date and ww.to_date <= :end_date)
    ),
    outcomes as (
     SELECT 
        SUM(IIF(pp.start_of_month = JULIANDAY(:start_date) and pp.end_of_week <= JULIANDAY(:end_date), pp.total,
                IIF(pp.start_of_week >= JULIANDAY(:start_date) and pp.end_of_week > JULIANDAY(:end_date),  ROUND(pp.total / 7 * (7 - (JULIANDAY(pp.end_of_week) - JULIANDAY(:end_date))), 2),   
                IIF(pp.start_of_week < JULIANDAY(:start_date) and pp.end_of_week <= JULIANDAY(:end_date),  ROUND(pp.total / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(pp.start_of_week))), 2),
                0)))) outcome
    FROM (
        SELECT  
            pp.total, 
            pp.date as date,
            JULIANDAY(date(date(pp.date,'weekday 1'),'start of month')) start_of_month,
            JULIANDAY(date(pp.date,'weekday 1')) start_of_week,
            JULIANDAY(date(pp.date,'weekday 0')) end_of_week
        FROM 
            wildberries_pvzpaiment pp) pp 
    WHERE (pp.start_of_week >= JULIANDAY(:start_date) and pp.start_of_week <= JULIANDAY(:end_date)) or (pp.end_of_week >= JULIANDAY(:start_date) and pp.end_of_week <= JULIANDAY(:end_date))
    )
    Select 
    ROUND(o.outcome, 2) salaryes,
    ROUND(i.income * 0.94 - o.outcome, 2) profit,
    ROUND(i.income * 0.06, 2) taxes 
    From 
    incomes i CROSS JOIN outcomes o;
'''
