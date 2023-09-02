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
                JULIANDAY(date(date(pp.date,'weekday 0', '-6 days'),'start of month')) start_of_month,
                JULIANDAY(date(pp.date,'weekday 0', '-6 days')) start_of_week,
                JULIANDAY(date(pp.date,'weekday 0')) end_of_week
            FROM 
                wildberries_pvzpaiment pp
            WHERE JULIANDAY((date(pp.date,'weekday 0', '-6 days')) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date)) or (JULIANDAY(date(pp.date,'weekday 0')) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date)) ) sub_pp
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
        service = 'SELECT COALESCE(SUM(sum), 0) service FROM wildberries_pvzoutcomes wp WHERE JULIANDAY(wp.date) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date)'
    else:
        filter = '(' + filter + ')'
        where_ww = f'''WHERE ((ww.from_date >= :start_date and ww.from_date <= :end_date) or (ww.to_date >= :start_date and ww.to_date <= :end_date)) and ww.pvz_id_id IN {filter}),'''
        where_pp = f''' WHERE pp.pvz_id_id IN {filter}'''
        rent = f'SELECT COALESCE(SUM(rent_price), 0) rent FROM wildberries_pvz WHERE id IN {filter}'
        service = f'SELECT COALESCE(SUM(sum), 0) service FROM wildberries_pvzoutcomes wp WHERE wp.pvz_id IN {filter} and JULIANDAY(wp.date) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date)'


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
                JULIANDAY(date(date(pp.date,'weekday 0', '-6 days'),'start of month')) start_of_month,
                JULIANDAY(date(pp.date,'weekday 0', '-6 days')) start_of_week,
                JULIANDAY(date(pp.date,'weekday 0')) end_of_week
            FROM 
                wildberries_pvzpaiment pp ''' + where_pp + ''' 
            ) pp 
            WHERE (pp.start_of_week >= JULIANDAY(:start_date) and pp.start_of_week <= JULIANDAY(:end_date)) or (pp.end_of_week >= JULIANDAY(:start_date) and pp.end_of_week <= JULIANDAY(:end_date))
            ),
            pvz as (''' + rent + '''),
            po as (''' + service + ''') 
            Select 
                ROUND(i.income, 2) income,
                ROUND(o.outcome, 2) salaryes,
                ROUND(i.income * 0.94 - o.outcome - p.rent - po.service, 2) profit,
                ROUND(i.income * 0.06, 2) taxes,
                p.rent rent,
                po.service service
            FROM 
            incomes i CROSS JOIN outcomes o CROSS JOIN pvz p CROSS JOIN po;
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
                ww.pvz_id_id),
        po AS (
        SELECT
            po.pvz_id pvz_id,
            COALESCE(SUM(sum), 0) total_outcome
        FROM 
            wildberries_pvzoutcomes po
        WHERE 
            pvz_id = :pvz_id AND JULIANDAY(date) BETWEEN JULIANDAY(:start_date) AND JULIANDAY(:end_date)
        )
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
            COALESCE(ROUND(ww.total * 0.94 - IIF(pp.salary is Null, 0, pp.salary) - (wp.rent_price / 4) - IIF(po.total_outcome is Null, 0, po.total_outcome), 2), 0) profit,
	        COALESCE(ROUND(ww.total * 0.06, 2), 0) taxes,
	        COALESCE(po.total_outcome, 0) total_outcome
        FROM
            wildberries_pvz wp
        LEFT JOIN pp ON
            wp.id = pp.id
        LEFT JOIN ww ON
            wp.id = ww.id
        LEFT JOIN po ON
            wp.id = po.pvz_id  
        WHERE wp.id = :pvz_id
