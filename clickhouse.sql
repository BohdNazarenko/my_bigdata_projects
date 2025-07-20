--Create table with interval delete 30 days
CREATE OR REPLACE TABLE user_events
(
    user_id     UInt32,
    event_type  String,
    point_spent UInt32,
    event_time  DATETIME
) ENGINE = MergeTree()
ORDER BY (event_time, user_id)
TTL event_time + INTERVAL 30 DAY DELETE;

-----------------------------------------------------------------------------------
--Create table for daily users metrics
CREATE TABLE daily_user_metrics
(
    event_type          String,
    event_date          Date,
    unique_spend        AggregateFunction(uniqExact(), UInt32),
    points_spent_state  AggregateFunction(sum(), UInt64),
    total_actions       AggregateFunction(count(), UInt32)
)
ENGINE = AggregatingMergeTree()
ORDER BY (event_type, event_date)
TTL event_date + INTERVAL 180 DAY DELETE;

----------------------------------------------------------------------------------
--Create MV
CREATE MATERIALIZED VIEW mv_daily_user_metrics
TO daily_user_metrics AS
    SELECT
        toDate(event_time)              AS event_date,
        event_type,
        uniqExactState(user_id)         AS unique_spend,
        sumState(toUInt64(point_spent)) AS points_spent_state,
        countState()                    AS total_actions
    FROM user_events
GROUP BY event_date, event_type;

---------------------------------------------------------------------------------
--Database query for fast analise
SELECT
    event_date,
    event_type,
    uniqExactMerge(unique_spend)   AS unique_users,
    sumMerge(points_spent_state)   AS total_spent,
    countMerge(total_actions)      AS total_actions
FROM daily_user_metrics
GROUP BY
    event_date,
    event_type
ORDER BY
    event_date,
    event_type;

---------------------------------------------------------------------------------
--Retention query (I decided to write small queries because I wanted to minimalize code because of retention_7d_percent data)

WITH
    first_users_active AS
        (
            SELECT
                user_id,
                min(toDate(event_time)) AS first_user_day
            FROM user_events
            GROUP BY user_id
        ),

    total_users_day_0 AS
        (
            SELECT uniqExact(user_id)
            FROM first_users_active
        ),

    returned_in_7_days AS
        (
            SELECT
            uniqExact(ue.user_id) AS seven_days
        FROM user_events AS ue
        INNER JOIN first_users_active f USING (user_id)
        WHERE  toDate(ue.event_time) >  f.first_user_day
          AND  toDate(ue.event_time) <= f.first_user_day + 7
      )

    SELECT
        (SELECT * FROM total_users_day_0) AS total_users_day_0,
        (SELECT * FROM returned_in_7_days) AS returned_in_7_days,
        round(returned_in_7_days / total_users_day_0 * 100, 2) AS retention_7d_percent;