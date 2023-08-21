month_total_by_pvz_query = '''      
               with sub as (SELECT
        wp.id id,
        wp.title title, 
        ww.total,
        ww.charge,
        ww.holded,
        COALESCE(pp.boxes, 0) boxes
    FROM
        wildberries_pvz wp
    left join (
        SELECT 
            sub_pp.id,
            SUM(IIF(sub_pp.start_of_month = JULIANDAY(:start_date) and sub_pp.end_of_week <= JULIANDAY(:end_date), COALESCE(sub_pp.boxes, 0),
                    IIF(sub_pp.start_of_week >= JULIANDAY(:start_date) and sub_pp.end_of_week > JULIANDAY(:end_date), CAST(CAST(sub_pp.boxes AS REAL) / 7 * (7 - (sub_pp.end_of_week - JULIANDAY(:end_date))) AS INTEGER),   
                    IIF(sub_pp.start_of_week < JULIANDAY(:start_date) and sub_pp.end_of_week <= JULIANDAY(:end_date), CAST(CAST(sub_pp.boxes AS REAL) / 7 * (7 - (JULIANDAY(:start_date) - sub_pp.start_of_week)) AS INTEGER),
                    0)))) boxes
        FROM (SELECT 
                pp.pvz_id_id id,
                pp.boxes_count boxes, 
                pp.date as date,
                JULIANDAY(date(date(pp.date,'weekday 1'),'start of month')) start_of_month,
                JULIANDAY(date(pp.date,'weekday 1')) start_of_week,
                JULIANDAY(date(pp.date,'weekday 0')) end_of_week
            FROM 
                wildberries_pvzpaiment pp
            WHERE JULIANDAY((date(pp.date,'weekday 1')) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date)) or (JULIANDAY(date(pp.date,'weekday 0')) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date)) ) sub_pp
        GROUP BY sub_pp.id
         ) pp ON
        wp.id = pp.id 
    left join (SELECT 
        ww.pvz_id_id id,
        SUM(IIF(JULIANDAY(ww.from_date) >= JULIANDAY(:start_date) and JULIANDAY(DATE(ww.from_date, 'weekday 0')) <= JULIANDAY(:end_date), ww.total,
            IIF(JULIANDAY(ww.from_date) >= JULIANDAY(:start_date) and JULIANDAY(ww.to_date) > JULIANDAY(:end_date),  ROUND(ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(:end_date))), 2),
            IIF(JULIANDAY(ww.from_date) < JULIANDAY(:start_date) and JULIANDAY(ww.to_date) <= JULIANDAY(:end_date),  ROUND(ww.total / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(ww.from_date))), 2),
            0)))) total, 
        SUM(IIF(JULIANDAY(ww.from_date) >= JULIANDAY(:start_date) and JULIANDAY(DATE(ww.from_date, 'weekday 0')) <= JULIANDAY(:end_date), ww.total_charge,
            IIF(JULIANDAY(ww.from_date) >= JULIANDAY(:start_date) and JULIANDAY(ww.to_date) > JULIANDAY(:end_date),  ROUND(ww.total_charge / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(:end_date))), 2),
            IIF(JULIANDAY(ww.from_date) < JULIANDAY(:start_date) and JULIANDAY(ww.to_date) <= JULIANDAY(:end_date),  ROUND(ww.total_charge / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(ww.from_date))), 2),
            0)))) charge,
        SUM(IIF(JULIANDAY(ww.from_date) >= JULIANDAY(:start_date) and JULIANDAY(DATE(ww.from_date, 'weekday 0')) <= JULIANDAY(:end_date), ww.total_hold,
            IIF(JULIANDAY(ww.from_date) >= JULIANDAY(:start_date) and JULIANDAY(ww.to_date) > JULIANDAY(:end_date),  ROUND(ww.total_hold / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(:end_date))), 2),
            IIF(JULIANDAY(ww.from_date) < JULIANDAY(:start_date) and JULIANDAY(ww.to_date) <= JULIANDAY(:end_date),  ROUND(ww.total_hold / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(ww.from_date))), 2),
            0)))) holded
        FROM wildberries_wbpayment ww
        WHERE (JULIANDAY(ww.from_date) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date)) or (JULIANDAY(ww.to_date) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date))
        GROUP BY ww.pvz_id_id
        ) ww ON
        wp.id = ww.id)
    SELECT 
                wp.id id,
                wp.title title,
                COALESCE(sub.total, 0) total,
                COALESCE(sub.charge, 0) charged,
                COALESCE(sub.holded, 0) holded,
                COALESCE(sub.boxes, 0) boxes
            FROM wildberries_pvz wp 
            LEFT JOIN sub ON wp.id = sub.id
            ORDER BY title
'''