'''

week_employee_report = '''  
   with sub as (
    SELECT 
        pp.employee_id_id employee_id,
        COALESCE(SUM(total), 0) to_pay
    FROM wildberries_pvzpaiment pp
    WHERE JULIANDAY(pp.date) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date) and pp.pvz_id_id = :pvz_id and is_closed=False
    GROUP BY pp.employee_id_id 
    )
    SELECT
        we.id id,
        we.name name,
        COALESCE(we.salary, 0) salary,
        we.penalty penalty,
        pp.days days, 
        pp.extra extra, 
        pp.add_penalty add_penalty, 
        pp.surcharge_penalty surcharge_penalty, 
        pp.boxes boxes,
        pp.total - IIF(sub.to_pay is NULL, 0, sub.to_pay) payed, 
        COALESCE(sub.to_pay, 0) to_pay,
        pp.total total
    FROM wildberries_employee we LEFT JOIN (
        SELECT 
            pp.employee_id_id,
            COALESCE(SUM(pp.number_days), 0) days, 
            COALESCE(SUM(pp.extra_payment), 0) extra, 
            COALESCE(SUM(pp.add_penalty), 0) add_penalty, 
            COALESCE(SUM(pp.surcharge_penalty), 0) surcharge_penalty, 
            COALESCE(SUM(pp.boxes_count), 0) boxes,
            COALESCE(SUM(pp.total), 0) total
        FROM wildberries_pvzpaiment pp
        WHERE JULIANDAY(pp.date) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date) and pp.pvz_id_id = :pvz_id
        GROUP BY pp.employee_id_id 
    ) pp ON we.id = pp.employee_id_id LEFT JOIN sub ON we.id=sub.employee_id 
    WHERE we.pvz_id_id = :pvz_id
'''

weekly_pvz_outcomes = '''
    SELECT 
        wc.title category, 
        SUM(po.sum) outcome,
        (SELECT SUM(sum) FROM wildberries_pvzoutcomes WHERE pvz_id = :pvz_id AND JULIANDAY(date) BETWEEN JULIANDAY(:start_date) AND JULIANDAY(:end_date)) total_outcome
    FROM 
        wildberries_pvzoutcomes po LEFT JOIN wildberries_category wc ON po.category_id = wc.id  
    WHERE 
        pvz_id = :pvz_id AND JULIANDAY(po.date) BETWEEN JULIANDAY(:start_date) and JULIANDAY(:end_date)
    GROUP BY 
        po.category_id
'''


def year_analitic_constructor_(filter):
    if not filter:
        query = f'''
        incomes AS (
		WITH A AS (
	        SELECT
	            date(from_date, 'start of month') month,
	            SUM(IIF(to_date < date(from_date, '+1 month', 'start of month'), total, 0))	total,
	            SUM(IIF(to_date < date(from_date, '+1 month', 'start of month'), total_hold, 0)) total_hold
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date <= date('now', '+1 month', 'start of month', '-1 day') or ww.to_date <= date('now', '+1 month', 'start of month', '-1 day'))
	        GROUP BY month
	       	UNION 
	        SELECT
	            date(ww.from_date, 'start of month') month,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day')))), 2), 0)) total,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total_hold / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day')))), 2), 0)) total_hold
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date < date('now', '+1 month', 'start of month') or ww.to_date < date('now', '+1 month', 'start of month'))
	        GROUP BY month
	        UNION
	        SELECT
	            date(ww.to_date, 'start of month') month,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total / 7 * (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day'))), 2), 0)) total,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total_hold / 7 * (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day'))), 2), 0)) total_hold
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date < date('now', '+1 month', 'start of month') or ww.to_date < date('now', '+1 month', 'start of month'))
	        GROUP BY month
	    	)
        SELECT
	        A.month month,
	        SUM(A.total) AS income,
	        SUM(A.total_hold) AS holded
        FROM A
        GROUP BY A.month
        ), salaries AS (
		WITH A AS(
			SELECT 
                pp.start_of_month month,
                COALESCE(SUM(IIF(pp.end_of_week < date(start_of_week, '+1 month', 'start of month'), pp.total, 0)),0) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				) pp
			WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
			UNION 
			SELECT 
					pp.start_of_month month,	
					SUM(IIF(pp.end_of_week >= date(pp.start_of_week, '+1 month', 'start of month'), ROUND(pp.total / 7 * (7 - (JULIANDAY(pp.end_of_week) - JULIANDAY(date(pp.start_of_week, '+1 month', 'start of month', '-1 day')))), 2), 0)) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				) pp
			WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
			UNION
			SELECT 
					date(pp.end_of_week, 'start of month') month,	
					SUM(IIF(pp.end_of_week >= date(pp.start_of_week, '+1 month', 'start of month'), ROUND(pp.total / 7 * (JULIANDAY(pp.end_of_week) - JULIANDAY(date(pp.start_of_week, '+1 month', 'start of month', '-1 day'))), 2), 0)) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				) pp
				WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
				)
		SELECT
			COALESCE(A.month, 0) month,
			SUM(A.total) AS salary
		FROM A
		GROUP BY month
        ),pvz AS (
            select
            COALESCE(SUM(rent_price),
            0) rent
            from
            wildberries_pvz
        ),
        service AS (
            SELECT
                date(date, 'start of month') month,
                COALESCE(SUM(sum), 0) service
            FROM
                wildberries_pvzoutcomes wp
            WHERE
                wp.date BETWEEN date('now', '+1 month', 'start of month', '-1 year') AND date('now', '+1 month', 'start of month', '-1 days')
            GROUP BY month
        )
        SELECT
            COALESCE(i.month, s.month) month,
            i.income,
            i.holded,
            s.salary,
            pvz.rent,
            COALESCE(se.service, 0) service,
            COALESCE(ROUND(i.income * 0.94 - IIF(s.salary IS NOT NULL, s.salary, 0) - pvz.rent - IIF(se.service IS NOT NULL, se.service, 0), 2), 0) profit
        FROM
            incomes i LEFT JOIN salaries s ON s.month = i.month LEFT JOIN pvz LEFT JOIN service se ON se.month = i.month 
