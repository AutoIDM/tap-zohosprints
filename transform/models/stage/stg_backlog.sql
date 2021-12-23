with source as (
    SELECT
backlogid::varchar backlog_id,
myteamid::varchar my_team_id,
projectid::varchar project_id
    FROM {{ source('tap_zohosprints', 'backlog') }}

)

select * from source