def month_total_constructor(filter):
    if not filter:
        where_ww = '''WHERE (ww.from_date >= :start_date and ww.from_date <= :end_date) or (ww.to_date >= :start_date and ww.to_date <= :end_date)),'''
        where_pp = ''
        rent = 'SELECT COALESCE(SUM(rent_price), 0) rent FROM wildberries_pvz'
    else:
        filter = '(' + filter + ')'
        where_ww = f'''WHERE ((ww.from_date >= :start_date and ww.from_date <= :end_date) or (ww.to_date >= :start_date and ww.to_date <= :end_date)) and ww.pvz_id_id IN {filter}),'''
        where_pp = f''' WHERE pp.pvz_id_id IN {filter}'''
        rent = f'SELECT COALESCE(SUM(rent_price), 0) rent FROM wildberries_pvz WHERE id IN {filter}'

    month_total_query = f'''
    with incomes as (
        SELECT 
        COALESCE(SUM(IIF(ww.from_date >= :start_date and DATE(ww.from_date, 'weekday 0') <= :end_date, ww.total,
                IIF(ww.from_date >= :start_date and ww.to_date > :end_date,  ROUND(ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(:end_date))), 2),
                IIF(ww.from_date < :start_date and ww.to_date <= :end_date,  ROUND(ww.total / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(ww.from_date))), 2),
                0)))), 0) income
        FROM wildberries_wbpayment ww ''' + where_ww + ''' outcomes as (
        SELECT 
            COALESCE(SUM(IIF(pp.start_of_month = JULIANDAY(:start_date) and pp.end_of_week <= JULIANDAY(:end_date), pp.total,
                    IIF(pp.start_of_week >= JULIANDAY(:start_date) and pp.end_of_week > JULIANDAY(:end_date),  ROUND(pp.total / 7 * (7 - (JULIANDAY(pp.end_of_week) - JULIANDAY(:end_date))), 2),   
                    IIF(pp.start_of_week < JULIANDAY(:start_date) and pp.end_of_week <= JULIANDAY(:end_date),  ROUND(pp.total / 7 * (7 - (JULIANDAY(:start_date) - JULIANDAY(pp.start_of_week))), 2),
                    0)))), 0) outcome
        FROM (
            SELECT 
                pp.pvz_id_id pvz_id_id, 
                pp.total, 
                pp.date as date,
                JULIANDAY(date(date(pp.date,'weekday 1'),'start of month')) start_of_month,
                JULIANDAY(date(pp.date,'weekday 1')) start_of_week,
                JULIANDAY(date(pp.date,'weekday 0')) end_of_week
            FROM 
                wildberries_pvzpaiment pp ''' + where_pp + ''' 
            ) pp 
            WHERE (pp.start_of_week >= JULIANDAY(:start_date) and pp.start_of_week <= JULIANDAY(:end_date)) or (pp.end_of_week >= JULIANDAY(:start_date) and pp.end_of_week <= JULIANDAY(:end_date))
            ),
            pvz as (''' + rent + ''')
            SELECT 
                ROUND(o.outcome, 2) salaryes,
                ROUND(i.income * 0.94 - o.outcome - p.rent, 2) profit,
                ROUND(i.income * 0.06, 2) taxes,
                p.rent rent
                From 
                incomes i CROSS JOIN outcomes o CROSS JOIN pvz p;
    '''
    return month_total_query


week_total_by_pvz_query = '''      
        WITH pp AS(
        SELECT
                pvz_id_id id,	
                COALESCE(SUM(add_penalty), 0) add_penalty,
                COALESCE(SUM(surcharge_penalty), 0) sub_penalty,
                COALESCE(SUM(total), 0) salary,
                COALESCE(SUM(boxes_count), 0) boxes
        FROM
            wildberries_pvzpaiment pp
        WHERE
            pvz_id_id = :pvz_id
            and JULIANDAY(pp.date) >= JULIANDAY(:start_date)
            and JULIANDAY(pp.date) <= JULIANDAY(:end_date)
        GROUP BY
                pp.pvz_id_id
            ), 
            ww AS (
        SELECT 
             pvz_id_id id,
             COALESCE(SUM(total), 0) total,
             COALESCE(SUM(total_charge), 0) charged,
             COALESCE(SUM(total_hold), 0) holded
        FROM 
            wildberries_wbpayment ww
        WHERE
            pvz_id_id = :pvz_id
            and JULIANDAY(ww.from_date) >= JULIANDAY(:start_date)
            and JULIANDAY(ww.from_date) <= JULIANDAY(:end_date)
        GROUP BY
                ww.pvz_id_id)
            SELECT 
            wp.id id, 
            wp.title title,
            COALESCE(wp.rent_price, 0) rent_price,
            COALESCE(pp.add_penalty, 0) add_penalty,
            COALESCE(pp.sub_penalty, 0) sub_penalty,
            COALESCE(pp.salary, 0) salary,
            COALESCE(pp.boxes, 0) boxes,
            COALESCE(ww.total, 0) income,
            COALESCE(ww.charged, 0) charged,
            COALESCE(ww.holded, 0) holded,
            COALESCE(ROUND(ww.total * 0.94 - IIF(pp.salary is Null, 0, pp.salary) - (wp.rent_price / 4), 2), 0) profit,
	        COALESCE(ROUND(ww.total * 0.06, 2), 0) taxes
        FROM
            wildberries_pvz wp
        LEFT JOIN pp ON
            wp.id = pp.id
        LEFT JOIN ww ON
            wp.id = ww.id
        WHERE wp.id = :pvz_id
'''

week_employee_report = '''  
    with sub as (SELECT * FROM wildberries_pvzpaiment pp
    WHERE JULIANDAY(pp.date) >= JULIANDAY(:start_date) and JULIANDAY(pp.date) <= JULIANDAY(:end_date)
    )
    SELECT 
    we.id id,
    we.name name,
    we.salary salary,
    we.penalty penalty,
    COALESCE(SUM(sub.number_days), 0) days,
    COALESCE(SUM(sub.extra_payment), 0) extra,
    COALESCE(SUM(sub.add_penalty), 0) add_penalty,
    COALESCE(SUM(sub.surcharge_penalty), 0) surcharge_penalty,
    COALESCE(SUM(sub.total), 0) total,
    COALESCE(SUM(sub.boxes_count), 0) boxes
    from wildberries_employee we LEFT JOIN sub ON we.id = sub.employee_id_id 
    WHERE we.pvz_id_id = :pvz_id
    GROUP BY we.id
    ORDER BY total DESC 
'''

pvz_outcomes_report = '''

'''