'''
    else:
        filter = '(' + filter + ')'
        query = f'''
    WITH incomes AS (
		WITH A AS (
	        SELECT
	            date(from_date, 'start of month') month,
	            SUM(IIF(to_date < date(from_date, '+1 month', 'start of month'), total, 0))	total,
	            SUM(IIF(to_date < date(from_date, '+1 month', 'start of month'), total_hold, 0))	total_hold
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date <= date('now', '+1 month', 'start of month', '-1 day') or ww.to_date <= date('now', '+1 month', 'start of month', '-1 day')) AND ww.pvz_id_id IN {filter}
	        GROUP BY month
	       	UNION 
	        SELECT
	            date(ww.from_date, 'start of month') month,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day')))), 2), 0)) total,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total_hold / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day')))), 2), 0)) total_hold
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date < date('now', '+1 month', 'start of month') or ww.to_date < date('now', '+1 month', 'start of month')) AND ww.pvz_id_id IN {filter}
	        GROUP BY month
	        UNION
	        SELECT
	            date(ww.to_date, 'start of month') month,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total / 7 * (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day'))), 2), 0)) total,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total_hold / 7 * (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day'))), 2), 0)) total_hold
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date < date('now', '+1 month', 'start of month') or ww.to_date < date('now', '+1 month', 'start of month')) AND ww.pvz_id_id IN {filter}
	        GROUP BY month
	    	)
        SELECT
	        A.month month,
	        SUM(A.total) AS income,
	        SUM(A.total_hold) AS holded
        FROM A
        GROUP BY A.month
        ), salaries AS (
		WITH A AS(
			SELECT 
					pp.start_of_month month,
					COALESCE(SUM(IIF(pp.end_of_week < date(start_of_week, '+1 month', 'start of month'), pp.total, 0)),
				0) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				WHERE pp.pvz_id_id IN {filter}) pp
			WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
			UNION 
			SELECT 
					pp.start_of_month month,	
					SUM(IIF(pp.end_of_week >= date(pp.start_of_week, '+1 month', 'start of month'), ROUND(pp.total / 7 * (7 - (JULIANDAY(pp.end_of_week) - JULIANDAY(date(pp.start_of_week, '+1 month', 'start of month', '-1 day')))), 2), 0)) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				WHERE pp.pvz_id_id IN {filter}) pp
			WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
			UNION
			SELECT 
					date(pp.end_of_week, 'start of month') month,	
					SUM(IIF(pp.end_of_week >= date(pp.start_of_week, '+1 month', 'start of month'), ROUND(pp.total / 7 * (JULIANDAY(pp.end_of_week) - JULIANDAY(date(pp.start_of_week, '+1 month', 'start of month', '-1 day'))), 2), 0)) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				WHERE pp.pvz_id_id IN {filter}) pp
				WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
				)
		SELECT
			COALESCE(A.month, 0) month,
			SUM(A.total) AS salary
		FROM
			A
		GROUP BY month
),pvz AS (
select
	COALESCE(SUM(rent_price),
	0) rent
from
	wildberries_pvz where id IN {filter}
),
service AS (
SELECT
	date(date, 'start of month') month,
	COALESCE(SUM(sum),
	0) service
FROM
	wildberries_pvzoutcomes wp
WHERE
	wp.pvz_id IN {filter} and wp.date BETWEEN date('now', '+1 month', 'start of month', '-1 year') AND date('now', '+1 month', 'start of month', '-1 days')
GROUP BY
	month
)
SELECT
	COALESCE(i.month, s.month) month,
	i.income,
	i.holded,
	s.salary,
	pvz.rent,
	COALESCE(se.service, 0) service,
	COALESCE(ROUND(i.income * 0.94 - IIF(s.salary IS NOT NULL, s.salary, 0) - pvz.rent - IIF(se.service IS NOT NULL, se.service, 0), 2), 0) profit
FROM
	incomes i LEFT JOIN salaries s ON s.month = i.month LEFT JOIN pvz LEFT JOIN service se ON se.month = i.month 
'''
    return query



def year_analitic_constructor(filter):
    if not filter:
        query = f'''
        WITH incomes AS (
		WITH A AS (
	        SELECT
	            date(from_date, 'start of month') month,
	            SUM(IIF(to_date < date(from_date, '+1 month', 'start of month'), total, 0))	total,
	            SUM(IIF(to_date < date(from_date, '+1 month', 'start of month'), total_hold, 0)) holded
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date <= date('now', '+1 month', 'start of month', '-1 day') or ww.to_date <= date('now', '+1 month', 'start of month', '-1 day'))
	        GROUP BY month
	       	UNION 
	        SELECT
	            date(ww.from_date, 'start of month') month,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day')))), 2), 0)) total,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total_hold / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day')))), 2), 0)) holded
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date < date('now', '+1 month', 'start of month') or ww.to_date < date('now', '+1 month', 'start of month'))
	        GROUP BY month
	        UNION
	        SELECT
	            date(ww.to_date, 'start of month') month,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total / 7 * (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day'))), 2), 0)) total,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total_hold / 7 * (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day'))), 2), 0)) holded
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date < date('now', '+1 month', 'start of month') or ww.to_date < date('now', '+1 month', 'start of month'))
	        GROUP BY month
	    	)
        SELECT
	        A.month month,
	        SUM(A.total) AS income,
	        SUM(A.holded) AS holded
        FROM A
        GROUP BY A.month
        ), salaries AS (
		WITH A AS(
			SELECT 
					pp.start_of_month month,
					COALESCE(SUM(IIF(pp.end_of_week < date(start_of_week, '+1 month', 'start of month'), pp.total, 0)),0) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				) pp
			WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
			UNION 
			SELECT 
					pp.start_of_month month,	
					SUM(IIF(pp.end_of_week >= date(pp.start_of_week, '+1 month', 'start of month'), ROUND(pp.total / 7 * (7 - (JULIANDAY(pp.end_of_week) - JULIANDAY(date(pp.start_of_week, '+1 month', 'start of month', '-1 day')))), 2), 0)) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				) pp
			WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
			UNION
			SELECT 
					date(pp.end_of_week, 'start of month') month,	
					SUM(IIF(pp.end_of_week >= date(pp.start_of_week, '+1 month', 'start of month'), ROUND(pp.total / 7 * (JULIANDAY(pp.end_of_week) - JULIANDAY(date(pp.start_of_week, '+1 month', 'start of month', '-1 day'))), 2), 0)) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				) pp
				WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
				)
		SELECT
			COALESCE(A.month, 0) month,
			SUM(A.total) AS salary
		FROM A
		GROUP BY month
        ),pvz AS (
            select
            COALESCE(SUM(rent_price),
            0) rent
            from
            wildberries_pvz
        ),
        service AS (
            SELECT
                date(date, 'start of month') month,
                COALESCE(SUM(sum), 0) service
            FROM
                wildberries_pvzoutcomes wp
            WHERE
                wp.date BETWEEN date('now', '+1 month', 'start of month', '-1 year') AND date('now', '+1 month', 'start of month', '-1 days')
            GROUP BY month
        )
        SELECT
            COALESCE(i.month, s.month) month,
            i.income,
            i.holded,
            s.salary,
            pvz.rent,
            COALESCE(se.service, 0) service,
            COALESCE(ROUND(i.income * 0.94 - IIF(s.salary IS NOT NULL, s.salary, 0) - pvz.rent - IIF(se.service IS NOT NULL, se.service, 0), 2), 0) profit
        FROM
            incomes i LEFT JOIN salaries s ON s.month = i.month LEFT JOIN pvz LEFT JOIN service se ON se.month = i.month 
'''
    else:
        filter = '(' + filter + ')'
        query = f'''
    WITH incomes AS (
		WITH A AS (
	        SELECT
	            date(from_date, 'start of month') month,
	            SUM(IIF(to_date < date(from_date, '+1 month', 'start of month'), total, 0))	total,
	            SUM(IIF(to_date < date(from_date, '+1 month', 'start of month'), total_hold, 0)) holded
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date <= date('now', '+1 month', 'start of month', '-1 day') or ww.to_date <= date('now', '+1 month', 'start of month', '-1 day')) AND ww.pvz_id_id IN {filter}
	        GROUP BY month
	       	UNION 
	        SELECT
	            date(ww.from_date, 'start of month') month,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day')))), 2), 0)) total,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total_hold / 7 * (7 - (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day')))), 2), 0)) holded
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date < date('now', '+1 month', 'start of month') or ww.to_date < date('now', '+1 month', 'start of month')) AND ww.pvz_id_id IN {filter}
	        GROUP BY month
	        UNION
	        SELECT
	            date(ww.to_date, 'start of month') month,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total / 7 * (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day'))), 2), 0)) total,
	            SUM(IIF(ww.to_date >= date(ww.from_date, '+1 month', 'start of month'),  ROUND(ww.total_hold / 7 * (JULIANDAY(ww.to_date) - JULIANDAY(date(ww.from_date, '+1 month', 'start of month', '-1 day'))), 2), 0)) holded
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', '+1 month', 'start of month', '-1 year') or ww.to_date >= date('now', '+1 month', 'start of month', '-1 year')) and 
	            (ww.from_date < date('now', '+1 month', 'start of month') or ww.to_date < date('now', '+1 month', 'start of month')) AND ww.pvz_id_id IN {filter}
	        GROUP BY month
	    	)
        SELECT
	        A.month month,
	        SUM(A.total) AS income,
	        SUM(A.holded) AS holded
        FROM A
        GROUP BY A.month
        ), salaries AS (
		WITH A AS(
			SELECT 
					pp.start_of_month month,
					COALESCE(SUM(IIF(pp.end_of_week < date(start_of_week, '+1 month', 'start of month'), pp.total, 0)),
				0) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				WHERE pp.pvz_id_id IN {filter}) pp
			WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
			UNION 
			SELECT 
					pp.start_of_month month,	
					SUM(IIF(pp.end_of_week >= date(pp.start_of_week, '+1 month', 'start of month'), ROUND(pp.total / 7 * (7 - (JULIANDAY(pp.end_of_week) - JULIANDAY(date(pp.start_of_week, '+1 month', 'start of month', '-1 day')))), 2), 0)) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				WHERE pp.pvz_id_id IN {filter}) pp
			WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
			UNION
			SELECT 
					date(pp.end_of_week, 'start of month') month,	
					SUM(IIF(pp.end_of_week >= date(pp.start_of_week, '+1 month', 'start of month'), ROUND(pp.total / 7 * (JULIANDAY(pp.end_of_week) - JULIANDAY(date(pp.start_of_week, '+1 month', 'start of month', '-1 day'))), 2), 0)) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(date(pp.date, 'weekday 0', '-6 days'), 'start of month') start_of_month,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				WHERE pp.pvz_id_id IN {filter}) pp
				WHERE 
					(pp.start_of_week >= date('now', '+1 month', 'start of month', '-1 year')
					or pp.end_of_week >= date('now', '+1 month', 'start of month', '-1 year'))
					and 
					(pp.start_of_week < date('now', '+1 month', 'start of month')
						or pp.end_of_week < date('now', '+1 month', 'start of month'))
				GROUP BY
					month
				)
		SELECT
			COALESCE(A.month, 0) month,
			SUM(A.total) AS salary
		FROM
			A
		GROUP BY month
),pvz AS (
select
	COALESCE(SUM(rent_price),
	0) rent
from
	wildberries_pvz where id IN {filter}
),
service AS (
SELECT
	date(date, 'start of month') month,
	COALESCE(SUM(sum),
	0) service
FROM
	wildberries_pvzoutcomes wp
WHERE
	wp.pvz_id IN {filter} and wp.date BETWEEN date('now', '+1 month', 'start of month', '-1 year') AND date('now', '+1 month', 'start of month', '-1 days')
GROUP BY
	month
)
SELECT
	COALESCE(i.month, s.month) month,
	i.income,
	i.holded,
	s.salary,
	pvz.rent,
	COALESCE(se.service, 0) service,
	COALESCE(ROUND(i.income * 0.94 - IIF(s.salary IS NOT NULL, s.salary, 0) - pvz.rent - IIF(se.service IS NOT NULL, se.service, 0), 2), 0) profit
FROM
	incomes i LEFT JOIN salaries s ON s.month = i.month LEFT JOIN pvz LEFT JOIN service se ON se.month = i.month 
'''
    return query


def year_analitic_by_weeks(pvz_id):
    if not pvz_id:
        query = '''
            WITH incomes AS (
            WITH A AS (
                SELECT
                    date(from_date, 'weekday 0', '-6 days') week,
                    SUM(total) total,
                    SUM(total_hold) holded
                FROM 
                    wildberries_wbpayment ww
                WHERE 
                    (ww.from_date >= date('now', 'weekday 0', '-6 days', '-1 year') or ww.to_date >= date('now', 'weekday 0', '-6 days', '-1 year')) and 
                    (ww.from_date <= date('now', 'weekday 0') or ww.to_date <= date('now', 'weekday 0'))
                GROUP BY week
                )
            SELECT
                A.week week,
                SUM(A.total) AS income,
                SUM(A.holded) AS holded
            FROM A
            GROUP BY A.week
            ), salaries AS (
            WITH A AS(
                SELECT 
                        pp.start_of_week week,
                        COALESCE(SUM(pp.total),0) total
                FROM
                    (
                    SELECT
                        pp.pvz_id_id pvz_id_id,
                        pp.total, 
                        pp.date as date,
                        date(pp.date, 'weekday 0', '-6 days') start_of_week,
                        date(pp.date, 'weekday 0') end_of_week
                    FROM 
                            wildberries_pvzpaiment pp
                    ) pp
                WHERE 
                        (pp.start_of_week >= date('now', 'weekday 0', '-6 days', '-1 year') or pp.end_of_week >= date('now', 'weekday 0', '-6 days', '-1 year'))
                        and 
                        (pp.start_of_week <= date('now', 'weekday 0') or pp.end_of_week <= date('now', 'weekday 0'))
                GROUP BY
                    week
            )
            SELECT
                COALESCE(A.week, 0) week,
                SUM(A.total) AS salary
            FROM A
            GROUP BY week
            ),pvz AS (
                select
                COALESCE(SUM(rent_price/4), 0) rent
                from
                wildberries_pvz
            ),
            service AS (
                SELECT
                    date(date, 'weekday 0', '-6 days') week,
                    COALESCE(SUM(sum), 0) service
                FROM
                    wildberries_pvzoutcomes wp
                WHERE
                    wp.date BETWEEN date('now', 'weekday 0', '-6 days', '-1 year') AND date('now', 'weekday 0')
                GROUP BY week
            )
            SELECT
                strftime('%d.%m', COALESCE(i.week, s.week), '-7 days') || ' - ' || strftime('%d.%m', COALESCE(i.week, s.week)) AS week,
                i.income,
                i.holded,
                s.salary,
                pvz.rent,
                COALESCE(se.service, 0) service,
                COALESCE(ROUND(i.income * 0.94 - IIF(s.salary IS NOT NULL, s.salary, 0) - pvz.rent - IIF(se.service IS NOT NULL, se.service, 0), 2), 0) profit
            FROM
                incomes i LEFT JOIN salaries s ON s.week = i.week LEFT JOIN pvz LEFT JOIN service se ON se.week = i.week 
        '''
    else:
        pvz_id = '(' + pvz_id + ')'
        query = f'''
        WITH incomes AS (
		WITH A AS (
	        SELECT
	            date(from_date, 'weekday 0', '-6 days') week,
	            SUM(total) total,
	            SUM(total_hold) holded
	        FROM 
	            wildberries_wbpayment ww
	        WHERE 
	            (ww.from_date >= date('now', 'weekday 0', '-6 days', '-1 year') or ww.to_date >= date('now', 'weekday 0', '-6 days', '-1 year')) and 
	            (ww.from_date <= date('now', 'weekday 0') or ww.to_date <= date('now', 'weekday 0')) and ww.pvz_id_id == {pvz_id}
	        GROUP BY week
	    	)
        SELECT
	        A.week week,
	        SUM(A.total) AS income,
	        SUM(A.holded) AS holded
        FROM A
        GROUP BY A.week
        ), salaries AS (
		WITH A AS(
			SELECT 
					pp.start_of_week week,
					COALESCE(SUM(pp.total),0) total
			FROM
				(
				SELECT
                    pp.pvz_id_id pvz_id_id,
                    pp.total, 
                    pp.date as date,
                    date(pp.date, 'weekday 0', '-6 days') start_of_week,
                    date(pp.date, 'weekday 0') end_of_week
				FROM 
						wildberries_pvzpaiment pp
				WHERE pp.pvz_id_id == {pvz_id}
				) pp
			WHERE 
					(pp.start_of_week >= date('now', 'weekday 0', '-6 days', '-1 year') or pp.end_of_week >= date('now', 'weekday 0', '-6 days', '-1 year'))
					and 
					(pp.start_of_week <= date('now', 'weekday 0') or pp.end_of_week <= date('now', 'weekday 0'))
			GROUP BY
				week
		)
		SELECT
			COALESCE(A.week, 0) week,
			SUM(A.total) AS salary
		FROM A
		GROUP BY week
        ),pvz AS (
            select
            COALESCE(SUM(rent_price/4), 0) rent
            from
            wildberries_pvz
            WHERE id == {pvz_id}
        ),
        service AS (
            SELECT
                date(date, 'weekday 0', '-6 days') week,
                COALESCE(SUM(sum), 0) service
            FROM
                wildberries_pvzoutcomes wp
            WHERE
                wp.date BETWEEN date('now', 'weekday 0', '-6 days', '-1 year') AND date('now', 'weekday 0') AND wp.pvz_id == {pvz_id}
            GROUP BY week
        )
        SELECT
        	strftime('%d.%m', COALESCE(i.week, s.week), '-7 days') || ' - ' || strftime('%d.%m', COALESCE(i.week, s.week)) AS week,
            i.income,
            i.holded,
            s.salary,
            pvz.rent,
            COALESCE(se.service, 0) service,
            COALESCE(ROUND(i.income * 0.94 - IIF(s.salary IS NOT NULL, s.salary, 0) - pvz.rent - IIF(se.service IS NOT NULL, se.service, 0), 2), 0) profit
        FROM
            incomes i LEFT JOIN salaries s ON s.week = i.week LEFT JOIN pvz LEFT JOIN service se ON se.week = i.week 
        '''
    return query
